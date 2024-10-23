import sqlite3
from flask import Flask, jsonify, request
from app.model.recette_model import Recette

app = Flask(__name__)

def creer_connexion():
    return sqlite3.connect('../API_Recette.dbf')

def fermer_connexion(con):
    con.close()

def create_table_recette():
    cde_ddl = '''CREATE TABLE IF NOT EXISTS Recette (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        ingredient TEXT)'''

    with creer_connexion() as con:
        curseur = con.cursor()
        curseur.execute(cde_ddl)
        con.commit()

@app.route('/v1/app/recettes', methods=['GET'])
def selectionner_data():
    ingredient = request.args.get('ingredient')
    registre = []
    requete = 'SELECT id, nom, ingredient FROM Recette WHERE ingredient LIKE ?'

    try:
        with creer_connexion() as con:
            curseur = con.cursor()
            curseur.execute(requete, ['%' + ingredient + '%'])
            for rec in curseur:
                registre.append(Recette(rec[1], rec[2]))

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

    return jsonify([{'Nom': rec.nom, 'Ingredient': rec.ingredient} for rec in registre])

@app.route('/v1/app/recettes', methods=['POST'])
def ajouter_recette():
    data = request.get_json()
    nom = data.get('nom')
    ingredient = data.get('ingredient')

    if not nom or not ingredient:
        return jsonify({'error': 'Le nom et l\'ingrédient sont obligatoires.'}), 400

    requete = 'INSERT INTO Recette (nom, ingredient) VALUES (?, ?)'
    try:
        with creer_connexion() as con:
            curseur = con.cursor()
            curseur.execute(requete, (nom, ingredient))
            con.commit()
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Recette ajoutée avec succès!'}), 201

@app.route('/v1/app/recettes/<int:id>', methods=['PUT'])
def update_recette(id):
    data = request.get_json()
    nom = data.get('nom')
    ingredient = data.get('ingredient')

    if not nom or not ingredient:
        return jsonify({'error': 'Le nom et l\'ingrédient sont obligatoires.'}), 400

    requete = 'UPDATE Recette SET nom = ?, ingredient = ? WHERE id = ?;'
    try:
        with creer_connexion() as con:
            curseur = con.cursor()
            curseur.execute(requete, [nom, ingredient, id])
            con.commit()
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Recette mise à jour.'}), 200

@app.route('/v1/app/recettes/<int:id>', methods=['DELETE'])
def supprimer_recette(id):
    requete = 'DELETE FROM Recette WHERE id = ?'
    try:
        with creer_connexion() as con:
            curseur = con.cursor()
            curseur.execute(requete, (id,))
            con.commit()
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Recette supprimée avec succès!'}), 200

if __name__ == '__main__':
    # Créer la table si elle n'existe pas
    #create_table_recette()
    # Lancer l'application Flask
    app.run(debug=True, host='0.0.0.0',port=5050)
