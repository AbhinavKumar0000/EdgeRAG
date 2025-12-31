from flask import Flask, render_template, request, Response, jsonify
import os, shutil, tempfile

from ingest_remote import Ingestor
from engine_remote import RAGEngine

TMP_DIR = tempfile.gettempdir()
INDEX = os.path.join(TMP_DIR, "faiss.index")
META  = os.path.join(TMP_DIR, "meta.json")

app = Flask(__name__)

def clear_db():
    for f in [INDEX, META]:
        if os.path.exists(f):
            os.remove(f)

@app.route("/")
def home():
    clear_db()  # auto flush on reload
    return render_template("index.html")

@app.post("/upload")
def upload():
    clear_db()
    pdf = request.files["file"]
    pdf_path = os.path.join(TMP_DIR, "temp.pdf")
    pdf.save(pdf_path)

    ing = Ingestor()
    ing.ingest(pdf_path, INDEX, META)

    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    return {"status": "ok"}

def stream_static_msg(msg):
    import time
    for word in msg.split():
        yield word + " "
        time.sleep(0.05)

@app.post("/ask")
def ask():
    if not os.path.exists(INDEX):
        return jsonify({"error": "No document"}), 400

    q = request.json["question"]
    engine = RAGEngine(INDEX, META)
    chunks = engine.retrieve(q)

    if not chunks:
        return Response(stream_static_msg("I couldn't find relevant information in the uploaded document to answer your question."), mimetype="text/plain")

    return Response(
        engine.stream_answer(q, chunks),
        mimetype="text/plain"
    )

@app.post("/clear")
def clear():
    clear_db()
    return {"cleared": True}

if __name__ == "__main__":
    app.run(debug=True)
