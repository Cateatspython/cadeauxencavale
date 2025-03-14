from ..app import app, db, login
from flask import render_template, request, flash, redirect, url_for
from sqlalchemy import or_
from ..models.users import Utilisateur, Historique, Gares_favorites
from ..models.formulaires import AjoutUtilisateur, Connexion, ChangerMdp
from flask_login import current_user,logout_user, login_required, login_user
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash

@app.route("/accueil")
def accueil():
    return render_template("index.html")

@app.route("/inscription", methods=['GET','POST'])
def ajout_utilisateur():
    form = AjoutUtilisateur()

    if form.validate_on_submit():
        statut, donnees = Utilisateur.ajout(
            pseudo=request.form.get("pseudo", None),
            email=request.form.get("email", None),
            password=request.form.get("password", None)
        )
        if statut is True:
            flash("Ajout effectué", "success")
            return redirect(url_for("accueil"))
        else:
            flash(",".join(donnees), "error")
            return render_template("pages/inscription.html", form=form)
    else:
        return render_template("pages/inscription.html", form=form)

@app.route("/connexion", methods=["GET","POST"])
def connexion():
    form=Connexion()

    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connecté", "info")
        return redirect(url_for("accueil"))

    if form.validate_on_submit():
        print("✅ Formulaire validé !")
    else:
        print("❌ Erreurs dans le formulaire :", form.errors)
    
    if form.validate_on_submit():
        print("✅ Formulaire validé !")

        pseudo = request.form.get("pseudo", None)
        email = request.form.get("email", None)
        password = request.form.get("password", None)

        print(f"📩 Données reçues : pseudo={pseudo}, email={email}, password={password}")

        utilisateur = Utilisateur.identification(pseudo=pseudo, email=email, password=password)

        print(f"🔍 Utilisateur trouvé : {utilisateur}")

        if utilisateur:
            login_user(utilisateur)
            print(f"👤 Utilisateur connecté : {current_user}")
            flash("Connexion effectuée", "success")
            print("✅ Redirection vers l'accueil")
            return redirect(url_for("accueil"))

        else:
            flash("Les identifiants n'ont pas été reconnus.","error")
            return render_template("pages/connexion.html", form=form)

    else:
        print("❌ Erreurs dans le formulaire :", form.errors)
    
    return render_template("pages/connexion.html", form=form)

login.login_view='connexion'

@app.route("/deconnexion", methods=["POST","GET"])
def deconnexion():
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté.","info")
    return redirect(url_for("accueil"))

#connexion obligatoire pour accéder à moncompte, l'historique et les gares favorites
@app.route("/moncompte")
@login_required
def moncompte():
    historique = Historique.query.filter_by(id=current_user.id).order_by(Historique.date_heure_recherche.desc()).all()
    
    favoris = Gares_favorites.query.filter_by(id=current_user.id).all()

    utilisateur = Utilisateur.query.all()

    return render_template('pages/moncompte.html', historique=historique, favoris=favoris, utilisateur=utilisateur)

@app.route("/changer-mot-de-passe", methods=["GET","POST"])
@login_required
def chgnt_mdp():
    form = ChangerMdp()

    if form.validate_on_submit():
        current_user.password = generate_password_hash(form.new_password.data)
        db.session.commit()
        
        flash("Votre mot de passe a été changé avec succès !", "success")
        return redirect(url_for("moncompte"))

    return render_template('changemdp.html', form=form)