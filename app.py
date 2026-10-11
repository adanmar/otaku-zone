from flask import Flask, session, request, abort
import secrets
import hmac
import os
from pathlib import Path
from config import Config

from models.db import mysql

from routes.auth import auth_bp
from routes.productos import productos_bp
from routes.carrito import carrito_bp
from routes.checkout import checkout_bp
from routes.admin import admin_bp
from routes.gestion import gestion_bp
from routes.perfil import perfil_bp
from routes.contacto import contacto_bp



app = Flask(__name__)

app.config.from_object(Config)
# Persistent local key, or an explicit secret provided by the deployment environment.
secret_path = Path(app.instance_path) / 'session.key'
secret_path.parent.mkdir(parents=True, exist_ok=True)
if not secret_path.exists():
    try:
        with secret_path.open('x', encoding='utf-8') as key_file:
            key_file.write(secrets.token_hex(32))
    except FileExistsError:
        pass
app.config.update(
    SECRET_KEY=os.environ.get('OTAKU_SECRET_KEY') or secret_path.read_text(encoding='utf-8').strip(),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.environ.get('OTAKU_HTTPS') == '1',
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,
)

mysql.init_app(app)

# BLUEPRINTS
app.register_blueprint(contacto_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(carrito_bp)
app.register_blueprint(checkout_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(gestion_bp)
app.register_blueprint(perfil_bp)


def csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = csrf_token

@app.before_request
def protect_forms():
    if request.method == 'POST':
        expected = session.get('_csrf_token', '')
        supplied = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token', '')
        if not expected or not hmac.compare_digest(expected, supplied):
            abort(400, description='La sesión del formulario venció. Recarga la página e inténtalo de nuevo.')

if __name__ == '__main__':
    app.run(debug=os.environ.get('OTAKU_DEBUG') == '1')
