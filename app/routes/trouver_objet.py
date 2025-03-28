from ..app import app, db
from flask import render_template, request, flash, redirect, url_for, jsonify
from sqlalchemy import or_, func
from ..models.gares import Gares, Horaires, Objets_trouves, Declaration_de_perte
from ..models.users import Historique, Gares_favorites
from flask_login import current_user
from ..models.formulaires import TrouverObjet
from datetime import datetime
import json

@app.route("/autocomplete-gares", methods=["GET"])
def autocomplete_gares():
    """
    Renvoie les noms des gares pour l'autocomplétion, filtrés selon la saisie de l'utilisateur.

    Retourne
    --------
        gares_noms : list
            Liste des noms de gares correspondant à la saisie de l'utilisateur.
    """
    query = request.args.get("query", "").lower()
    gares = Gares.query.filter(Gares.nom.ilike(f"%{query}%")).with_entities(Gares.nom).all()
    gares_noms = [gare.nom for gare in gares]
    return jsonify(gares_noms)

@app.route("/trouver-objet", methods=["GET", "POST"])
def trouver_objet():
    """
    Route pour rechercher des objets trouvés dans les gares et afficher des statistiques.

    Cette route permet aux utilisateurs de renseigner un formulaire pour rechercher des objets perdus.
    Les résultats sont filtrés selon les critères suivants :
    - Type d'objet recherché
    - Liste des gares sélectionnées (maximum 2)
    - Date du trajet
    - Heure approximative de perte

    Fonctionnalités
    ---------------
    1. Validation du formulaire :
       - Tous les champs doivent être remplis
       - Limitation à 2 gares maximum
       - Vérification du format des dates et heures (ISO 8601)
       - Vérification de la date de perte entre le 20 décembre 2024 et le 6 janvier 2025
    
    2. Requêtes SQLAlchemy :
       - Récupération des gares correspondant aux critères
       - Filtrage des objets trouvés entre la date/heure approximative de perte et la fin des vacances de Noël
       - Comptage des objets trouvés le jour donné et par type d'objet
       
    3. Données renvoyées au template :
       - Informations sur chaque gare (nom, adresse, horaires, nombre d'objets trouvés)
       - Statistiques pour la datavisualisation :
         - Nombre total d'objets trouvés le jour sélectionné
         - Répartition des objets trouvés par type dans les gares sélectionnées
         - Nombre d'objets perdus, trouvés et restitués par région le jour sélectionné

    Retourne
    --------
        Render_template vers "trouver_objet.html" avec les données nécessaires pour l'affichage :
        - form : instance du formulaire TrouverObjet
            Le formulaire validé ou vide
        - donnees : list
            Détails des gares (nom, adresse, horaires, etc.)
        - data_par_region : list
            Statistiques des objets perdus, trouvés et restitués par région
        - data_objets_par_types_gares : list
            Nombre d'objets trouvés par type dans les gares sélectionnées
        - type_d_objet : str
            Type d'objet recherché
        - date_trajet : str
            Date du trajet sélectionnée

    Exceptions gérées
    -----------------
        - Un champ du formulaire est vide
        - Plus de 2 gares sont sélectionnées
        - Les formats de date/heure sont invalides
        - La date de perte n'est pas entre le 20 décembre 2024 et le 6 janvier 2025
    """
    form = TrouverObjet()
    donnees = []
    data_par_region = []
    data_objets_par_types_gares = []
    type_d_objet = []
    date_trajet = []
    
    if form.validate_on_submit():
        type_d_objet = request.form.get("type_d_objet", None)
        gares = request.form.get("gares")  # Liste des gares sélectionnées
        date_trajet = request.form.get("date_trajet", None)
        heure_approx_perte = request.form.get("heure_approx_perte", None)
        
        # Soulever une erreur si les champs sont vides
        if not (type_d_objet and gares and date_trajet and heure_approx_perte) or gares == []:
            flash("Veuillez renseigner tous les champs du formulaire", "error")
            return redirect(url_for("trouver_objet"))

        print(f'Gares sélectionnées : {gares}')
        # Convertir la liste des gares en liste d'objets
        gares = gares.split(",")

        print(f'Gares sélectionnées : {gares}')
        # Limiter le nombre de gares à deux maximum
        if len(gares) > 2 :
            flash("Veuillez sélectionner au maximum deux gares.", "error")
            print("Trop de gares sélectionnées")
            return redirect(url_for("trouver_objet"))

        # Combine date_trajet et heure_approx_perte en datetime ISO 8601
        fin_vacances_noel = datetime.fromisoformat("2025-01-06T23:59:59+01:00")
        debut_vacances_noel = datetime.fromisoformat("2024-12-20T00:00:00+01:00")
        try:
            date_heure_perte = datetime.fromisoformat(f"{date_trajet}T{heure_approx_perte}:00+01:00")
        except ValueError:
            flash("Format de date ou heure invalide.", "error")
            return redirect(url_for("trouver_objet"))

        # Vérifier si la date de perte est entre la date de début et la date de fin des vacances de Noël
        if not (debut_vacances_noel <= date_heure_perte <= fin_vacances_noel):
            flash("La date de perte doit être entre le 20 décembre 2024 et le 6 janvier 2025.", "error")
            return redirect(url_for("trouver_objet"))

        #Message de validation du formulaire si aucun problème n'est rencontré
        flash("Formulaire validé !", "success")

        ### RECUPERATION DES DONNEES ###

        # Récupérer les gares correspondantes
        gares_result = Gares.query.filter(
            or_(*[Gares.nom.ilike(f"%{gare.lower()}%") for gare in gares])
        ).all()

        # Filtrer les objets trouvés par :
        # - le type sélectionné
        # - dans l'intervalle datetime perte / datetime fin des vacances
        # - les gares sélectionnées
        objets_trouves = Objets_trouves.query.filter(
            Objets_trouves.type_objet.ilike(f"%{type_d_objet}%"),
            Objets_trouves.date_perte >= date_heure_perte,
            Objets_trouves.date_perte <= fin_vacances_noel,
            Objets_trouves.UIC.in_([gare.UIC for gare in gares_result])
        ).all()

        # Horaires des gares sélectionnées
        horaires = Horaires.query.filter(Horaires.UIC.in_([gare.UIC for gare in gares_result])).all()

        ### RECUPERATION DES DONNEES POUR LES DATAVISUALISATIONS PERSONNALISEES ###
        
        # 1. Tous les objets perdus, objets_trouvés.date_perte, objets_trouvés.date_restitution en France par Région, du type sélectionné, pendant toute la journée de perte.
        datetime_debut_journee_perte = datetime.fromisoformat(f"{date_trajet}T00:00:00")
        datetime_fin_journee_perte = datetime.fromisoformat(f"{date_trajet}T23:59:59")

        # Queries pour récupérer le nombre d'objets perdus par région
        nb_objets_perdus_par_region = db.session.query(
            Gares.region, func.count(Declaration_de_perte.id)
        ).join(Gares, Declaration_de_perte.UIC == Gares.UIC).filter(
            Declaration_de_perte.date_perte >= datetime_debut_journee_perte,
            Declaration_de_perte.date_perte <= datetime_fin_journee_perte,
            Declaration_de_perte.type_objet.ilike(f"%{type_d_objet}%")
        ).group_by(Gares.region).all()
        # Queries pour récupérer le nombre d'objets trouvés par région
        nb_objets_trouves_par_region = db.session.query(
            Gares.region, func.count(Objets_trouves.date_perte)
        ).join(Gares, Objets_trouves.UIC == Gares.UIC).filter(
            Objets_trouves.date_perte >= datetime_debut_journee_perte,
            Objets_trouves.date_perte <= datetime_fin_journee_perte,
            Objets_trouves.type_objet.ilike(f"%{type_d_objet}%")
        ).group_by(Gares.region).all()
        # Queries pour récupérer le nombre d'objets restitués par région
        nb_objets_restitues_par_region = db.session.query(
            Gares.region, func.count(Objets_trouves.date_restitution)
        ).join(Gares, Objets_trouves.UIC == Gares.UIC).filter(
            Objets_trouves.date_restitution >= datetime_debut_journee_perte,
            Objets_trouves.date_restitution <= datetime_fin_journee_perte,
            Objets_trouves.type_objet.ilike(f"%{type_d_objet}%")
        ).group_by(Gares.region).all()

        # Convertir les résultats des requêtes en dictionnaires pour un accès rapide
        perdus_par_region = dict(nb_objets_perdus_par_region)
        trouves_par_region = dict(nb_objets_trouves_par_region)
        restitues_par_region = dict(nb_objets_restitues_par_region)

        # Récupérer toutes les régions uniques
        regions = set(perdus_par_region.keys()) | set(trouves_par_region.keys()) | set(restitues_par_region.keys())

        # Construire le dictionnaire final
        data_par_region = [
            {
                "region": region,
                "nb_objets_perdus": perdus_par_region.get(region, 0),
                "nb_objets_trouves": trouves_par_region.get(region, 0),
                "nb_objets_restitues": restitues_par_region.get(region, 0)
            }
            for region in regions
        ]
        # #2. Nombre d'objets trouvés par types dans les gares sélectionnées, pendant la période des vacances de Noël
        nb_objets_par_type_par_gare = db.session.query(
            Objets_trouves.UIC, Objets_trouves.type_objet, func.count(Objets_trouves.id)
        ).filter(
            Objets_trouves.date_perte >= date_heure_perte,
            Objets_trouves.date_perte <= fin_vacances_noel,
            Objets_trouves.UIC.in_([gare.UIC for gare in gares_result])
        ).group_by(Objets_trouves.UIC, Objets_trouves.type_objet).all()

        data_objets_par_types_gares = [
            {
                "gare": gare.nom,
                "type_objet": type_objet,
                "nb_objets_trouves": nb
            }
            for UIC, type_objet, nb in nb_objets_par_type_par_gare
            for gare in gares_result if gare.UIC == UIC
        ]
        print(data_objets_par_types_gares)


        # Infos pour les gares sélectionnées (liste de dictionnaires)
        donnees = [
            {
            # nom de la gare (str)
            "nom": gare.nom,
            # adresse complète de la gare (str)
            "adresse": f'{gare.adresse}, {gare.code_postal} {gare.commune}.' if gare.adresse else f'{gare.code_postal} {gare.commune}.',
            # géolocalisation de la gare (dict)
            "geolocalisation": {
                "latitude": gare.latitude,
                "longitude": gare.longitude
            },
            # horaires d'ouverture de la gare sous forme de dictionnaire imbriqué (dict)
            "horaires": {
                h.jour: {
                "horaires_jour_normal": h.horaire_jour_normal,
                "horaires_jour_ferie": h.horaire_jour_ferie
                }
                for h in horaires if h.UIC == gare.UIC
            },
            "UIC": gare.UIC,
            # nombre d'objets trouvés du type cherché entre date/heure approx perte et la fin des vacances pour la gare itérée (int)
            "nb_objets_trouves_periode_perte_type": len([obj for obj in objets_trouves if obj.UIC == gare.UIC])
            }
            for gare in gares_result
        ]

        # Enregistrement de l'historique de recherche automatique si utilisateur connecté
        if current_user.is_authenticated:
            filtres_requetes = json.dumps({
                "type_d_objet": type_d_objet,
                "gares": gares,
                "date_trajet": date_trajet,
                "heure_approx_perte": heure_approx_perte
            })
            Historique.enregistrement_historique(
                id_utilisateur=current_user.get_id(),
                date_heure_recherche=datetime.now(),
                requete_json=filtres_requetes
               )
            flash("Recherche enregistrée dans l'historique", "info")
        
        # Ajout de la gare aux favoris si utilisateur connecté et activation du bouton "Ajouter aux favoris"
    
    return render_template("pages/trouver_objet.html",
                           form=form,
                           donnees=donnees,
                           data_par_region=data_par_region,
                           data_objets_par_types_gares=data_objets_par_types_gares,
                           type_d_objet=type_d_objet,
                           date_trajet=date_trajet
                           )


@app.route("/ajouter-favori", methods=["POST"])
def ajouter_favori():
    """
    Une route permettant de gérer l'ajout d'une gare aux favoris de l'utilisateur connecté.
    Cette route est appelée par une requête AJAX lorsque l'utilisateur clique sur le bouton "Ajouter aux favoris".
    Elle vérifie si l'utilisateur est connecté et si la gare n'est pas déjà dans ses favoris.
    Si la gare est déjà dans les favoris, un message d'information est affiché.
    Sinon, la gare est ajoutée aux favoris et un message de succès est affiché.

    Retourne
    --------
        JSON
            Un message de succès ou d'erreur selon le résultat de l'opération.
    """
    if not request.is_json:
        flash("Requête invalide, veuillez utiliser JSON", "error")
        return jsonify({"status": "error", "message": "Requête invalide, veuillez utiliser JSON"})
    
    data = request.get_json()
    UIC = data.get("UIC")
    
    if not UIC:
        flash("UIC manquant", "error")
        return jsonify({"status": "error", "message": "UIC manquant"})
    
    if current_user.is_authenticated:
        favori_existant = Gares_favorites.query.filter_by(utilisateur_id=current_user.id, UIC=UIC).first()
        
        if favori_existant:
            flash("Cette gare est déjà dans vos favoris", "info")
            return jsonify({"status": "exists", "message": "Cette gare est déjà dans vos favoris"})
        else:
            Gares_favorites.ajout_favoris(utilisateur_id=current_user.id, UIC=UIC)
            db.session.commit()
            flash("Gare ajoutée aux favoris avec succès", "success")
            return jsonify({"status": "success", "message": "Gare ajoutée aux favoris avec succès"})
    else:
        flash("Utilisateur non connecté", "error")
        return jsonify({"status": "error", "message": "Utilisateur non connecté"})