from ..app import app, db, login
from flask import render_template, request, flash, redirect, url_for
from sqlalchemy import or_
from ..models.users import Utilisateur, AjoutUtilisateur, Connexion
from flask_login import current_user,logout_user, login_required
from flask_wtf import FlaskForm

@app.route("/accueil")
def accueil():
    return render_template("index.html")

@app.route("/inscription")
def ajout_utilisateur():
    form = AjoutUtilisateur()

    if form.validate_on_submit():
        statut, donnees = Users.ajout(
            prenom=clean_arg(request.form.get("prenom", None)),
            password=clean_arg(request.form.get("password", None))
        )
        if statut is True:
            flash("Ajout effectué", "success")
            return redirect(url_for("accueil"))
        else:
            flash(",".join(donnees), "error")
            return render_template("signup.html", form=form)
    else:
        return render_template("signup.html", form=form)

@app.route("/connexion", methods=["GET","POST"])
def connexion():
    form=Connexion()

    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connecté", "info")
        return redirect(url_for("accueil"))
    
    if form.validate_on_submit():
        utilisateur=Users.identification(
            pseudo=clean_arg(request.form.get("pseudo", None)),
            password=clean_arg(request.form.get("password",None))
        )
        if utilisateur:
            flash("Connexion effectuée","success")
            login_user(utilisateur)
            return redirect(url_for("accueil"))
        else:
            flash("Les identifiants n'ont pas été reconnus.","error")
            return render_template("login.html", form=form)

    else:
        return render_template("login.html", form=form)

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
    return render_template('profil.html')