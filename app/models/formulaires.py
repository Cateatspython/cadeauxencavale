from ..app import app, db
from flask_wtf import FlaskForm
from wtforms import SelectField, FieldList, DateField, TimeField, SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from ..models.gares import Objets_trouves

class TrouverObjet(FlaskForm):
    """
    Une classe héritant de FlaskForm pour créer un formulaire de recherche d'objets trouvés dans les gares.

    Attributs
    ---------
    type_d_objet : SelectField
        Champ pour sélectionner le type d'objet dans une liste déroulante.
    gares : FieldList
        Champ autocomplété pour sélectionner une à deux gares.
    date_trajet : DateField
        Champ pour rentrer une date au format normé.
    heure_approx_perte : TimeField
        Champ pour rentrer une heure au format normé.
    submit : SubmitField
        Champ pour soumettre le formulaire.

    Méthodes
    --------
    __init__(self, *args, **kwargs)
        Constructeur de la classe. Initialise le champ type_d_objet avec les types d'objets uniques depuis la base de données.
    """
    # Champ pour sélectionner le type d'objet dans une liste déroulante
    type_d_objet = SelectField(
        "Type d'objet",
        choices=[],
        # validators=[DataRequired(message="Veuillez sélectionner un type d'objet.")]
    )

    # Champ autocomplété pour sélectionner une à deux gares
    gares = FieldList(StringField("Gares"), min_entries=1, max_entries=2) #validators=[DataRequired()])

    # Champ pour rentrer une date au format normé
    date_trajet = DateField(
        "Date du trajet",
        format="%Y-%m-%d",
        #validators=[DataRequired(message="Veuillez renseigner la date du trajet.")]
    )

    # Champ pour rentrer une heure au format normé
    heure_approx_perte = TimeField(
        "Heure approximative de perte",
        format="%H:%M",
        #validators=[DataRequired(message="Veuillez renseigner l'heure approximative.")]
    )

    submit = SubmitField("Rechercher")

    # création de la liste des type d'objet pour le dropdown
    def __init__(self, *args, **kwargs):
        super(TrouverObjet, self).__init__(*args, **kwargs)
        # Récupérer les types d'objets uniques depuis la base de données
        self.type_d_objet.choices = [
            (type_objet[0], type_objet[0]) for type_objet in db.session.query(Objets_trouves.type_objet).distinct().all()
        ]
        # Rajouter un champ vide qui s'affiche par défaut
        self.type_d_objet.choices.insert(0, ("", "Sélectionnez un type d'objet..."))
        

class Connexion(FlaskForm):
    """
    Une classe héritant de FlaskForm pour créer un formulaire de connexion pour les utilisateurs déjà inscrit.

    Attributs 
    ---------
    pseudo : Stringfield
        Champ pour soumettre le pseudo de l'utilisateur.
    email : Stringfield
        Champ pour soumettre l'email de l'utilisateur.
    password : PasswordField
        Champ pour soumettre le mot de passe de l'utilisateur.

    Exceptions
    ----------
    - Si le pseudo, l'email ou le mot de passe n'a pas été renseigné
    - Si le pseudo fait moins de trois lettres ou s'il en contient plus de vingt
    - Si le mot de passe contient moins de 6 caractères
    """
    pseudo=StringField("pseudo", validators=[DataRequired(message="Aucun pseudo n'a été renseigné."), Length(min=3, max=20, message="Le pseudo doit contenir entre 3 et 20 caractères.")])
    email=StringField("email", validators=[DataRequired(message="Aucune adresse email n'a été renseignée."), Email()])
    password=PasswordField("password", validators=[DataRequired(message="Aucun mot de passe n'a été renseigné."), Length(min=6, message="Le mot de passe doit contenir au moins 6 caractères.")])

class AjoutUtilisateur(FlaskForm):
    """
    Une classe héritant de FlaskForm pour créer un formulaire d'inscription pour les utilisateurs qui ne se sont pas encore inscrit.

    Attributs 
    ---------
    pseudo : Stringfield
        Champ pour soumettre le pseudo de l'utilisateur.
    email : Stringfield
        Champ pour soumettre l'email de l'utilisateur.
    password : PasswordField
        Champ pour soumettre le mot de passe de l'utilisateur.
    
        Exceptions
    ----------
    - Si le pseudo, l'email ou le mot de passe n'a pas été renseigné
    - Si le pseudo fait moins de trois lettres ou s'il en contient plus de vingt
    - Si le mot de passe contient moins de 6 caractères
    """
    pseudo = StringField("pseudo", validators=[DataRequired(message="Aucun pseudo n'a été renseigné."), Length(min=3, max=20, message="Le pseudo doit contenir entre 3 et 20 caractères.")])
    password = PasswordField("password", validators=[DataRequired(message="Aucun mot de passe n'a été renseigné."), Length(min=6, message="Le mot de passe doit contenir au moins 6 caractères.")])
    email=StringField("email", validators=[DataRequired(message="Aucune adresse email n'a été renseignée."), Email(message="Veuillez entrer une adresse email valide.")])

class ChangerMdp(FlaskForm):
    """
    Une classe héritant de FlaskForm pour créer un formulaire de changement de mot de passe pour les utilisateurs qui se sont déjà inscrits. 

    Attributs 
    ---------
    new_password : PasswordField
        Champ pour soumettre le nouveau mot de passe de l'utilisateur.
    confirmation_mdp : PasswordField
        Champ pour soumettre la confirmation du nouveau mot de passe de l'utilisateur.
    
    Exceptions
    ----------
    - Si le new_password ou le confirmation_mdp ne sont pas renseignés.
    - Si le new_password contient moins de six caractères
    - Si le confirmation_mdp n'est pas identique au new_password
    """
    new_password = PasswordField("password", validators=[DataRequired(message="Aucun mot de passe n'a été renseigné."), Length(min=6, message="Le mot de passe doit contenir au moins 6 caractères.")])
    confirmation_mdp = PasswordField("conf_password", validators=[DataRequired(message="Aucun mot de passe n'a été renseigné."), EqualTo("new_password", message="Les mots de passe ne correspondent pas")])