from flask import Flask, render_template, request, jsonify
from simulation import Retire_Simulate

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/simulate", methods=["POST"])
def simulate():
    data = request.get_json(force=True)

    try:
        starting_amount      = float(data["starting_amount"])
        monthly_contribution = float(data["monthly_contribution"])
        retirement_target    = float(data["retirement_target"])
        n_simulations        = int(data.get("n_simulations", 1000))
        max_years            = int(data.get("max_years", 40))
    except (KeyError, ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400

    n_simulations = max(100, min(n_simulations, 5000))
    max_years     = max(5,   min(max_years, 60))
    starting_amount      = max(0, starting_amount)
    monthly_contribution = max(0, monthly_contribution)
    retirement_target    = max(1, retirement_target)

    result = Retire_Simulate(
        starting_amount=starting_amount,
        monthly_contribution=monthly_contribution,
        retirement_target=retirement_target,
        n_simulations=n_simulations,
        max_years=max_years,
    )
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
