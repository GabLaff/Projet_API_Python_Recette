# app/routes/recette/mod_recette.py
import jwt
import requests
from flasgger import Swagger
from flask import Flask, jsonify, request, Blueprint, current_app

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Le hockey recommence'
app.config['SWAGGER'] = {
    'title': 'Gestion de service de retour de Recette',
    'version': '1.1.5'
}
# Route pour obtenir des recettes en fonction d'un token et des ingrédients
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
        api_uri = 'http://localhost:5050/v1/app/recettes'
        params = {'ingredient': ingredient}

        # Envoyer la requête GET à l'API service_dao
        response = requests.get(api_uri, params=params)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'Erreur': 'Erreur dans la réponse de service-dao'}), response.status_code

    except Exception as e:
        return jsonify({'Erreur': 'Dans la requête pour accéder au dao', 'details': str(e)}), 500


if __name__ == '__main__':
    swagger = Swagger(app)
    app.run(debug=True, host='0.0.0.0',port=5500)

"""
# Route pour enregistrer un utilisateur
@app.route('/v1/app/service-api/register', methods=['POST'])
def register():
    # Ici, tu devrais ajouter la logique pour enregistrer un utilisateur
    exp_date = datetime.utcnow() + timedelta(seconds=900)
    token = jwt.encode({'exp': exp_date}, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token}), 201


# Route pour connecter un utilisateur
@app.route('/v1/app/service-api/login', methods=['POST'])
def login():
    # Ici, tu devrais ajouter la logique pour valider l'utilisateur
    exp_date = datetime.utcnow() + timedelta(seconds=900)
    token = jwt.encode({'exp': exp_date}, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token}), 200
    """

