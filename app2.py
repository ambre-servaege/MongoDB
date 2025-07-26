from flask import Flask, request, jsonify
from pymongo import MongoClient
from flasgger import Swagger
import certifi

# --- Initialisation ---
app = Flask(__name__)
Swagger(app)

# MongoDB connection
client = MongoClient(
    "mongodb+srv://Cluster06212:12345@cluster06212.xhpu0ds.mongodb.net/?retryWrites=true&w=majority&appName=Cluster06212",
    serverSelectionTimeoutMS=50000,
    tls=True,
    tlsCAFile=certifi.where()
)
collection = client['questions_db']['questions_collection']

# --- Keyword Search Endpoint ---
@app.route('/')
def search():
    """
    Recherche de questions par mot-clé
    ---
    parameters:
      - name: query
        in: query
        type: string
        required: true
        description: Le mot-clé à rechercher
    responses:
      200:
        description: Liste des questions contenant le mot-clé
        schema:
          type: array
          items:
            type: object
            properties:
              question:
                type: string
    """
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "Paramètre 'query' manquant"}), 400

    # Recherche insensible à la casse dans MongoDB
    matches = collection.find({"question": {"$regex": query, "$options": "i"}}, {"_id": 0, "question": 1})
    results = [{"question": doc["question"]} for doc in matches]

    return jsonify(results)

# --- Ajouter une question ---
@app.route('/add', methods=['POST'])
def add():
    """
    Ajouter une nouvelle question
    ---
    parameters:
      - name: question
        in: body
        type: string
        required: true
        description: La question à ajouter
        schema:
          type: object
          properties:
            question:
              type: string
    responses:
      200:
        description: Message de confirmation
        schema:
          type: object
          properties:
            message:
              type: string
    """
    data = request.get_json()
    question = data.get("question")
    if not question:
        return jsonify({"error": "Champ 'question' manquant"}), 400

    collection.insert_one({"question": question})
    return jsonify({"message": "Question ajoutée avec succès."})

if __name__ == "__main__":
    app.run(port=8000, debug=True)
