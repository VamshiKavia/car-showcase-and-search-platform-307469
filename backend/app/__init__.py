from flask import Flask
from flask_cors import CORS
from flask_smorest import Api

from .routes.cars import blp as cars_blp
from .routes.health import blp as health_blp

app = Flask(__name__)
app.url_map.strict_slashes = False

# Allow frontend dev server to call the API.
# NOTE: If you need more origins (e.g., deployed frontend), add them here.
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ]
        }
    },
)

# Flask-Smorest / OpenAPI config (keeps Swagger UI under /docs).
app.config["API_TITLE"] = "My Flask API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)
api.register_blueprint(health_blp)
api.register_blueprint(cars_blp)
