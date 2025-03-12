from ..app import app, db, login
from werkzeug.security import generate_password_hash
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy import String
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, TextAreaField, PasswordField

class Utilisateur(UserMixin, db.Model):
    __tablename__="utilisateur"
    id_utilisateur=db.Column(db.String(30), primary_key=True)
    pseudo=db.Column(db.String(20), nullable=False)
    password=db.Column(db.Text, nullable=False)
    email=db.Column(db.Text, nullable=False)

    #Relations
    historique=db.relationship("Historique", backref="utilisateur", lazy=True)
    historique=db.relationship("Gares_favorites", backref="utilisateur", lazy=True)

    @staticmethod
    def identification(prenom, password):
        utilisateur = Users.query.filter(Users.prenom == prenom).first()
        if utilisateur and check_password_hash(utilisateur.password, password):
            return utilisateur
        return None

    @staticmethod
    def ajout(prenom, password):
        erreurs = []
        if not prenom:
            erreurs.append("Le prénom est vide")
        if not password or len(password) < 6:
            erreurs.append("Le mot de passe est vide ou trop court")

        unique = Users.query.filter(
            db.or_(Users.prenom == prenom)
        ).count()
        if unique > 0:
            erreurs.append("Le prénom existe déjà")

        if len(erreurs) > 0:
            return False, erreurs
        
        utilisateur = Users(
            prenom=prenom,
            password=generate_password_hash(password)
        )

        try:
            db.session.add(utilisateur)
            db.session.commit()
            return True, utilisateur
        except Exception as erreur:
            return False, [str(erreur)]

    def get_id(self):
        return self.id_utilisateur

    @login.user_loader
    def get_user_by_id(id):
        return Users.query.get(int(id_utilisateur))

#ou à mettre dans un fichier dédié formulaire.py ?
class Connexion(FlaskForm):
    pseudo=StringField("pseudo", validators=[])
    password=PasswordField("pseudo", validators=[])

class AjoutUtilisateur(FlaskForm):
    pseudo = StringField("prenom", validators=[])
    password = PasswordField("password", validators=[])


class Historique(db.Model):
    __tablename__="historique"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_utilisateur=db.Column(db.String(30), ForeignKey('utilisateur.id_utilisateur')) #Foreign Key id_utilisateur de Utilisateurs
    date_heure_recherche=db.Column(db.DateTime)
    requete_json=db.Column(db.Text)

class Gares_favorites(db.Model):
    __tablename__="gares_favorites"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UIC=db.Column(db.Integer, ForeignKey('gares.UIC')) #Foreign Key UIC de Gares
    id_utilisateur=db.Column(db.String(30), ForeignKey('utilisateur.id_utilisateur')) #Foreign Key id_utilisateur de Utilisateurs