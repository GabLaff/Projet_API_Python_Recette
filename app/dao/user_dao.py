import sqlite3
from flask import Flask, jsonify, request
from app.model.recette_model import Recette

app = Flask(__name__)

def creer_table():
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
@app.route('/v1/app/get-users', methods=['POST'])
def selectionner_user():
    # Récupérer l'email à rechercher dans les paramètres de requête
    email = request.args.get('email', default='', type=str)
    utilisateurs = []
    requete = 'SELECT email, password FROM User WHERE email LIKE ?'

    try:
        with creer_connexion() as con:
            curseur = con.cursor()
            # Exécuter la requête avec un wildcard pour rechercher des emails partiels
            curseur.execute(requete, ['%' + email + '%'])
            for rec in curseur:
                utilisateurs.append({
                    'email': rec[0],
                    'password': rec[1]
                })

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

    # Retourner la liste des utilisateurs sous forme de JSON
    return jsonify(utilisateurs), 200


@app.route('/v1/app/users', methods=['POST'])
def ajouter_user():
    # Récupérer les données JSON de la requête
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Validation des données
    if not email or not password:
        return jsonify({'error': 'L\'email et le mot de passe sont obligatoires.'}), 400

    # Insertion
    requete = 'INSERT INTO User (email, password) VALUES (?, ?)'
    try:
        with creer_connexion() as con:
            curseur = con.cursor()
            curseur.execute(requete, (email, password))
            con.commit()
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Utilisateur ajouté avec succès!'}), 201

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

def user_exists(id):
    """ Vérifie si un utilisateur existe dans la base de données. """
    requete = 'SELECT id FROM User WHERE id = ?'
    with creer_connexion() as con:
        curseur = con.cursor()
        curseur.execute(requete, (id,))
        return curseur.fetchone() is not None

def creer_connexion():
    return sqlite3.connect('../API_Recette.dbf')

def fermer_connexion(con):
    con.close()

if __name__ == '__main__':
    # Créer la table si elle n'existe pas
    #creer_table()

    # Lancer l'application Flask
    app.run(debug=True, host='0.0.0.0',port=5051)
