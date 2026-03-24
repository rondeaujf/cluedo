from flask import Flask, render_template, request, jsonify
from pycsp3 import *

app = Flask(__name__)

# Données statiques
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
    indices = data.get('indices', []) # Liste d'objets {type: 'negatif/positif', joueur: 0, cartes: []}
    
    clear() # Réinitialise le modèle PyCSP3
    
    n_joueurs = 3 
    proprietaires = ["Moi", "Joueur_1", "Joueur_2", "Enveloppe"]
    env_idx = 3
    
    # Variables
    mat = VarArray(size=[len(toutes_cartes), len(proprietaires)], dom={0, 1})

    # Contraintes structurelles
    for c in range(len(toutes_cartes)):
        satisfy(Sum(mat[c]) == 1)
    
    # L'enveloppe
    satisfy(Sum(mat[i][env_idx] for i in range(len(suspects))) == 1)
    satisfy(Sum(mat[i+6][env_idx] for i in range(len(armes))) == 1)
    satisfy(Sum(mat[i+12][env_idx] for i in range(len(lieux))) == 1)

    # Application des indices reçus de l'interface
    for ind in indices:
        j_idx = ind['joueur']
        c_idxs = [toutes_cartes.index(c_name) for c_name in ind['cartes']]
        
        if ind['type'] == 'possession_directe': # "J'ai cette carte"
            satisfy(mat[c_idxs[0]][j_idx] == 1)
        elif ind['type'] == 'negatif': # "Il n'a aucune de ces 3 cartes"
            for c_idx in c_idxs:
                satisfy(mat[c_idx][j_idx] == 0)
        elif ind['type'] == 'positif': # "Il a au moins une de ces 3"
            satisfy(Sum(mat[c_idx][j_idx] for c_idx in c_idxs) >= 1)
        elif ind['type'] == 'montre_une_carte': 
            # Indice de type "OU" : Le joueur possède au moins l'une de ces cartes
            indices_cartes = []
            for c_nom in ind['cartes']:
                if c_nom in toutes_cartes:
                    indices_cartes.append(toutes_cartes.index(c_nom))
            
            if indices_cartes:
                # Contrainte : Somme des variables (0 ou 1) >= 1
                satisfy(Sum(mat[c_idx][j_idx] for c_idx in indices_cartes) >= 1)

    # Résolution
    if solve() is SAT:
        res = {
            "coupable": suspects[values(mat[0:6, env_idx]).index(1)],
            "arme": armes[values(mat[6:12, env_idx]).index(1)],
            "lieu": lieux[values(mat[12:21, env_idx]).index(1)]
        }
        return jsonify({"status": "found", "solution": res})
    
    return jsonify({"status": "no_solution"})

if __name__ == '__main__':
    app.run(debug=True)
