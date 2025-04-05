from flask import render_template, redirect, url_for, request, Blueprint

from app import db
from appconfig import AppConfig
from blueprints.webapp.models import ConfigModel

cfg_bp = Blueprint("cfg", __name__)


@cfg_bp.route('/', methods=["GET"])
def index():
    configs = ConfigModel.query.all()

    print(configs)

    return render_template('config_list.html', configs=configs)


@cfg_bp.route("/delete/<int:cfg_id>", methods=["GET"])
def delete(cfg_id: int):
    db.session.delete(ConfigModel.query.filter(ConfigModel.id == cfg_id).first())
    db.session.commit()

    return redirect(url_for(".index"))


@cfg_bp.route("/create", methods=["POST", "GET"])
def create():
    if request.method == "GET":
        return render_template("config_create.html", available_models=AppConfig.AVAILABLE_MODELS)

    config_name = request.form.get("name", None)
    model_id: str = request.form.get("model_id", None)
    chunk_size = request.form.get("chunkSize", type=int)
    document_count = request.form.get("documentCount", type=int)

    selected_model = next((x for x in AppConfig.AVAILABLE_MODELS if x["id"] == model_id), None)

    # TODO :: Some kind of error message
    if not config_name or not selected_model or not chunk_size or not document_count:
        return redirect(url_for(".index"))

    print(selected_model)
    new_config = ConfigModel(name=config_name, model_id=selected_model['id'], model_name=selected_model['name'],
                             chunk_size=chunk_size, document_count=document_count)
    db.session.add(new_config)
    db.session.commit()

    return redirect(url_for(".index"))
