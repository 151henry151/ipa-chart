from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import gruut
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/interactive')
def interactive():
    return send_from_directory('.', 'interactive_ipa.html')

@app.route('/ucla_ipa')
def ucla_ipa():
    return send_from_directory('.', 'ucla_ipa.html')

@app.route('/ipa', methods=['POST'])
def ipa():
    data = request.get_json()
    text = data.get('text', '')
    ipa_result = ''
    try:
        # Use gruut to get IPA for each sentence
        sentences = gruut.sentences(text, lang="en-us")
        ipa_chunks = []
        for sentence in sentences:
            for word in sentence:
                # word.phonemes is the list of IPA phonemes for the word
                if word.phonemes:
                    ipa_chunks.append(''.join(word.phonemes))
                else:
                    ipa_chunks.append(word.text)
        ipa_result = ' '.join(ipa_chunks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'ipa': ipa_result})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 