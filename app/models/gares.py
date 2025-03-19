from ..app import app, db
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash
from sqlalchemy.sql import func

class Gares(db.Model):
    __tablename__="gares"
    UIC=db.Column(db.Integer, primary_key=True)
    nom=db.Column(db.Text)
    latitude=db.Column(db.Float)
    longitude=db.Column(db.Float)
    adresse=db.Column(db.Text)
    commune=db.Column(db.Text)
    code_postal=db.Column(db.Integer)
    moyenne_frequentation_2021_2023=db.Column(db.Integer)
    region=db.Column(db.Text)

    #Relations
    favorites=db.relationship("Gares_favorites", backref="gares", lazy=True)
    horaires=db.relationship("Horaires", backref="gares", lazy=True)
    trouves=db.relationship("Objets_trouves", backref="gares", lazy=True)
    declarations_pertes=db.relationship("Declaration_de_perte", backref="gares", lazy=True)

class Horaires(db.Model):
    __tablename__="horaires"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UIC=db.Column(db.Integer, ForeignKey('gares.UIC')) #Foreign Key UIC de Gares
    jour_de_la_semaine=db.Column(db.String(10))
    horaires_jour_normal=db.Column(db.String(30))
    horaires_jour_ferie=db.Column(db.String(30))

class Objets_trouves(db.Model):
    __tablename__="objets_trouves"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UIC=db.Column(db.Integer, ForeignKey('gares.UIC')) #Foreign Key UIC de Gares
    date_perte=db.Column(db.DateTime)
    date_restitution=db.Column(db.DateTime)
    type_objet=db.Column(db.Text)
    nature_objet=db.Column(db.Text)

class Declaration_de_perte(db.Model):
    __tablename__="declaration_perte"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UIC=db.Column(db.Integer, ForeignKey('gares.UIC')) #Foreign Key UIC de Gares
    date_perte=db.Column(db.DateTime)
    type_objet=db.Column(db.Text) #normalisation du pluriel