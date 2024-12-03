# app/routes/recette/mod_recette.py
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
import jwt
import requests
from flasgger import Swagger, swag_from
from flask import Flask, jsonify, request, Blueprint, current_app, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Le hockey recommence'
app.config['SWAGGER'] = {
    'title': 'Gestion de service de retour de Recette',
    'version': '1.1.5'
}
swagger = Swagger(app)


# Vérification du token
def validate_token():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(" ")[1]
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return True, None
        except jwt.ExpiredSignatureError:
            return False, {'message': 'Token expiré'}, 401
        except jwt.InvalidTokenError:
            return False, {'message': 'Token invalide'}, 401
    else:
        return False, {'message': 'Token manquant'}, 401

"""Toutes c'est routes sont seulement pour l'admin"""

"""Routes qui permet de connecter un compte administrateur seulement qui est créer avec la base de donner"""
@app.route('/v1/app/service-api/login', methods=['POST'])
def login():
    """
    Connecter le compte admin seulement et renvoyer un token.
    admin@gmail.com
    admin
    """
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({'Erreur': 'Format de données incorrect. Un objet JSON est requis.'}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'Erreur': 'Aucun Email ou Mot de Passe fourni'}), 400

        # Envoi de la requête pour obtenir les utilisateurs
        api_uri = 'http://localhost:5050/v1/app/get-users'
        headers = {'Content-Type': 'application/json'}
        payload = {'email': email, 'password': password}
        response = requests.post(api_uri, headers=headers, json=payload)

        if response.status_code != 200:
            return jsonify({'Erreur': 'Erreur dans la réponse de service-dao'}), response.status_code

        users_data = response.json()

        # Vérification que `users_data` est bien une liste
        if not isinstance(users_data, list):
            return jsonify({'Erreur': 'Réponse de service-dao inattendue.'}), 500

        # Recherche de l'utilisateur correspondant à l'email fourni
        user_data = next((user for user in users_data if user.get('email') == email), None)
        print(user_data)

        if not user_data:
            return jsonify({'Erreur': 'Utilisateur non trouvé.'}), 404

        # Vérification des informations d'authentification
        if user_data.get('email') != 'admin@gmail.com' or user_data.get('password') != password:
            return jsonify({'Erreur': 'Accès refusé!'}), 403

        # Génération du token si l'authentification réussit
        exp_date = datetime.utcnow() + timedelta(seconds=900)
        token = jwt.encode({'exp': exp_date, 'email': email}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token}), 200

    except Exception as e:
        print(f"Erreur inattendue lors de la connexion : {str(e)}")
        return jsonify({'Erreur': 'Erreur interne du serveur'}), 500


"""Routes qui permet d'obtenir la liste de toutes les recettes"""
@app.route('/v1/app/service-api/recettes', methods=['GET'])
def list_recettes():
    """
    Obtenir la liste de toutes les recettes.
    ---
    responses:
      200:
        description: Liste des recettes récupérée avec succès.
      500:
        description: Erreur interne du serveur.
    """
    try:
        # URI de l'API qui retourne toutes les recettes
        api_uri = 'http://localhost:5050/v1/app/recettes'
        response = requests.get(api_uri)

        # Vérifiez si la requête a réussi
        if response.status_code == 200:
            return jsonify(response.json()), 200  # Retournez la liste des recettes sous forme de JSON

        # Si le statut n'est pas 200, retournez une erreur
        return jsonify({'Erreur': 'Erreur lors de la récupération des recettes.'}), response.status_code

    except requests.exceptions.RequestException as req_e:
        print(f"Erreur de requête: {str(req_e)}")
        return jsonify({'Erreur': 'Erreur lors de la communication avec le service.'}), 500

    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        return jsonify({'Erreur': str(e)}), 500

"""Route qui permet de récupérer une recette seulement avec le id"""
@app.route('/v1/app/service-api/recette/<int:id>', methods=['GET'])
def get_recette_by_id(id):
    # Récupération du token depuis les headers
    #token = request.headers.get('Authorization')
    #valid, error = validate_token(token)

   # if not valid:
   #     return jsonify(error), 401

    # URI de l'API pour obtenir les détails d'une recette spécifique
    api_uri = f'http://localhost:5050/v1/app/recettes/{id}'

    try:
        # Envoyer la requête GET au service externe pour obtenir la recette par ID
        response = requests.get(api_uri)

        if response.status_code == 200:
            # Retourner les détails de la recette
            return jsonify(response.json()), 200
        else:
            # Gérer le cas où la recette n'est pas trouvée ou autre erreur
            return jsonify({'Erreur': 'Erreur dans la réponse de service-dao'}), response.status_code
    except requests.exceptions.RequestException as req_e:
        print(f"Erreur de requête : {str(req_e)}")
        return jsonify({'Erreur': 'Erreur lors de la communication avec le service.'}), 500


"""Routes qui """
@app.route('/v1/app/service-api/recettes', methods=['GET'])

def get_recette(token):
    valid, error = validate_token(token)
    if not valid:
        return jsonify(error), 401

    ingredient = request.args.get('ingredient')
    if not ingredient:
        return jsonify({'Erreur': 'Aucun ingrédient fourni'}), 400

    api_uri = 'http://localhost:5050/v1/app/recettes'
    params = {'ingredient': ingredient}

    response = requests.get(api_uri, params=params)
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({'Erreur': 'Erreur dans la réponse de service-dao'}), response.status_code

"""routes pour ajouter une recette"""
@app.route('/v1/app/service-api/recette', methods=['POST'])
def add_recette():
    data = request.get_json()
    if not data:
        return jsonify({'Erreur': 'Données de recette manquantes'}), 400

    api_uri = 'http://localhost:5050/v1/app/recette'
    response = requests.post(api_uri, json=data)

    if response.status_code == 201:
        return jsonify(response.json()), 201
    else:
        return jsonify({'Erreur': 'Erreur dans la réponse de service-dao'}), response.status_code

"""Routes qui fait la mise a jour de recette"""
@app.route('/v1/app/service-api/recette/<int:id>', methods=['PUT'])

def update_recette(id):
   # token = session.get('admin_token')  # Récupérer le token à partir de la session
    #if not token:
      #  return jsonify({'Erreur': 'Token manquant ou invalide'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'Erreur': 'Données de recette manquantes'}), 400

    api_uri = f'http://localhost:5050/v1/app/recettes/{id}'
    response = requests.put(api_uri, json=data)

    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({'Erreur': 'Erreur dans la réponse de service-dao'}), response.status_code


"""Route pour supprimer une recette"""
@app.route('/v1/app/service-api/recette/<int:id>', methods=['DELETE'])

def delete_recette(id):
    #valid, error = validate_token(token)
    #if not valid:
     #   return jsonify(error), 401

    api_uri = f'http://localhost:5050/v1/app/recettes/{id}'
    response = requests.delete(api_uri)

    if response.status_code == 204:
        return jsonify({'message': 'Recette supprimée avec succès'}), 204
    else:
        return jsonify({'Erreur': 'Erreur dans la réponse de service-dao'}), response.status_code

"""--------------USER---------------------------------------------------"""

"""routes pour obtenir la liste de tout les users"""
@app.route('/v1/app/service-api/users', methods=['GET'])
def get_all_users():
    """
    Obtenir la liste de tous les utilisateurs.
    ---
    responses:
      200:
        description: Liste des utilisateurs récupérée avec succès.
        schema:
          type: array
          items:
            type: object
            properties:
              email:
                type: string
              password:
                type: string
      500:
        description: Erreur interne du serveur.
    """
    try:
        # URI de l'API qui retourne les utilisateurs
        api_uri = 'http://localhost:5050/v1/app/listUsers'
        response = requests.get(api_uri)

        # Vérifiez si la requête a réussi
        if response.status_code == 200:
            users = response.json()  # Obtenez les données des utilisateurs

            # Transformez les utilisateurs en liste de dictionnaires
            user_list = [dict(user) for user in users]
            return jsonify(user_list), 200  # Retournez la liste sous forme de JSON

        # Si le statut n'est pas 200, retournez une erreur
        return jsonify({'Erreur': 'Erreur lors de la récupération des utilisateurs.'}), response.status_code

    except requests.exceptions.RequestException as req_e:
        print(f"Erreur de requête: {str(req_e)}")
        return jsonify({'Erreur': 'Erreur lors de la communication avec le service.'}), 500

    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        return jsonify({'Erreur': str(e)}), 500



"""Routes qui récupere un user par id"""
@app.route('/v1/app/service-api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    Obtenir les informations d'un utilisateur par ID.
    ---
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: ID de l'utilisateur
    responses:
      200:
        description: Informations de l'utilisateur récupérées.
      404:
        description: Utilisateur non trouvé.
      500:
        description: Erreur interne du serveur.
    """
    try:
        api_uri = f'http://localhost:5050/v1/app/users/{user_id}'
        response = requests.get(api_uri)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        elif response.status_code == 404:
            return jsonify({'Erreur': 'Utilisateur non trouvé'}), 404

    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        return jsonify({'Erreur': str(e)}), 500


"""Route pour la mise a jour du user par id"""
@app.route('/v1/app/service-api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Mettre à jour les informations d'un utilisateur.
    ---
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: ID de l'utilisateur
      - name: user_data
        in: body
        required: true
        description: Données à mettre à jour
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Utilisateur mis à jour avec succès.
      400:
        description: Erreur de validation des paramètres.
      500:
        description: Erreur interne du serveur.
    """
    try:
        data = request.get_json()
        api_uri = f'http://localhost:5050/v1/app/users/{user_id}'
        headers = {'Content-Type': 'application/json'}

        response = requests.put(api_uri, headers=headers, json=data)

        if response.status_code == 200:
            return jsonify({'Succès': 'Utilisateur mis à jour avec succès'}), 200
        elif response.status_code == 400:
            return jsonify({'Erreur': 'Paramètres invalides'}), 400

    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        return jsonify({'Erreur': str(e)}), 500

"""route pour supprimer un utilisateur"""
@app.route('/v1/app/service-api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Supprimer un utilisateur.
    ---
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: ID de l'utilisateur
    responses:
      200:
        description: Utilisateur supprimé avec succès.
      404:
        description: Utilisateur non trouvé.
      500:
        description: Erreur interne du serveur.
    """
    try:
        api_uri = f'http://localhost:5050/v1/app/users/{user_id}'
        response = requests.delete(api_uri)

        if response.status_code == 200:
            return jsonify({'Succès': 'Utilisateur supprimé avec succès'}), 200
        elif response.status_code == 404:
            return jsonify({'Erreur': 'Utilisateur non trouvé'}), 404

    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        return jsonify({'Erreur': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5502)
