from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_login import LoginManager

app = Flask(
    'Cadeaux en cavale', 
    template_folder='app/templates',
    static_folder='statics')
app.config.from_object(Config)

db = SQLAlchemy(app)

login = LoginManager(app)

from .routes import trouver_objet, generales, le_saviez_vous
#ne pas oublier d'ajouter les autres .py de /routes lorsque complétés