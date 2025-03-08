from ..app import app, db
from flask import render_template, request, flash, redirect, url_for, jsonify
from sqlalchemy import or_, func
from ..models.model import Gares, Horaires, Objets_trouves, Declaration_de_perte
from flask import request
from ..models.formulaires import TrouverObjet
from datetime import datetime

@app.route('/trouver_objet/autocomplete', methods=['GET'])
def autocomplete():
    """
    Permet l'auto-completion de la partie 'Gares' du formulaire de recherche 
    """
    query = request.args.get('q', '').lower()
    results = db.session.query(Gares.nom).filter(Gares.nom.ilike(f"%{query}%")).all()
    suggestions = [result.nom for result in results]
    return jsonify(suggestions)

@app.route("/trouver-objet")
def trouver_objet():
    """
    Route qui permet le fonctionnement du formulaire pour trouver la ou les gares 
    les plus probables pour retrouver un objet perdu.
    1. Récupère les entrées utilisateur du formulaire
    2. Soulève un erreur si l'utilisateur rentre plus de deux gares
    4. Renvoie vers le template :
    - geolocalisations : 
    - 
    """
    form = TrouverObjet()
    donnees=[]
    
    if form.validate_on_submit():
        type_d_objet = request.form.get("type_d_objet", None)
        gares = request.form.getlist("gares")  # Liste des gares sélectionnées
        date_trajet = request.form.get("date_trajet", None)
        heure_approx_perte = request.form.get("heure_approx_perte", None)

        # Limiter le nombre de gares à deux maximum
        if len(gares) > 2:
            flash("Veuillez sélectionner au maximum deux gares.", "error")
            return redirect(url_for("trouver_objet"))

         # Combine date_trajet et heure_approx_perte en datetime ISO 8601
        try:
            date_heure_perte = datetime.fromisoformat(f"{date_trajet}T{heure_approx_perte}")
            fin_vacances_noel = datetime.fromisoformat("2025-01-06T23:59:59+01:00")
        except ValueError:
            flash("Format de date ou heure invalide.", "error")
            return redirect(url_for("trouver_objet"))

        # Récupérer les gares correspondantes
        gares_result = Gares.query.filter(
            or_(*[Gares.nom.ilike(f"%{gare.lower()}%") for gare in gares])
        ).all()

        # Géolocalisations des gares sélectionnées
        geolocalisations = [
            {"nom": gare.nom, "latitude": gare.latitude, "longitude": gare.longitude} for gare in gares_result
        ]

        # Filtrer les objets trouvés dans l'intervalle et les gares sélectionnées
        objets_trouves = Objets_trouves.query.filter(
            Objets_trouves.type_objet.ilike(f"%{type_d_objet}%"),
            Objets_trouves.date_heure_trouves >= date_heure_perte,
            Objets_trouves.date_heure_trouves <= fin_vacances_noel,
            Objets_trouves.UIC.in_([gare.UIC for gare in gares_result])
        ).all()

        # Statistiques pour dataviz
        nb_objets_jour = db.session.query(func.count(Objets_trouves.id)).filter(
            func.date(Objets_trouves.date_heure_trouves) == date_trajet,
            Objets_trouves.type_objet.ilike(f"%{type_d_objet}%")
        ).scalar()

        nb_objets_par_type = db.session.query(
            Objets_trouves.type_objet, func.count(Objets_trouves.id)
        ).filter(
            Objets_trouves.UIC.in_([gare.UIC for gare in gares_result]),
            Objets_trouves.date_heure_trouves <= fin_vacances_noel
        ).group_by(Objets_trouves.type_objet).all()

        # Infos pour les gares sélectionnées
        donnees = [
            {
                "nom": gare.nom,
                "adresse": gare.adresse,
                "horaires": [(h.jour_de_la_semaine, h.horaires_jour_normal, h.horaires_jour_ferie) for h in gare.horaires],
                "nb_objets_trouves": len([obj for obj in objets_trouves if obj.UIC == gare.UIC])
            }
            for gare in gares_result
        ]

        return render_template("trouver_objet.html",
                               form=form,
                               geolocalisations=geolocalisations,
                               donnees=donnees,
                               nb_objets_jour=nb_objets_jour,
                               nb_objets_par_type=nb_objets_par_type)

    return render_template("trouver_objet.html", form=form, geolocalisations=[])

    #La route doit renvoyer : 
    #-> Les données de géolocalisations des deux gares max vers le script JS
    #-> Les données de la gare (Nom complet + Adresse complète + horaires d'ouverture et potentiellement //
    # le nb d'objets trouvés du type cherché entre date/heure approx perte et la fin des vacances)
    # -> Données dataviz personnalisées pour script JS : nombre d'objets du même type, perdus et trouvés le même jour partout en France et //
    # nombre do'bjets perdus pour tous les types d'objets dans la gare sélectionnée sur toute la période des vacances.



