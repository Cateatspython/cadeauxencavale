from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_login import LoginManager

app = Flask(
    __name__, 
    template_folder='templates',
    static_folder='statics')
app.config.from_object(Config)

db = SQLAlchemy(app)

login = LoginManager(app)

from .routes import trouver_objet
#ne pas oublier d'ajouter les autres .py de /routes lorsque complétés