from ..app import app, db
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func

class Gares(db.Model):
    """
    Une classe pour représenter la table gares de la base de données.

    Attributs
    ---------
    UIC : sqlalchemy.sql.schema.Column
        Identifiant unique de la gare (clé primaire).
    nom : sqlalchemy.sql.schema.Column
        Nom de la gare.
    latitude : sqlalchemy.sql.schema.Column
        Latitude de la gare.
    longitude : sqlalchemy.sql.schema.Column
        Longitude de la gare.
    adresse : sqlalchemy.sql.schema.Column
        Adresse de la gare.
    commune : sqlalchemy.sql.schema.Column
        Commune où se situe la gare.
    code_postal : sqlalchemy.sql.schema.Column
        Code postal de la gare.
    moyenne_frequentation_2021_2023 : sqlalchemy.sql.schema.Column
        Moyenne de fréquentation de la gare.
    region : sqlalchemy.sql.schema.Column
        Région où se situe la gare.

    favorites : sqlalchemy.orm.relationship
        Relation avec la table Gares_favorites.
    horaires : sqlalchemy.orm.relationship
        Relation avec la table Horaires.
    trouves : sqlalchemy.orm.relationship
        Relation avec la table Objets_trouves.
    declarations_pertes : sqlalchemy.orm.relationship
        Relation avec la table Declaration_de_perte.
    """
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
    """
    Une classe qui représente la table horaires de la base de données.

    Attributs
    ---------
    id : sqlalchemy.sql.schema.Column
        Identifiant unique de l'horaire (clé primaire).
    UIC : sqlalchemy.sql.schema.Column
        Identifiant unique de la gare (clé étrangère).
    jour : sqlalchemy.sql.schema.Column
        Jour de la semaine.
    horaire_jour_normal : sqlalchemy.sql.schema.Column
        Horaire pour un jour normal.
    horaire_jour_ferie : sqlalchemy.sql.schema.Column
        Horaire pour un jour férié.
    """
    __tablename__="horaires"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UIC=db.Column(db.Integer, ForeignKey('gares.UIC')) #Foreign Key UIC de Gares
    jour=db.Column(db.String(10))
    horaire_jour_normal=db.Column(db.String(30))
    horaire_jour_ferie=db.Column(db.String(30))

class Objets_trouves(db.Model):
    """
    Une classe qui représente la table objets_trouves de la base de données.

    Attributs
    ---------
    id : sqlalchemy.sql.schema.Column
        Identifiant unique de l'objet trouvé (clé primaire).
    UIC : sqlalchemy.sql.schema.Column
        Identifiant unique de la gare (clé étrangère).
    date_perte : sqlalchemy.sql.schema.Column
        Date de la perte de l'objet.
    date_restitution : sqlalchemy.sql.schema.Column
        Date de la restitution de l'objet.
    type_objet : sqlalchemy.sql.schema.Column
        Type de l'objet trouvé.
    nature_objet : sqlalchemy.sql.schema.Column
        Nature de l'objet trouvé.
    """
    __tablename__="objets_trouves"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UIC=db.Column(db.Integer, ForeignKey('gares.UIC')) #Foreign Key UIC de Gares
    date_perte=db.Column(db.DateTime)
    date_restitution=db.Column(db.DateTime)
    type_objet=db.Column(db.Text)
    nature_objet=db.Column(db.Text)

class Declaration_de_perte(db.Model):
    """
    Une classe qui représente la table declarations_de_perte de la base de données.

    Attributs
    ---------
    id : sqlalchemy.sql.schema.Column
        Identifiant unique de la déclaration de perte (clé primaire).
    UIC : sqlalchemy.sql.schema.Column
        Identifiant unique de la gare (clé étrangère).
    date_perte : sqlalchemy.sql.schema.Column
        Date de la perte de l'objet.
    type_objet : sqlalchemy.sql.schema.Column
        Type de l'objet perdu.
    """
    __tablename__="declarations_de_perte"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UIC=db.Column(db.Integer, ForeignKey('gares.UIC')) #Foreign Key UIC de Gares
    date_perte=db.Column(db.DateTime)
    type_objet=db.Column(db.Text) #normalisation du pluriel