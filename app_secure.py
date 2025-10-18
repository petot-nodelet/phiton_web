# app_secure.py
import os
from flask import Flask, request, abort, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = os.getenv('DATABASE_URL', f"sqlite:///users.db")
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

app = Flask(__name__)

# Simple token-based protection for demonstration
REQUIRED_TOKEN = os.getenv('ADMIN_TOKEN', '')

def require_token():
    token = request.headers.get('X-ADMIN-TOKEN', '')
    if not REQUIRED_TOKEN or token != REQUIRED_TOKEN:
        abort(403)

@app.route('/')
def secure_index():
    require_token()
    return jsonify({'status': 'secure area'})

@app.route('/list-users')
def list_users():
    require_token()
    try:
        session = SessionLocal()
        rows = session.execute("SELECT id, username, email FROM users LIMIT 500").fetchall()
        users = [{'id': r[0], 'username': r[1], 'email': r[2]} for r in rows]
        return jsonify({'users': users})
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
