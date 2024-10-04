# app.py

from flask import Flask, request, jsonify
from code_review import analyze_code, refactor_code
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend interaction

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    code = data['code']
    language = data.get('language', 'python').lower()
    issues = analyze_code(code, language)
    return jsonify({"issues": issues})

@app.route('/refactor', methods=['POST'])
def refactor():
    data = request.get_json()
    code = data['code']
    language = data.get('language', 'python').lower()
    refactored_code = refactor_code(code, language)
    return jsonify({"refactored_code": refactored_code})

if __name__ == '__main__':
    app.run(debug=True)
