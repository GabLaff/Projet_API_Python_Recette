import sqlite3
from http.client import responses
from flask import Flask, jsonify, request
from model.recette_model import Recette
import os
app = Flask(__name__)

def creer_connexion():
    return sqlite3.connect('API_Recette.dbf')

print(os.path.abspath('API_Recette.dbf'))


def fermer_connexion(con):
    con.close()
"""Table user"""
def creer_table_user():
    cde_ddl = '''CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        password TEXT
    )'''
    con = creer_connexion()
    curseur = con.cursor()
    curseur.execute(cde_ddl)
    con.commit()
    fermer_connexion(con)

"""Table Recette"""
def create_table_recette():
    cde_ddl = '''CREATE TABLE IF NOT EXISTS Recette (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        ingredient TEXT)'''

    with creer_connexion() as con:
        curseur = con.cursor()
        curseur.execute(cde_ddl)
        con.commit()

"""routes dao qui execute une requete qui select une recette par un ingredient"""
@app.route('/v1/app/recettes_by_ingredient', methods=['GET'])
def selectionner_data_by_ingredient():
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


"""routes dao qui execute une requete récupération d'une liste"""
@app.route('/v1/app/recettes', methods=['GET'])
def selectionner_data():
    """
    Obtenir toutes les recettes.
    ---
    responses:
      200:
        description: Liste des recettes récupérées avec succès.
      500:
        description: Erreur interne du serveur.
    """
    registre = []

    # Requête SQL pour récupérer toutes les recettes
    requete = 'SELECT id, nom, ingredient FROM Recette'

    try:
        with creer_connexion() as con:
            curseur = con.cursor()
            curseur.execute(requete)  # Exécuter la requête pour toutes les recettes
            for rec in curseur:
                #registre.append(Recette(rec[0],rec[1], rec[2]))
                registre.append({
                    'id': rec[0],
                    'Nom': rec[1],
                    'Ingredient': rec[2]
                })

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

    #return jsonify([{'id': rec.id,'nom': rec.nom, 'ingredient': rec.ingredient} for rec in registre])
    return jsonify(registre)

"""
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

"""

"""routes dao qui execute une requete insert """
@app.route('/v1/app/recette', methods=['POST'])
def ajouter_recette():
    data = request.get_json()
    nom = data.get('nom')
    ingredient = data.get('ingredient')

    # Vérifier si les éléments requis sont présents
    if not nom or not ingredient:
        return jsonify({'error': 'Éléments manquants'}), 400

    requete = 'INSERT INTO Recette (nom, ingredient) VALUES (?, ?)'
    try:
        with creer_connexion() as con:
            curseur = con.cursor()
            curseur.execute(requete, (nom, ingredient))
            con.commit()
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Recette ajoutée avec succès.'}), 201






"""routes dao qui execute une requete select by id"""
@app.route('/v1/app/recettes/<int:id>', methods=['GET'])
def selectionner_data_by_id(id):
    """
    Obtenir une recette par son identifiant.
    ---
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: L'identifiant de la recette à récupérer.
    responses:
      200:
        description: Recette récupérée avec succès.
        schema:
          type: object
          properties:
            id:
              type: integer
            nom:
              type: string
            ingredient:
              type: string
      404:
        description: Recette non trouvée.
      500:
        description: Erreur interne du serveur.
    """
    requete = 'SELECT id, nom, ingredient FROM Recette WHERE id = ?'

    try:
        with creer_connexion() as con:
            curseur = con.cursor()
            curseur.execute(requete, (id,))
            rec = curseur.fetchone()

            if rec:
                # Si la recette est trouvée, la retourner en JSON
                recette = {
                    'id': rec[0],
                    'nom': rec[1],
                    'ingredient': rec[2]
                }
                return jsonify(recette), 200
            else:
                # Si aucune recette n'est trouvée avec cet ID
                return jsonify({'error': 'Recette non trouvée'}), 404

    except sqlite3.Error as e:
        return jsonify({'ERREUR': 'TU est dans recetteDao'+str(e)}), 500

"""routes dao qui execute une requete de mise a jour"""
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

"""routes dao qui execute une requete delete"""
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




"""--------------USER---------------USER------------------------------------------------"""

@app.route('/v1/app/get-users', methods=['POST'])
def selectionner_user():
    # Récupérer l'email à rechercher depuis le corps de la requête JSON
    data = request.get_json()  # Attendre un JSON dans le corps de la requête
    email = data.get('email', '')

    if not email:
        return jsonify({'ERREUR': "L'email est requis"}), 400

    if not user_exists_email(email):
        return jsonify({'ERREUR': 'Utilisateur non trouvé.'}), 404

    utilisateurs = []

    requete = 'SELECT email, password FROM User WHERE email LIKE ?'

    try:
        with creer_connexion() as con:
            curseur = con.cursor()
            # Exécuter la requête avec un wildcard pour rechercher des emails partiels
            curseur.execute(requete, ('%' + email + '%',))
            for rec in curseur:
                utilisateurs.append({
                    'email': rec[0],
                    'password': rec[1]
                })

    except Exception as e:
        print(f"Erreur inattendue lors de la connexion : {str(e)}")
        return jsonify({'Erreur': 'Erreur interne du serveur'}), 500

    # Retourner la liste des utilisateurs sous forme de JSON
    return jsonify(utilisateurs), 200
@app.route('/v1/app/users', methods=['POST'])
def ajouter_user():
    # Récupérer les données JSON de la requête
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    print(f"Données reçues: {data}")

    # Validation des données
    if not email or not password:
        return jsonify({'error': 'Email et le mot de passe sont obligatoires.'}), 400


    # Insertion
    requete = 'INSERT INTO User (email, password) VALUES (?, ?)'
    try:
        with creer_connexion() as con:
            curseur = con.cursor()
            curseur.execute(requete, (email, password))
            con.commit()
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Utilisateur ajouter avec succes!'}), 201

@app.route('/v1/app/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Validation des données
    if not email or not password:
        return jsonify({'error': 'L\'email et le mot de passe sont obligatoires.'}), 400

    # Vérifier si l'utilisateur existe
    if not user_exists(id):
        return jsonify({'error': 'Utilisateur non trouvé.'}), 404

    requete = 'UPDATE User SET email = ?, password = ? WHERE id = ?;'
    try:
        with creer_connexion() as con:
            curseur = con.cursor()
            curseur.execute(requete, (email, password, id))
            con.commit()
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Utilisateur mis à jour.'}), 200

@app.route('/v1/app/users/<int:id>', methods=['DELETE'])
def supprimer_user(id):
    # Vérifier si l'utilisateur existe
    if not user_exists(id):
        return jsonify({'error': 'Utilisateur non trouvé.'}), 404

    requete = 'DELETE FROM User WHERE id = ?'

    try:
        with creer_connexion() as con:
            curseur = con.cursor()
            curseur.execute(requete, (id,))
            con.commit()
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Utilisateur supprimé avec succès!'}), 200

@app.route('/v1/app/listUsers', methods=['GET'])
def get_all_users():
    """
    Récupérer tous les utilisateurs de la base de données.
    :return: Liste d'utilisateurs sous forme de dictionnaires.
    """
    utilisateurs = []
    requete = 'SELECT id, email FROM User'

    try:
        with creer_connexion() as con:
            curseur = con.cursor()
            curseur.execute(requete)
            for rec in curseur:
                utilisateurs.append({
                    'id': rec[0],
                    'email': rec[1]
                })
    except sqlite3.Error as e:
        return jsonify({'error': f"Erreur lors de la récupération des utilisateurs: {str(e)}"}), 500

    # Retourner la liste des utilisateurs sous forme de JSON
    return jsonify(utilisateurs), 200



def user_exists(id):
    """ Vérifie si un utilisateur existe dans la base de données. """
    requete = 'SELECT id FROM User WHERE id = ?'
    with creer_connexion() as con:
        curseur = con.cursor()
        curseur.execute(requete, (id,))
        return curseur.fetchone() is not None

def user_exists_email(email):
    """Vérifie si un utilisateur existe dans la base de données."""
    requete = 'SELECT email FROM User WHERE email = ?'
    try:
        with creer_connexion() as con:
            curseur = con.cursor()
            curseur.execute(requete, (email,))
            return curseur.fetchone() is not None
    except Exception as e:
        # Gérer l'exception, si nécessaire
        print(f"Erreur lors de la vérification de l'utilisateur: {str(e)}")
        return False



if __name__ == '__main__':
    create_table_recette()
    creer_table_user()

    # Lancer l'application Flask
    app.run(debug=True, host='0.0.0.0',port=5050)
