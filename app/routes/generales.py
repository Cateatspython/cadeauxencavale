from ..app import app, db, login
from flask import render_template, request, flash, redirect, url_for, current_app, send_file
from sqlalchemy import or_, desc
from ..models.users import Utilisateur, Historique, Gares_favorites
from ..models.gares import Gares
from ..models.formulaires import AjoutUtilisateur, Connexion, ChangerMdp
from flask_login import current_user,logout_user, login_required, login_user
import json
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF
from ..config import Config
import os
import io
from dotenv import load_dotenv

@app.route("/")
def accueil():
    """
    Affiche la page d'accueil.

    Cette fonction rend le modèle HTML correspondant à la page d'accueil
    de l'application web.

    Returns
    -------
        str: Le contenu HTML de la page d'accueil.
    """
    return render_template("pages/accueil.html")

#inscription sur l'application 
@app.route("/inscription", methods=['GET', 'POST'])
def ajout_utilisateur():
    """
    Gère l'ajout d'un nouvel utilisateur via un formulaire.

    Cette fonction traite les données soumises par un formulaire d'inscription.
    Si les données sont valides, un nouvel utilisateur est ajouté à la base de données.
    En cas de succès, l'utilisateur est redirigé vers la page d'accueil.
    Sinon, les erreurs sont affichées à l'utilisateur.

    Returns
    -------
        - Une redirection vers la page d'accueil si l'ajout est réussi.
        - Le rendu du formulaire d'inscription avec des messages d'erreur en cas d'échec.
    """
    form = AjoutUtilisateur()

    if form.validate_on_submit():
        print("Validation réussie")
        try:
            statut, donnees = Utilisateur.ajout(
                pseudo=request.form.get("pseudo", None),
                email=request.form.get("email", None),
                password=request.form.get("password", None)
            )

            if statut is True:
                utilisateur = Utilisateur.query.filter_by(email=request.form.get("email")).first()

                if utilisateur :
                    login_user(utilisateur)
                    print(current_user.is_authenticated)
                    flash("Inscription réussie, vous êtes maintenant connecté.", "success")
                    return redirect(url_for("moncompte"))

            else: 
                for erreur in donnees:
                    flash(erreur, "danger")

        except Exception as e:
            db.session.rollback()

    return render_template("partials/formulaires/inscription.html", form=form)


#Connexion et gestion des erreurs lors de la connexion
@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    """ Gère la connexion d'un utilisateur.
    Cette fonction vérifie si l'utilisateur est déjà authentifié. Si oui, il est redirigé vers la page "moncompte".
    Sinon, elle traite les données soumises via un formulaire de connexion, effectue des vérifications sur l'email, 
    le pseudo et le mot de passe, et connecte l'utilisateur si les informations sont valides.
    
    Returns
    ------
        - Redirige vers la page "moncompte" si l'utilisateur est déjà connecté ou après une connexion réussie.
        - Affiche le formulaire de connexion avec des messages d'erreur si les informations fournies sont incorrectes.

    Exceptions gérées
    -----------------
        - Email non reconnu.
        - Pseudo non reconnu.
        - Mot de passe incorrect."""
    
    form = Connexion()

    if current_user.is_authenticated is True:
        return redirect(url_for("moncompte"))

    if form.validate_on_submit():
        pseudo = request.form.get("pseudo", None)
        email = request.form.get("email", None)
        password = request.form.get("password", None)
    
        """
        Vérifications et gestion des erreurs par étapes : 
            - vérification de l'email
            - vérification du pseudo
            - vérification du mdp
        quand ce qui a été rentré dans le formulaire ne correspond pas à ce qui est dans la base de données
        """

        utilisateur = Utilisateur.query.filter_by(email=email).first()

        if not utilisateur:
            flash("Cet email n'est pas reconnu.", "danger")
            return render_template("partials/formulaires/connexion.html", form=form, email=email, pseudo=pseudo, password=password)

        if utilisateur.pseudo != pseudo:
            flash("Ce pseudo n'est pas reconnu.", "danger")
            return render_template("partials/formulaires/connexion.html", form=form, email=email, pseudo=pseudo, password=password)

        if not check_password_hash(utilisateur.password, password):
            flash("Ce mot de passe n'est pas reconnu.", "danger")
            return render_template("partials/formulaires/connexion.html", form=form, email=email, pseudo=pseudo, password=password)

        login_user(utilisateur)
        return redirect(url_for("moncompte"))

    return render_template("partials/formulaires/connexion.html", form=form)

login.login_view='connexion'

#se déconnecter et être redirigé vers la page d'accueil
@app.route("/deconnexion", methods=["POST","GET"])
def deconnexion():
    """
    Déconnecte l'utilisateur actuel s'il est authentifié.

    Cette fonction vérifie si l'utilisateur actuel est authentifié. 
    Si c'est le cas, elle effectue la déconnexion de l'utilisateur, 
    affiche un message de confirmation, et redirige vers la page d'accueil.

    Retourne
    -------
        werkzeug.wrappers.Response: Une redirection vers la page d'accueil.
    """
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous avez été déconnecté.", "success")
    return redirect(url_for("accueil"))

#Connexion obligatoire pour accéder à moncompte, l'historique et les gares favorites
@app.route("/moncompte/")
@login_required
def moncompte():
    """Cette fonction permet de récupérer et d'afficher les informations nécessaires
        pour la page "Mon Compte" d'un utilisateur connecté. Elle inclut les informations
        personnelles de l'utilisateur, ses gares favorites, ainsi que son historique
        de recherches paginé.

        Fonctionnalités
        ---------------
        - Récupère les informations de l'utilisateur connecté à partir de la base de données.
        - Récupère les gares favorites de l'utilisateur et leurs noms associés.
        - Récupère l'historique des recherches de l'utilisateur, avec pagination.
        - Décode les données JSON des requêtes de l'historique pour les rendre exploitables.

        Retourne
        -------
            template
                Retourne le template pages/moncompte.html avec les informations suivantes :
                    - `utilisateur` : Les informations de l'utilisateur connecté.
                    - `favoris` : Une liste des gares favorites de l'utilisateur avec leurs noms.
                    - `historique` : Une liste paginée des recherches de l'utilisateur, incluant
                    la date et les détails de chaque recherche.
                    - `pagination` : Les informations de pagination pour l'historique.

        Exceptions gérées
        -----------------
        - Si le JSON des requêtes de l'historique est invalide, il est remplacé par un dictionnaire vide.

        Variables de configuration
        --------------------------
        - `RESOURCES_PER_PAGE` : Nombre d'éléments par page pour la pagination de l'historique.
    """
    # Récupération des informations de l'utilisateur
    utilisateur = Utilisateur.query.filter_by(id=current_user.id).first()

    # Récupération des informations sur les favoris, et récupération du nom de la gare pour affichage
    favoris = db.session.query(Gares_favorites, Gares.nom)\
                    .join(Gares, Gares_favorites.UIC == Gares.UIC)\
                    .filter(Gares_favorites.utilisateur_id == current_user.id)\
                    .all()

    # Pagination des résultats pour l'historique
    per_page = current_app.config["RESOURCES_PER_PAGE"]
    page = request.args.get('page', 1, type=int)

    # Récupération de l'historique et déballage du json
    historique = Historique.query.filter_by(id_utilisateur=current_user.id).order_by(desc(Historique.date_heure_recherche)).paginate(page=page, per_page=per_page, error_out=False)
    historique_data = []
    for h in historique: 
        try:
            # Parser le json de la requête en dictionnaire python
            requete = json.loads(h.requete_json) if h.requete_json else {} 
        except json.JSONDecodeError:
            requete = {}
        historique_data.append({
            'date_heure_recherche': h.date_heure_recherche,
            'requete': requete
        })

    return render_template('pages/moncompte.html', historique=historique_data, favoris=favoris, utilisateur=utilisateur, pagination=historique)

###GESTION DE L'EXPORT DES FAVORIS EN PDF###
#Récupération du logo

#Création de la classe PDF pour pouvoir exporter les favoris
load_dotenv()

class PDF(FPDF):
    def header(self):
        """
        Une classe représentant les PDF à générer lors de l'export des gares favorites.
        Cette classe hérite de FPDF et permet de personnaliser l'en-tête du PDF.
        On indique ici une rapide présentation de la classe.

        Méthodes utilisées
        ------------------
        - set_font : Définit la police de caractères utilisée dans le PDF.
        - image : Ajoute le logo de l'application.
        - set_xy : Définit la position du curseur dans le PDF.
        - cell : Crée une cellule dans le PDF pour y afficher du texte.
        - ln : Ajoute une ligne vide dans le PDF.
        - footer : Définit le pied de page du PDF, incluant le numéro de page.
        """
        self.set_font('Arial', 'B', 18)
        
        # Ajout de l'image dans le header
        chemin_relatif_image = os.getenv('TRAIN_IMAGE_PATH')

        # Transformer le chemin relatif en chemin absolu
        chemin_absolu_image = os.path.join(os.getcwd(), chemin_relatif_image)
        self.image(chemin_absolu_image, x=10, y=7, w=15)
        
        # Positionnement du texte
        self.set_xy(15, 10)
        self.cell(0, 10, 'Cadeaux en cavale', ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# Fonction de génération du PDF
def generate_favoris_pdf(favoris):
    """
    Une fonction permettant la génération de l'export pdf des gares favorites.
    Cette fonction utilise la bibliothèque FPDF et la classe PDF définie ci-dessus.

    Paramètres
    ----------
        favoris : list, obligatoire
            Une liste de tuples contenant les informations sur les gares favorites de l'utilisateur connecté.
            Chaque tuple contient l'instance de Gares_favorites et le nom de la gare.
    
    Retourne
    --------
        pdf_outpout : io.BytesIO
            Un objet BytesIO contenant le contenu du PDF généré.        
    """
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    pdf.cell(10, 10, 'Gares favorites :', ln=True, align='L')
    pdf.ln(2)

    # Ajout les favoris
    for _, nom_gare in favoris:
        pdf.cell(0, 10, f'- {nom_gare}', ln=True)
    
    # Génération du fichier PDF
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output = io.BytesIO(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output

@app.route("/moncompte/export_favoris")
@login_required
def export_favoris():
    """
    Exporte les favoris de l'utilisateur actuel sous forme de fichier PDF.

    Cette fonction effectue les étapes suivantes :
    1. Récupère les informations des gares favorites de l'utilisateur actuel
       en effectuant une jointure entre les tables `Gares_favorites` et `Gares`.
    2. Génère un fichier PDF contenant les informations des favoris.
    3. Retourne le fichier PDF en tant que pièce jointe téléchargeable.

    Retourne
    --------
        send_file
            Envoie le fichier PDF généré en tant que pièce jointe à l'utilisateur.
        pdf_output : io.BytesIO
            Un objet BytesIO contenant le fichier PDF généré, prêt à être téléchargé.
        as_attachment : bool
            Indique que le fichier doit être téléchargé en tant que pièce jointe.
        download_name : str
            Nom du fichier à utiliser lors du téléchargement.
        mimetype : str
            Type MIME du fichier, ici 'application/pdf'.

    Exceptions possibles
    --------------------
        - Si l'utilisateur actuel n'est pas authentifié, une erreur peut être levée.
        - Si une erreur survient lors de la génération ou de l'envoi du fichier PDF.
    """
    # Récupération des informations sur les favoris
    favoris = db.session.query(Gares_favorites, Gares.nom)\
                    .join(Gares, Gares_favorites.UIC == Gares.UIC)\
                    .filter(Gares_favorites.utilisateur_id == current_user.id)\
                    .all()

    # Génération du PDF des favoris
    pdf_output = generate_favoris_pdf(favoris)

    # Au lieu de retourner un template, retourner le pdf
    return send_file(pdf_output, as_attachment=True, download_name='favoris.pdf', mimetype='application/pdf')

#Changement de mot de passe possible quand on est connecté
@app.route("/changer-mot-de-passe", methods=["GET","POST"])
@login_required
def chgnt_mdp():
    """
    Route pour changer le mot de passe de l'utilisateur connecté.
    Cette route permet à un utilisateur authentifié de modifier son mot de passe. 
    Elle gère à la fois les requêtes GET et POST. Lors d'une requête GET, elle affiche 
    le formulaire de changement de mot de passe. Lors d'une requête POST, elle valide 
    les données soumises, met à jour le mot de passe de l'utilisateur dans la base de 
    données et redirige vers la page "mon compte" avec un message de confirmation.

    Retourne
    --------
        render_template
            Affiche le formulaire de changement de mot de passe si la méthode est GET.
        form
            Instance du formulaire de changement de mot de passe.
    """
    form = ChangerMdp()

    try:
        if form.validate_on_submit():
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            
            flash("Votre mot de passe a été changé avec succès !", "success")

            return redirect(url_for("moncompte"))
    except Exception as e:
            db.session.rollback()

    return render_template('partials/formulaires/changemdp.html', form=form)