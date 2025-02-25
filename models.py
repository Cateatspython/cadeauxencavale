from ..app import app, db

class Utilisateur(db.Model):
    __tablename__="utilisateur"
    id_utilisateur=db.Column(db.String(30), primary_key=True)
    pseudo=db.Column(db.String(20))
    password=db.Column(db.String(20))
    email=db.Column(db.Text)

    #Relations
    historique=db.relationship("Historique", backref="utilisateur", lazy=True)
    historique=db.relationship("Gares_favorites", backref="utilisateur", lazy=True)


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

class Gares(db.Model):
    __tablename__="gares"
    UIC=db.Column(db.Integer, primary_key=True)
    nom=db.Column(db.Text)
    position_geographique=db.Column(db.Text)
    adresse=db.Column(db.Text)
    ville=db.Column(db.Text)
    code_postal=db.Column(db.Integer)

    #Relations
    favorites=db.relationship("Gares_favorites", backref="gares", lazy=True)
    horaires=db.relationship("Horaires", backref="gares", lazy=True)
    frequentation=db.relationship("Frequentation_gare", backref="gares", lazy=True)
    trouves=db.relationship("Objets_trouves", backref="gares", lazy=True)
    declarations_pertes=db.relationship("Declaration_de_perte", backref="gares", lazy=True)

class Horaires(db.Model):
    __tablename__="horaires"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UIC=db.Column(db.Integer, ForeignKey('gares.UIC')) #Foreign Key UIC de Gares
    jour_de_la_semaine=db.Column(db.String(10))
    horaires_jour_normal=db.Column(db.String(30))
    horaires_jour_ferie=db.Column(db.String(30))

class Frequentation_gare(db.Model):
    __tablename__="frequentation_gare"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UIC=db.Column(db.Integer, ForeignKey('gares.UIC')) #Foreign Key UIC de Gares
    total_voyageurs_2023=db.Column(db.String(30))

class Objets_trouves(db.Model):
    __tablename__="objets_trouves"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UIC=db.Column(db.Integer, ForeignKey('gares.UIC')) #Foreign Key UIC de Gares
    date_heure_trouves=db.Column(db.DateTime)
    type_objet=db.Column(db.Text)
    date_heure_restitution=db.Column(db.DateTime)

class Declaration_de_perte(db.Model):
    __tablename__="declaration_perte"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UIC=db.Column(db.Integer, ForeignKey('gares.UIC')) #Foreign Key UIC de Gares
    date_perte=db.Column(db.DateTime)
    type_objet=db.Column(db.Text) #normalisation du pluriel
    nature_objet=db.Column(db.Text) #normalisation du pluriel


