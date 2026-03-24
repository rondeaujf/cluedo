# 🕵️‍♂️ Cluedo Smart Solver (PyCSP3 + Flask)

Un assistant de déduction logique pour le jeu de société **Cluedo**, propulsé par la programmation par contraintes (**Constraint Satisfaction Problem**). 

Ce solveur ne se contente pas de "deviner" : il élimine mathématiquement toutes les combinaisons de cartes impossibles en fonction des mains des joueurs et des suggestions faites durant la partie.

## ✨ Fonctionnalités

- **Moteur CSP Puissant** : Utilise la bibliothèque `PyCSP3` pour modéliser les relations entre les cartes, les joueurs et l'enveloppe.
- **Gestion Dynamique** : Supporte de 3 à 6 joueurs.
- **Logique Disjonctive** : Gère les cas complexes où un joueur montre "une carte parmi trois" sans révéler laquelle.
- **Interface Mobile-Friendly** : Interface web épurée avec Bootstrap pour une utilisation rapide sur smartphone pendant une partie.
- **Journal d'Indices** : Historique des faits enregistrés avec option d'annulation (Undo).

## Installer les dépendances

pip install flask pycsp3

## Lancer l'application
python app.py
L'interface sera accessible sur http://127.0.0.1:5000.
