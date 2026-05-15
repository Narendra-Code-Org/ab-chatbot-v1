import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from chatbot.ingest_default import ingest_default_docs
from chatbot.ingest_uploaded import ingest_uploaded_doc
from chatbot.chain import ask_question

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data/uploaded_pdfs'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Ingest default documents on startup
with app.app_context():
    try:
        ingest_default_docs()
    except Exception as e:
        print(f"Error during default ingestion: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    try:
        response = ask_question(question)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            ingest_uploaded_doc(filepath)
            return jsonify({"message": f"Successfully processed {filename}"})
        except Exception as e:
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500
    else:
        return jsonify({"error": "Allowed file types are .pdf"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
