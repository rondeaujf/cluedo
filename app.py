from flask import Flask, render_template, request, jsonify
from pycsp3 import *
import os

app = Flask(__name__)

# --- DONNÉES DU JEU ---
suspects = ["Rose", "Moutarde", "Pervenche", "Olive", "Leblanc", "Violet"]
armes = ["Poignard", "Chandelier", "Revolver", "Corde", "Matraque", "Cle"]
lieux = ["Cuisine", "GrandSalon", "PetitSalon", "SalleAManger", "Bureau", "Bibliotheque", "Billard", "Hall", "Veranda"]
toutes_cartes = suspects + armes + lieux

@app.route('/')
def index():
    return render_template('index.html', suspects=suspects, armes=armes, lieux=lieux)

@app.route('/solve', methods=['POST'])
def solve_cluedo():
    data = request.json
    indices = data.get('indices', [])
    n_joueurs = int(data.get('n_joueurs', 4))
    seuil = int(data.get('seuil', 5))
    
    # Réinitialisation impérative du modèle PyCSP3 pour chaque requête
    clear()
    
    # Définition des propriétaires : [Moi, Joueur_1, ..., Enveloppe]
    proprietaires = ["Moi"] + [f"Joueur_{i+1}" for i in range(n_joueurs - 1)] + ["Enveloppe"]
    env_idx = len(proprietaires) - 1
    
    # Matrice de variables binaires : mat[carte][propriétaire]
    # mat[c][p] == 1 signifie que le propriétaire p possède la carte c
    mat = VarArray(size=[len(toutes_cartes), len(proprietaires)], dom={0, 1})

    # --- CONTRAINTES STRUCTURELLES ---
    
    # 1. Chaque carte a exactement UN propriétaire
    for c in range(len(toutes_cartes)):
        satisfy(Sum(mat[c]) == 1)
    
    # 2. L'enveloppe contient exactement 1 suspect, 1 arme et 1 lieu
    satisfy(Sum(mat[i][env_idx] for i in range(0, 6)) == 1)       # Suspects
    satisfy(Sum(mat[i][env_idx] for i in range(6, 12)) == 1)      # Armes
    satisfy(Sum(mat[i][env_idx] for i in range(12, 21)) == 1)     # Lieux

    # 3. Répartition des cartes entre les joueurs (hors enveloppe)
    n_cartes_a_distribuer = len(toutes_cartes) - 3
    min_cartes = n_cartes_a_distribuer // n_joueurs
    max_cartes = min_cartes + (1 if n_cartes_a_distribuer % n_joueurs != 0 else 0)
    
    for j in range(n_joueurs):
        # Chaque joueur a entre le min et le max de cartes possibles
        satisfy(Sum(mat[c][j] for c in range(len(toutes_cartes))) >= min_cartes)
        satisfy(Sum(mat[c][j] for c in range(len(toutes_cartes))) <= max_cartes)

    # --- INTEGRATION DES INDICES ---
    
    for ind in indices:
        j_idx = int(ind['joueur'])
        # On ignore l'indice si le joueur n'existe pas dans la config actuelle
        if j_idx >= len(proprietaires):
            continue
            
        c_idxs = [toutes_cartes.index(c) for c in ind['cartes'] if c in toutes_cartes]
        
        if ind['type'] == 'possession_directe':
            # "Je sais que ce joueur possède cette carte précise"
            satisfy(mat[c_idxs[0]][j_idx] == 1)
            
        elif ind['type'] == 'negatif':
            # "Ce joueur n'a AUCUNE de ces cartes" (il a passé son tour)
            for ci in c_idxs:
                satisfy(mat[ci][j_idx] == 0)
                
        elif ind['type'] == 'positif':
            # "Ce joueur possède AU MOINS UNE de ces 3 cartes"
            satisfy(Sum(mat[ci][j_idx] for ci in c_idxs) >= 1)

    # --- RECHERCHE DES SOLUTIONS ---
    
    solutions_enveloppe = []
    # On cherche toutes les solutions (limitées à 50 pour la performance)
    if solve(sols=ALL, limit=50) is SAT:
        for s in solutions():
            # Extraire les noms des cartes dans l'enveloppe pour cette solution
            config = {
                "coupable": suspects[[s[mat][c][env_idx] for c in range(0, 6)].index(1)],
                "arme": armes[[s[mat][c][env_idx] for c in range(6, 12)].index(1)],
                "lieu": lieux[[s[mat][c][env_idx] for c in range(12, 21)].index(1)]
            }
            # On ne garde que les combinaisons d'enveloppe uniques
            if config not in solutions_enveloppe:
                solutions_enveloppe.append(config)

    total_sols = len(solutions_enveloppe)

    if total_sols == 0:
        return jsonify({"status": "no_solution"})

    # On renvoie les hypothèses seulement si elles sont sous le seuil choisi
    return jsonify({
        "status": "success",
        "count": total_sols,
        "hypotheses": solutions_enveloppe if total_sols <= seuil else []
    })

if __name__ == '__main__':
    # Utilisation du port 5000 par défaut
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
