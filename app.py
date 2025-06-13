from flask import Flask, request, jsonify, send_from_directory
from bot import load_faq_data, find_best_faq_answer, get_gpt_answer
import os

app = Flask(__name__)
faq_df = load_faq_data()

@app.route("/", methods=["GET"])
def serve_index():
    return send_from_directory(".", "index.html")

@app.route("/api/messages", methods=["POST"])
def handle_message():
    data = request.get_json()
    user_input = data.get("text", "")

    if not user_input:
        return jsonify({"text": "Please enter a question."})

    answer = find_best_faq_answer(user_input, faq_df)
    if answer:
        return jsonify({"text": answer})
    else:
        gpt_answer = get_gpt_answer(user_input)
        return jsonify({"text": gpt_answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
