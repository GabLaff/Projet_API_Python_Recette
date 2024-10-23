from datetime import datetime, timedelta
import jwt
import requests
from flasgger import Swagger
from flask import Flask,request, jsonify

from datetime import datetime, timedelta
import jwt
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Le hockey recommence'
app.config['SWAGGER'] = {
    'title': 'Gestion de service de retour de Recette',
    'version': '1.1.5'
}
# Route pour enregistrer un utilisateur
@app.route('/v1/app/service-api/register', methods=['POST'])
def register():
    """
    Enregistrer un nouvel utilisateur et renvoyer un token.
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
    data = request.json
    # Validation simple des données
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email et mot de passe requis.'}), 400

    exp_date = datetime.utcnow() + timedelta(seconds=900)
    token = jwt.encode({'exp': exp_date, 'email': data['email']}, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token}), 200

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
        api_uri = 'http://localhost:5051/v1/app/get-users'
        headers = {'Content-Type': 'application/json'}
        payload = {'email': email, 'password': password}

        # Envoyer la requête POST à l'API service_dao
        response = requests.post(api_uri, headers=headers, json=payload)

        # Vérifier la réponse de service_dao
        if response.status_code != 200:
            print(f"Réponse brute de service_dao: {response.text}")
            return jsonify({'Erreur': 'Erreur dans la réponse de service-dao'}), response.status_code

        # Si la réponse est OK (200), générer le token
        exp_date = datetime.utcnow() + timedelta(seconds=900)
        token = jwt.encode({'exp': exp_date, 'email': email}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token}), 200

    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        return jsonify({'Erreur': str(e)}), 500


if __name__ == '__main__':
    swagger = Swagger(app)
    app.run(debug=True, host='0.0.0.0',port=5501)