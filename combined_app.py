# combined_app.py
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Request, Response

# import apps
import app_vuln as vuln_mod
import app_secure as secure_mod

# vuln_mod.app and secure_mod.app are Flask WSGI apps
vuln_app = vuln_mod.app
secure_app = secure_mod.app

# mount secure app under /secure (so /secure/* forwarded)
application = DispatcherMiddleware(vuln_app, {
    '/secure': secure_app
})

# ready for gunicorn: `gunicorn combined_app:application`
