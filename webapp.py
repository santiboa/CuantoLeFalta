"""Flask web app for Cuánto Le Falta landing page."""
from flask import Flask, render_template

app = Flask(__name__)

# Sexenio dates (must match countdown.py)
SEXENIO_END_ISO = "2030-10-01T00:00:00"
SEXENIO_START_ISO = "2024-10-01T00:00:00"
TIMEZONE = "America/Mexico_City"

# X/Twitter profile
X_HANDLE = "cuantolefalta"


@app.route("/")
def index():
    return render_template(
        "index.html",
        end_iso=SEXENIO_END_ISO,
        start_iso=SEXENIO_START_ISO,
        timezone=TIMEZONE,
        x_handle=X_HANDLE,
    )


if __name__ == "__main__":
    app.run(debug=True)
