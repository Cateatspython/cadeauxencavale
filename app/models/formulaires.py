from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField, DateField, TimeField, SubmitField
from wtforms.validators import DataRequired
from your_app.models import Objets_trouves

class TrouverObjet(FlaskForm):
    """
    Formulaire pour rechercher un objet trouvé dans une gare.
    """
    # Champ pour sélectionner le type d'objet dans une liste déroulante
    type_d_objet = SelectField(
        "Type d'objet",
        choices=[],
        validators=[DataRequired(message="Veuillez sélectionner un type d'objet.")]
    )

    # Champ autocomplété pour sélectionner une à deux gares
    gares = SelectMultipleField(
        "Gares",
        choices=[],
        validators=[DataRequired(message="Veuillez sélectionner au moins une gare.")]
    )

    #Champ pour rentrer une date au format normé
    date_trajet = DateField(
        "Date du trajet",
        format="%Y-%m-%d",
        validators=[DataRequired(message="Veuillez renseigner la date du trajet.")]
    )

    #Champ pour rentrer une heure au format normé
    heure_approx_perte = TimeField(
        "Heure approximative de perte",
        format="%H:%M",
        validators=[DataRequired(message="Veuillez renseigner l'heure approximative.")]
    )

    submit = SubmitField("Rechercher")

    #création de la liste des type d'objet pour le dropdown
    def __init__(self, *args, **kwargs):
        super(TrouverObjet, self).__init__(*args, **kwargs)
        # Récupérer les types d'objets uniques depuis la base de données
        self.type_d_objet.choices = [
            (type_objet, type_objet) for type_objet in db.session.query(Objets_trouves.type_objet).distinct().all()
        ]
        #Rajouter un champ vide qui s'affiche par défaut
        self.type_d_objet.choices.insert(0, ("", "Sélectionnez un type d'objet..."))
