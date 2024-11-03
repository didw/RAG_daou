import os
from flask import Flask, request, jsonify
import numpy as np
import requests

app = Flask(__name__)

VECTOR_DB_URL = os.getenv('VECTOR_DB_URL', 'http://vector-db-service:80/query')


@app.route('/retrieve', methods=['POST'])
def retrieve():
    embedding = request.json.get('embedding')
    if not embedding:
        return jsonify({'error': 'No embedding provided'}), 400

    response = requests.post(VECTOR_DB_URL, json={'embedding': embedding})
    if response.status_code != 200:
        return jsonify({'error': 'Vector DB error'}), 500

    results = response.json().get('results')
    documents = [item['document'] for item in results]
    return jsonify({'documents': documents})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
