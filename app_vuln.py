# app_vuln.py
# "Vulnerable" app converted to use SQLAlchemy safely for learning.
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = os.getenv('DATABASE_URL', f"sqlite:///users.db")
SECRET_CONTENT = os.getenv('SECRET_CONTENT', '')  # produce secret via env var

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=True)
    # add other fields as necessary

# create tables if missing (safe for sqlite/dev)
Base.metadata.create_all(bind=engine)

app = Flask(__name__)

def get_user_by_username(username: str):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.username == username).first()
        return user
    except SQLAlchemyError:
        return None
    finally:
        session.close()

@app.route('/user')
def user_lookup():
    """Return user info by ?username=... (safe parameterized access)"""
    username = request.args.get('username', '')
    if not username:
        return jsonify({'error': 'username parameter required'}), 400
    user = get_user_by_username(username)
    if not user:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email})

@app.route('/secret')
def secret():
    """Return secret if header token matches; secret read from env var SECRET_CONTENT"""
    access_token = request.headers.get('X-ACCESS-TOKEN', '')
    required = os.getenv('ACCESS_TOKEN', '')
    if not required or access_token != required:
        abort(403)
    # Return secret from environment variable
    return SECRET_CONTENT or "No secret configured."

# Keep minimal root for testing
@app.route('/')
def index():
    return "App (root) — user lookup: /user?username=<name>"

if __name__ == '__main__':
    # Local dev: can use python app_vuln.py
    app.run(host='0.0.0.0', port=8000, debug=True)
