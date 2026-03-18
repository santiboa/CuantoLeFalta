"""Flask web app for Cuánto Le Falta landing page."""
import json
from pathlib import Path

from flask import Flask, render_template

app = Flask(__name__)

# Sexenio dates (must match countdown.py)
SEXENIO_END_ISO = "2030-10-01T00:00:00-06:00"
SEXENIO_START_ISO = "2024-10-01T00:00:00-06:00"
TIMEZONE = "America/Mexico_City"

# X/Twitter profile
X_HANDLE = "cuantolefalta"

LATEST_TWEET_FILE = Path(__file__).parent / "latest_tweet.json"


def load_latest_tweet() -> dict:
    """Load the latest posted tweet from cache. Returns empty dict if unavailable."""
    if not LATEST_TWEET_FILE.exists():
        return {}
    try:
        with open(LATEST_TWEET_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


@app.route("/")
def index():
    latest_tweet = load_latest_tweet()
    return render_template(
        "index.html",
        end_iso=SEXENIO_END_ISO,
        start_iso=SEXENIO_START_ISO,
        timezone=TIMEZONE,
        x_handle=X_HANDLE,
        tweet_id=latest_tweet.get("tweet_id"),
    )


if __name__ == "__main__":
    app.run(debug=True)
