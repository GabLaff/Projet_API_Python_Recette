from datetime import datetime, timedelta
import jwt
import requests
from flasgger import Swagger
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Le hockey recommence'
app.config['SWAGGER'] = {
    'title': 'Gestion de service de retour de Recette',
    'version': '1.1.5'
}

# Initialiser Swagger
swagger = Swagger(app)



"""Routes qui permet a l'utilisateur d'entrer un ingrédient puis se fait retourne une liste de recette"""
@app.route('/v1/app/service-api/<string:token>', methods=['GET'])
#@swag_from('recette.yml')
def get_recette(token):
    """
    Récupérer les recettes par ingrédient.
  ---
parameters:
  - name: ingredient
    in: query
    type: string
    required: true
    description: L'ingrédient à rechercher.
  - name: token
    in: path
    type: string
    required: true
    description: Le token d'authentification.
responses:
  200:
    description: Liste des recettes correspondantes.
  400:
    description: Erreur de validation des paramètres.
  500:
    description: Erreur interne du serveur.

    """
    try:
        # Valider le token
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expiré'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token invalide'}), 401

    try:
        # Récupérer les ingrédients depuis les paramètres GET (pas JSON)
        ingredient = request.args.get('ingredient')

        if not ingredient:
            return jsonify({'Erreur': 'Aucun ingrédient fourni'}), 400

        # Créer la demande pour l'API service_dao get ingrédients
        api_uri = 'http://localhost:5050/v1/app/recettes_by_ingredient'
        params = {'ingredient': ingredient}

        # Envoyer la requête GET à l'API service_dao
        response = requests.get(api_uri, params=params)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'Erreur': 'Erreur dans la réponse de service-dao'}), response.status_code

    except Exception as e:
        return jsonify({'Erreur': 'Dans la requête pour accéder au dao', 'details': str(e)}), 500

"""route qui Récupère toute les recettes"""
@app.route('/v1/app/service-api/recettes/<string:token>', methods=['GET'])
def get_all_recettes(token):
    """
    Récupérer toutes les recettes.
   ---
parameters:
  - name: token
    in: path
    type: string
    required: true
    description: Le token d'authentification.
responses:
  200:
    description: Liste de toutes les recettes disponibles.
  500:
    description: Erreur interne du serveur.

    """
    try:
        # Valider le token
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expiré'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token invalide'}), 401

    try:
        # Créer la demande pour l'API service_dao pour récupérer toutes les recettes
        api_uri = 'http://localhost:5050/v1/app/recettes'

        # Envoyer la requête GET à l'API service_dao pour obtenir toutes les recettes
        response = requests.get(api_uri)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'Erreur': 'Erreur dans la réponse de service-dao'}), response.status_code

    except Exception as e:
        return jsonify({'Erreur': 'Erreur lors de la récupération des recettes', 'details': str(e)}), 500



"""Routes pour enregistrer un nouvel utilisateur"""
@app.route('/v1/app/service-api/register', methods=['POST'])
def register():
    """
    Enregistrer un nouvel utilisateur et renvoyer un message de succès.
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        print(f"Données reçues: {data}")

        if not email or not password:
            return jsonify({'Erreur': 'Aucun Email ou Mot de Passe fourni'}), 400

        api_uri_register = 'http://localhost:5050/v1/app/users'
        payload_register = {'email': email, 'password': password}
        headers = {'Content-Type': 'application/json'}

        # Envoyer la requête POST à l'API service_dao
        response = requests.post(api_uri_register, json=payload_register, headers=headers)
        print(f"Réponse de l'API service_dao : {response.status_code} - {response.text}")

        if response.status_code == 201:
            return jsonify({'Succès': 'Compte ajouté'}), 201
        else:
            return jsonify({'Erreur': "Échec de l'enregistrement de l'utilisateur", 'Détails': response.text}), response.status_code

    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        return jsonify({'Erreur': str(e)}), 500

"""Routes pour la connection d'un utilisateur et retourne un token"""
@app.route('/v1/app/service-api/login', methods=['POST'])
def login():
    """
    Connecter un utilisateur et renvoyer un token.
    ---
    parameters:
      - name: email
        in: body
        required: true
        description: L'email de l'utilisateur
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Token généré.
        schema:
          type: object
          properties:
            token:
              type: string
      400:
        description: Erreur de validation des paramètres.
      500:
        description: Erreur interne du serveur.
    """
    try:
        # Obtenir les données du corps de la requête
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'Erreur': 'Aucun Email ou Mot de Passe fourni'}), 400

        # Créer la demande pour l'API service_dao pour vérifier l'utilisateur
        api_uri = 'http://localhost:5050/v1/app/get-users'


        headers = {'Content-Type': 'application/json'}
        payload = {'email': email, 'password': password}

        # Envoyer la requête POST à l'API service_dao
        response = requests.post(api_uri, headers=headers, json=payload)

        # Vérifier la réponse de service_dao
        if response.status_code != 200:
            print(f"Réponse brute de service_dao: {response.text}")
            return jsonify({'Erreur': "L'email n'existe pas"}), response.status_code

        # Si la réponse est OK (200), générer le token
        exp_date = datetime.utcnow() + timedelta(seconds=900)
        token = jwt.encode({'exp': exp_date, 'email': email}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token}), 200

    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        return jsonify({'Erreur': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5500)
