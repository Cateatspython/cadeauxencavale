from ..app import app, db
from flask_wtf import FlaskForm
from wtforms import SelectField, FieldList, DateField, TimeField, SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from ..models.gares import Objets_trouves, Gares

class TrouverObjet(FlaskForm):
    """
    Formulaire pour rechercher un objet trouvé dans une gare.
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
    #Formulaire pour pouvoir se connecter -- comprend les messages à afficher en cas d'erreur dans le formulaire
    pseudo=StringField("pseudo", validators=[DataRequired(message="Aucun pseudo n'a été renseigné."), Length(min=3, max=20)])
    email=StringField("email", validators=[DataRequired(message="Aucune adresse email n'a été renseignée."), Email()])
    password=PasswordField("password", validators=[DataRequired(message="Aucun mot de passe n'a été renseigné."), Length(min=6)])

class AjoutUtilisateur(FlaskForm):
    #Formulaire pour pouvoir ajouter un utilisateur -- comprend les messages à afficher en cas d'erreur dans le formulaire
    pseudo = StringField("pseudo", validators=[DataRequired(message="Aucun pseudo n'a été renseigné."), Length(min=3, max=20, message="Le pseudo peut contenir entre 3 et 20 caractères.")])
    password = PasswordField("password", validators=[DataRequired(message="Aucun mot de passe n'a été renseigné."), Length(min=6, message="Le mot de passe doit contenir au moins 6 caractères.")])
    email=StringField("email", validators=[DataRequired(message="Aucune adresse email n'a été renseignée."), Email(message="Veuillez entrer un email valide.")])

class ChangerMdp(FlaskForm):
    #Formulaire pour pouvoir changer de mot de passe -- comprend les messages à afficher en cas d'erreur dans le formulaire
    new_password = PasswordField("password", validators=[DataRequired(message="Aucun mot de passe n'a été renseigné."), Length(min=6, message="Le mot de passe doit contenir au moins 6 caractères.")])
    confirmation_mdp = PasswordField("conf_password", validators=[DataRequired(message="Aucun mot de passe n'a été renseigné."), EqualTo("new_password", message="Les mots de passe ne correspondent pas")])