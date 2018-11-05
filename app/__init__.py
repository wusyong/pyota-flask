from flask import Flask
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_qrcode import QRcode
from app.config import Config
from datetime import timedelta

bcrypt = Bcrypt()
bootstrap = Bootstrap()
qrcode = QRcode()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

    bcrypt.init_app(app)
    bootstrap.init_app(app)
    qrcode.init_app(app)

    from app.main.routes import main
    from app.services.routes import services
    from app.errors.handlers import errors
    app.register_blueprint(main)
    app.register_blueprint(services)
    app.register_blueprint(errors)

    return app
