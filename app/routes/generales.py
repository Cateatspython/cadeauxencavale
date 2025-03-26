from ..app import app, db, login
from flask import render_template, request, flash, redirect, url_for, current_app, send_file
from sqlalchemy import or_, desc
from ..models.users import Utilisateur, Historique, Gares_favorites
from ..models.gares import Gares
from ..models.formulaires import AjoutUtilisateur, Connexion, ChangerMdp
from flask_login import current_user,logout_user, login_required, login_user
from flask_wtf import FlaskForm
import json
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF
from ..config import Config
import os
import io

@app.route("/accueil")
def accueil():
    return render_template("/index.html")

#inscription sur l'application 
@app.route("/inscription", methods=['GET', 'POST'])
def ajout_utilisateur():
    form = AjoutUtilisateur()

    if form.validate_on_submit():
        statut, donnees = Utilisateur.ajout(
            pseudo=request.form.get("pseudo", None),
            email=request.form.get("email", None),
            password=request.form.get("password", None)
        )

        if statut is True:
            return redirect(url_for("accueil"))
        else: 
            for erreur in donnees:
                flash(erreur, "error")

    return render_template("pages/inscription.html", form=form)


#connexion + gestion des erreurs lors de la connexion
@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    form = Connexion()

    if current_user.is_authenticated is True:
        return redirect(url_for("accueil"))

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
            flash("Cet email n'est pas reconnu.", "error")
            return render_template("pages/connexion.html", form=form, email=email, pseudo=pseudo, password=password)

        if utilisateur.pseudo != pseudo:
            flash("Ce pseudo n'est pas reconnu.", "error")
            return render_template("pages/connexion.html", form=form, email=email, pseudo=pseudo, password=password)

        if not check_password_hash(utilisateur.password, password):
            flash("Ce mot de passe n'est pas reconnu.", "error")
            return render_template("pages/connexion.html", form=form, email=email, pseudo=pseudo, password=password)

        login_user(utilisateur)
        return redirect(url_for("accueil"))

    return render_template("pages/connexion.html", form=form)

login.login_view='connexion'

#se déconnecter et être redirigé vers la page d'accueil
@app.route("/deconnexion", methods=["POST","GET"])
def deconnexion():
    if current_user.is_authenticated is True:
        logout_user()
    return redirect(url_for("accueil"))

#Connexion obligatoire pour accéder à moncompte, l'historique et les gares favorites
@app.route("/moncompte/")
@login_required
def moncompte():
    #Récupération des informations de l'utilisateur
    utilisateur = Utilisateur.query.filter_by(id=current_user.id).first()

    """
    Récupération des informations sur les favoris, et récupération du nom de la gare pour affichage, au lieu de l'UIC :
        - aller chercher les tables gares_favorites et le nom dans la table gares
        - prendre les gares favorites de l'utilisateur actuel
    """
    favoris = db.session.query(Gares_favorites, Gares.nom)\
                    .join(Gares, Gares_favorites.UIC == Gares.UIC)\
                    .filter(Gares_favorites.utilisateur_id == current_user.id)\
                    .all()

    """
    Récupération de l'historique.
    Pagination des résultats pour l'historique :
        - renvoie au contenu de config.py
        - qui lui-même va chercher la valeur indiquée dans le .env
    """
    per_page = current_app.config["RESOURCES_PER_PAGE"]
    page = request.args.get('page', 1, type=int)

    """
    Récupération de l'historique et déballage du json :
        - création du dictionnaire python vide historique_data
        - pour chaque itération de l'historique, parser le json de la requête en dictionnaire python, puis mettre le json parsé dans le dictionnaire historique_data
        - s'il n'y a pas de requête, retourne un dictionnaire vide
    """
    historique = Historique.query.filter_by(id_utilisateur=current_user.id).order_by(desc(Historique.date_heure_recherche)).paginate(page=page, per_page=per_page, error_out=False)
    historique_data = []
    for h in historique: 
        try:
            requete = json.loads(h.requete_json) if h.requete_json else {} 
        except json.JSONDecodeError:
            requete = {}
        historique_data.append({
            'date_heure_recherche': h.date_heure_recherche,
            'requete': requete
        })

    return render_template('pages/moncompte.html', historique=historique_data, favoris=favoris, utilisateur=utilisateur, pagination=historique)

#Trouver l'image du train
train_image_path = os.path.join(Config.IMG_DIR, 'train.png')

#Création de la classe PDF pour pouvoir exporter les favoris
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 18)
        
        # Ajout de l'image dans le header
        self.image(train_image_path, x=10, y=7, w=15)
        
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
    form = ChangerMdp()

    if form.validate_on_submit():
        current_user.password = generate_password_hash(form.new_password.data)
        db.session.commit()
        
        flash("Votre mot de passe a été changé avec succès !", "success")

        return redirect(url_for("moncompte"))

    return render_template('pages/changemdp.html', form=form)