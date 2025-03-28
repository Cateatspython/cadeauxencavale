from ..app import app, db
from flask import render_template
from sqlalchemy import func
from ..models.gares import Gares, Objets_trouves

@app.route("/le-saviez-vous", methods=["GET", "POST"])
def le_saviez_vous():
    """
Route pour la page "Le Saviez-Vous".
Cette route gère les requêtes GET et POST pour afficher des statistiques sur les objets perdus et retrouvés dans les gares.
Requêtes effectuées :
1. Calcul du pourcentage et du taux d'objets perdus par gare.
2. Calcul du délai moyen de restitution des objets perdus par type et nature d'objet.
3. Calcul du nombre d'objets perdus par mois et par région.
Retourne :
    Un rendu du template "le_saviez_vous.html" avec les données suivantes :
    - donnees_heatmap : Liste de dictionnaires contenant le nom, la latitude, la longitude et le pourcentage d'objets perdus par gare.
    - donnees_diff_perte_restitution : Liste de dictionnaires contenant le type d'objet, la nature d'objet et le délai moyen de restitution en jours.
    - donnees_perte_par_mois_region : Liste de dictionnaires contenant l'année, le mois, le type d'objet, la région et le nombre d'objets perdus.
"""
# Requete pour récupérer le taux d'objet perdus par gare/frequentation pour 1000 personnes
    requete_heatmap = (
    db.session.query(
            Gares.nom,
            Gares.latitude,
            Gares.longitude,
            (func.count(Objets_trouves.date_perte) / 3.0 / func.nullif(Gares.moyenne_frequentation_2021_2023, 0) * 1000)
            .label("taux_objets_perdus")
        )
        .join(Objets_trouves, Gares.UIC == Objets_trouves.UIC)
        .group_by(Gares.nom, Gares.latitude, Gares.longitude, Gares.moyenne_frequentation_2021_2023)
        .all()
    )
    donnees_heatmap = [
        {
            "nom": gare.nom,
            "latitude": gare.latitude,
            "longitude": gare.longitude,
            "pourcentage_objets_perdus": gare.taux_objets_perdus,
        }
        for gare in requete_heatmap
    ]

#requete pour récupérer le délai moyen de restitution des objets perdus par type et nature d'objet
    requete_diff_perte_restiution = (
    db.session.query(
        Objets_trouves.type_objet,
        Objets_trouves.nature_objet,
        func.avg(func.julianday(Objets_trouves.date_restitution) - func.julianday(Objets_trouves.date_perte)).label("delai_moyen_jours")
    )
    .filter(Objets_trouves.date_restitution.isnot(None))  # Exclure les objets non encore restitués
    .group_by(Objets_trouves.type_objet, Objets_trouves.nature_objet)
    .all()
    )
    donnees_diff_perte_restitution = [
        {
            "type_objet": objet.type_objet,
            "nature_objet": objet.nature_objet,
            "delai_moyen_jours": objet.delai_moyen_jours,
        }
        for objet in requete_diff_perte_restiution
    ]
    
    #requete pour récupérer le nombre d'objets perdus par mois, par région et par nature/type d'objet
    requete_perte_par_mois = (
        db.session.query(
            func.extract('month', Objets_trouves.date_perte).label("mois"),
            Objets_trouves.type_objet,
            func.count(Objets_trouves.date_perte).label("nombre_perdus")
        )
        .filter(
            func.extract('year', Objets_trouves.date_perte).between(2021, 2024)
        )
        .group_by("mois", Objets_trouves.type_objet)
        .order_by("mois")
        .all()
    )

# Convertir les résultats de la requête en un dictionnaire de moyennes
    donnees_perte_mois = {}
    for resultat in requete_perte_par_mois :
        mois = f'{resultat.mois:02d}'
        type_objet = resultat.type_objet
        
        if mois not in donnees_perte_mois :
            donnees_perte_mois[mois] = {}
        
        donnees_perte_mois[mois][type_objet] = resultat.nombre_perdus

    return render_template("pages/le_saviez_vous.html", donnees_heatmap=donnees_heatmap, donnees_diff_perte_restitution=donnees_diff_perte_restitution, donnees_perte_mois=donnees_perte_mois)