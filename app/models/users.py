from ..app import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy import String
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, TextAreaField, PasswordField

class Utilisateur(UserMixin, db.Model):
    __tablename__="utilisateur"
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    pseudo=db.Column(db.String(20), nullable=False)
    password=db.Column(db.Text, nullable=False)
    email=db.Column(db.Text, nullable=False, unique=True)

    #Relations
    historique=db.relationship("Historique", backref="utilisateur", lazy=True)
    gares_favorites=db.relationship("Gares_favorites", backref="utilisateur", lazy=True)

    @staticmethod
    def identification(pseudo, email, password):
        utilisateur = Utilisateur.query.filter(
            db.or_(Utilisateur.pseudo == pseudo, Utilisateur.email == email)
        ).first()
        
        if utilisateur and check_password_hash(utilisateur.password, password):
            return utilisateur
        return None

    @staticmethod
    def ajout(pseudo, email, password):
        erreurs = []
        if not pseudo:
            erreurs.append("Le pseudo est vide")
        if not email:
            erreurs.append("L'email est vide")
        if not password or len(password) < 6:
            erreurs.append("Le mot de passe est vide ou trop court")

        unique = Utilisateur.query.filter(
            db.or_(Utilisateur.pseudo == pseudo, Utilisateur.email == email)
        ).count()
        if unique > 0:
            erreurs.append("Le pseudo ou l'email existe déjà")

        if len(erreurs) > 0:
            print(f"Erreurs rencontrées : {erreurs}")
            return False, erreurs
        utilisateur = Utilisateur(
            pseudo=pseudo,
            email=email,
            password=generate_password_hash(password)
        )

        try:
            db.session.add(utilisateur)
            db.session.commit()
            print("Ajout réussi !")
            return True, utilisateur
        except Exception as erreur:
            return False, [str(erreur)]

    def get_id(self):
        return self.id

    @login.user_loader
    def get_user_by_id(id):
        return Utilisateur.query.get(int(id))


class Historique(db.Model):
    __tablename__="historique"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_utilisateur=db.Column(db.String(30), ForeignKey('utilisateur.id')) #Foreign Key id_utilisateur de Utilisateurs
    date_heure_recherche=db.Column(db.DateTime)
    requete_json=db.Column(db.Text)

    @staticmethod
    def enregistrement_historique(id_utilisateur, date_heure_recherche, requete_json):
        historique = Historique(
            id_utilisateur=id_utilisateur,
            date_heure_recherche=date_heure_recherche,
            requete_json=requete_json
        )

        try:
            db.session.add(historique)
            db.session.commit()
            return True, historique
        except Exception as erreur:
            return False, [str(erreur)]

class Gares_favorites(db.Model):
    __tablename__="gares_favorites"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UIC=db.Column(db.Integer, ForeignKey('gares.UIC')) #Foreign Key UIC de Gares
    id_utilisateur=db.Column(db.String(30), ForeignKey('utilisateur.id')) #Foreign Key id_utilisateur de Utilisateurs

    @staticmethod
    def ajout_favoris(UIC, id_utilisateur):
        gare_favoris = Gares_favorites(
            UIC=UIC,
            id_utilisateur=id_utilisateur
        )

        try:
            db.session.add(gare_favoris)
            db.session.commit()
            return True, gare_favoris
        except Exception as erreur:
            return False, [str(erreur)]
