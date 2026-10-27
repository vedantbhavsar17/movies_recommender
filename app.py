from flask import Flask, jsonify, render_template, request

from backendlogic import get_movie_titles, recommend_movie

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/recommender", methods=["GET", "POST"])
def recommender():
    selected_title = ""
    recommendations = None
    error = None

    if request.method == "POST":
        selected_title = request.form.get("title", "").strip()
        try:
            recommendations = recommend_movie(selected_title, n=5)
        except (ValueError, LookupError) as exc:
            error = str(exc)

    return render_template(
        "recommender.html",
        titles=get_movie_titles(),
        selected_title=selected_title,
        recommendations=recommendations,
        error=error,
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
