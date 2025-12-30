from flask import Flask, render_template, request, Response, jsonify
import os, shutil

from ingest_remote import Ingestor
from engine_remote import RAGEngine

INDEX = "faiss.index"
META  = "meta.json"

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
    pdf.save("temp.pdf")

    ing = Ingestor()
    ing.ingest("temp.pdf", INDEX, META)

    os.remove("temp.pdf")
    return {"status": "ok"}

@app.post("/ask")
def ask():
    if not os.path.exists(INDEX):
        return jsonify({"error": "No document"}), 400

    q = request.json["question"]
    engine = RAGEngine(INDEX, META)
    chunks = engine.retrieve(q)

    if not chunks:
        return Response("OUT OF CONTEXT", mimetype="text/plain")

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
