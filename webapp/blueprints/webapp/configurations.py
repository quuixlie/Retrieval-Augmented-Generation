from flask import render_template, redirect, url_for, request, Blueprint

cfg_bp = Blueprint("cfg", __name__)

AVAILABLE_MODELS = ["MODEL 1", "MODEL 2", "MODEL 3"]


@cfg_bp.route('/', methods=["GET"])
def index():
    return render_template('configurations.html', available_models=AVAILABLE_MODELS)


@cfg_bp.route("/delete/<int:id>", methods=["POST"])
def delete(id: int):
    return redirect(url_for(".index"))


@cfg_bp.route("/create", methods=["POST"])
def create():
    model: str = request.form.get("model", None)

    if model not in AVAILABLE_MODELS:
        return redirect(url_for(".index"))

    return redirect(url_for(".index"))
