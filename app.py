from flask import Flask, render_template, request, jsonify
from pycsp3 import *

app = Flask(__name__)

# Configuration du jeu
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
    n_joueurs = int(data.get('n_joueurs', 3))
    
    clear() # Reset PyCSP3
    
    # Propriétaires : [Moi, Joueur_1, ..., Enveloppe]
    proprietaires = ["Moi"] + [f"Joueur_{i+1}" for i in range(n_joueurs - 1)] + ["Enveloppe"]
    env_idx = len(proprietaires) - 1
    
    # Matrice binaire [Carte][Propriétaire]
    mat = VarArray(size=[len(toutes_cartes), len(proprietaires)], dom={0, 1})

    # --- CONTRAINTES ---
    # 1. Chaque carte appartient à exactement une personne (ou l'enveloppe)
    for c in range(len(toutes_cartes)):
        satisfy(Sum(mat[c]) == 1)
    
    # 2. L'enveloppe contient 1 suspect, 1 arme, 1 lieu
    satisfy(Sum(mat[i][env_idx] for i in range(0, 6)) == 1)      # Suspects
    satisfy(Sum(mat[i][env_idx] for i in range(6, 12)) == 1)     # Armes
    satisfy(Sum(mat[i][env_idx] for i in range(12, 21)) == 1)    # Lieux

    # 3. Répartition équitable des cartes (18 cartes / n joueurs)
    n_cartes_joueurs = (len(toutes_cartes) - 3)
    min_cartes = n_cartes_joueurs // n_joueurs
    max_cartes = min_cartes + (1 if n_cartes_joueurs % n_joueurs != 0 else 0)
    
    for j in range(n_joueurs):
        satisfy(Sum(mat[c][j] for c in range(len(toutes_cartes))) >= min_cartes)
        satisfy(Sum(mat[c][j] for c in range(len(toutes_cartes))) <= max_cartes)

    # 4. Application des indices de la partie
    for ind in indices:
        j_idx = int(ind['joueur'])
        if j_idx >= len(proprietaires): continue
        
        c_idxs = [toutes_cartes.index(c) for c in ind['cartes'] if c in toutes_cartes]
        
        if ind['type'] == 'possession_directe':
            satisfy(mat[c_idxs[0]][j_idx] == 1)
        elif ind['type'] == 'negatif':
            for ci in c_idxs: satisfy(mat[ci][j_idx] == 0)
        elif ind['type'] == 'positif':
            # "A montré une carte" = au moins l'une des 3 est chez lui
            satisfy(Sum(mat[ci][j_idx] for ci in c_idxs) >= 1)

    # --- RÉSOLUTION ---
    if solve() is SAT:
        res = {
            "coupable": suspects[values(mat[0:6, env_idx]).index(1)],
            "arme": armes[values(mat[6:12, env_idx]).index(1)],
            "lieu": lieux[values(mat[12:21, env_idx]).index(1)]
        }
        return jsonify({"status": "found", "solution": res})
    
    return jsonify({"status": "no_solution"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
