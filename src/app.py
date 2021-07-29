from typing import Dict, Tuple, List

import yaml
from draug.homag.tax import Tax
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.datastructures import FileStorage

from src import taxonomy
from src.json_encoder import JsonEncoder
from src.taxonomy import Symptom

#
# Set up app object
#

app = Flask(__name__)

CORS(app)

app.config['JSON_SORT_KEYS'] = False  # Simplify debugging in frontend
app.json_encoder = JsonEncoder

#
# Create taxonomy
#

tax: Tax

#
# Seed taxonomy
#

# cat_a = add_symptom(None, 'Cat A')
# cat_a_1 = add_symptom(cat_a, 'Cat A.1')
# cat_a_2 = add_symptom(cat_a, 'Cat A.2')
# cat_a_2_1 = add_symptom(cat_a_2, 'Cat A.2.1')
# cat_b = add_symptom(None, 'Cat B')


#
# Set up routes
#

@app.route('/')
def get_root():
    return 'Server is up'


@app.route('/api/1.0.0/symptoms', methods=['GET'])
def get_symptoms() -> Dict:
    return {'taxonomy': taxonomy.get_symptoms()}


@app.route('/api/1.0.0/symptom', methods=['POST'])
def post_symptom() -> Tuple[Response, int]:
    data: Dict = request.get_json()
    parent: Symptom = taxonomy.lookup_symptoms[data['parent']] if data['parent'] else None

    created_symptom = taxonomy.add_symptom(parent, data['name'])

    return jsonify(created_symptom), 201


@app.route('/api/1.0.0/symptom', methods=['PATCH'])
def patch_symptom() -> Response:
    data: Dict = request.get_json()

    symptom_id = data['id']
    new_name = data['name']

    patched_symptom = taxonomy.update_symptom(symptom_id, new_name)

    return jsonify(patched_symptom)


@app.route('/api/1.0.0/symptom/<int:symptom_id>', methods=['DELETE'])
def delete_symptom(symptom_id: int) -> Response:
    symptom = taxonomy.delete_symptom(symptom_id)

    return jsonify(symptom)


@app.route('/api/1.0.0/taxonomy', methods=['PUT'])
def put_taxonomy() -> Tuple[str, int]:
    global tax

    metaYml: FileStorage = request.files['metaYml']
    nodesTxt: FileStorage = request.files['nodesTxt']
    edgesTxt: FileStorage = request.files['edgesTxt']

    meta = yaml.load(metaYml.stream, Loader=yaml.FullLoader)

    node_id_data_list = (line.split(' ', maxsplit=1) for line in nodesTxt.stream.readlines())
    nodes = (int(node_id), eval(data) for node_id, data in node_id_data_list)

    triples = (tuple(map(int, line.split())) for line in edgesTxt.stream)

    tax = Tax.load_from_memory(meta, nodes, triples)

    return '', 201

#
# Run server
#

if __name__ == '__main__':
    app.run()
