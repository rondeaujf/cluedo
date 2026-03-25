# 🕵️‍♂️ Cluedo Smart Solver (PyCSP3 + Flask)

Un assistant de déduction logique pour le jeu de société **Cluedo**, propulsé par la programmation par contraintes (**Constraint Satisfaction Problem**). 

Ce solveur ne se contente pas de "deviner" : il élimine mathématiquement toutes les combinaisons de cartes impossibles en fonction des mains des joueurs et des suggestions faites durant la partie.

## ✨ Fonctionnalités

- **Moteur CSP Puissant** : Utilise la bibliothèque `PyCSP3` pour modéliser les relations entre les cartes, les joueurs et l'enveloppe.
- **Gestion Dynamique** : Supporte de 3 à 6 joueurs.
- **Logique Disjonctive** : Gère les cas complexes où un joueur montre "une carte parmi trois" sans révéler laquelle.
- **Interface Mobile-Friendly** : Interface web épurée avec Bootstrap pour une utilisation rapide sur smartphone pendant une partie.
- **Journal d'Indices** : Historique des faits enregistrés avec option d'annulation (Undo).

### 📊 Analyse d'incertitude
L'outil permet aussi de quantifier votre progression :
- **Compteur de probabilités** : Affiche combien de combinaisons "Suspect/Arme/Lieu" restent possibles.
- **Mode Hypothèses** : Si le nombre de solutions tombe sous un seuil (ex: 3), l'outil liste explicitement les suspects restants pour vous aider à orienter vos prochaines questions.

## Installer les dépendances

pip install flask pycsp3

## Lancer l'application
python app.py
L'interface sera accessible sur http://127.0.0.1:5000.

## 🛠 Comment ça marche ?
Le problème est modélisé sous forme de matrice binaire $M_{c,p}$ :

- $c \in \{0 \dots 20\}$ (les 21 cartes du jeu)
- $p \in \{0 \dots n\}$ (les joueurs + l'enveloppe)

Le solveur impose que :

1. Chaque carte a un propriétaire unique : $\sum_{p} M_{c,p} = 1$
2. L'enveloppe contient exactement 1 Suspect, 1 Arme et 1 Lieu.
3. Chaque joueur possède un nombre de cartes cohérent avec la distribution initiale.
 
Lorsqu'un joueur montre une carte pour une suggestion (Suspect S, Arme A, Lieu L), on ajoute la contrainte :

$M_{S,p} + M_{A,p} + M_{L,p} \geq 1$.

## 📜 LicenceMIT - Amusez-vous bien (et gagnez toutes vos parties) !
