from ..app import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import ForeignKey


class Utilisateur(UserMixin, db.Model):
    """
    Une classe représentant les utilisateurs de l'application.
    Elle hérite de la classe UserMixin de Flask-Login pour gérer l'authentification.

    Attributs
    ---------
    id : sqlalchemy.sql.schema.Column
        L'identifiant unique de l'utilisateur.
    pseudo : sqlalchemy.sql.schema.Column
        Le pseudo de l'utilisateur.
    password : sqlalchemy.sql.schema.Column
        Le mot de passe de l'utilisateur (stocké sous forme hachée).
    email : sqlalchemy.sql.schema.Column
        L'adresse email de l'utilisateur (doit être unique).
    historique : sqlalchemy.orm.relationship
        La relation entre l'utilisateur et son historique de recherches.
    gares_favorites : sqlalchemy.orm.relationship
        La relation entre l'utilisateur et ses gares favorites.

    Méthodes
    --------
    identification(pseudo, email, password)
        Vérifie si les informations d'identification fournies sont valides.
    ajout(pseudo, email, password)
        Ajoute un nouvel utilisateur à la base de données.
    get_id()
        Retourne l'identifiant de l'utilisateur actuel.
    get_user_by_id(id)
        Retourne un utilisateur à partir de son identifiant.
    """
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

    #Méthode pour ajouter un utilisateur et erreurs soulevées quand des données existent déjà dans la base de données
    @staticmethod
    def ajout(pseudo, email, password):
        erreurs = []

        unique_pseud = Utilisateur.query.filter(
            db.or_(Utilisateur.pseudo == pseudo)
        ).count()
        if unique_pseud > 0:
            erreurs.append("Le pseudo existe déjà")
        
        unique_mail = Utilisateur.query.filter(
            db.or_(Utilisateur.email == email)
        ).count()
        if unique_mail > 0:
            erreurs.append("Cette adresse email a déjà été utilisée")

        if len(erreurs) > 0:
            print(f"Erreur.s rencontrée.s : {erreurs}")
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
    """
    Une classe qui représente la table historique de la base de données.

    Attributs
    ---------
    id : sqlalchemy.sql.schema.Column
        L'identifiant unique de l'historique.
    id_utilisateur : sqlalchemy.sql.schema.Column
        L'identifiant de l'utilisateur associé à cet historique (clé étrangère).
    date_heure_recherche : sqlalchemy.sql.schema.Column
        La date et l'heure de la recherche effectuée.
    requete_json : sqlalchemy.sql.schema.Column
        La requête JSON associée à cette recherche.
    
    Méthodes
    --------
    enregistrement_historique(id_utilisateur, date_heure_recherche, requete_json)
        Enregistre un nouvel historique dans la base de données.
    """
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
    """
    Une classe qui représente la table gares_favorites de la base de données.

    Attributs
    ---------
    id : sqlalchemy.sql.schema.Column
        L'identifiant unique de la gare favorite.
    UIC : sqlalchemy.sql.schema.Column
        Le code UIC de la gare favorite (clé étrangère vers la table gares).
    utilisateur_id : sqlalchemy.sql.schema.Column
        L'identifiant de l'utilisateur associé à cette gare favorite (clé étrangère vers la table utilisateur).
    
    Méthodes
    --------
    ajout_favoris(UIC, utilisateur_id)
        Ajoute une gare aux favoris de l'utilisateur.
    """
    __tablename__="gares_favorites"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UIC=db.Column(db.Integer, ForeignKey('gares.UIC')) #Foreign Key UIC de Gares
    utilisateur_id=db.Column(db.String(30), ForeignKey('utilisateur.id')) #Foreign Key id_utilisateur de Utilisateurs

    @staticmethod
    def ajout_favoris(UIC, utilisateur_id):
        gare_favoris = Gares_favorites(
            UIC=UIC,
            utilisateur_id=utilisateur_id
        )

        try:
            db.session.add(gare_favoris)
            db.session.commit()
            return True, gare_favoris
        except Exception as erreur:
            return False, [str(erreur)]
