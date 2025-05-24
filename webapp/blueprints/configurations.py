from flask import render_template, redirect, url_for, request, Blueprint

from extensions import db
from app_config import AppConfig
from .models import ConfigModel

cfg_bp = Blueprint("cfg", __name__,static_folder="static", template_folder="templates")


@cfg_bp.route('/', methods=["GET"])
def index():
    """
    The main configuration page that lets the user create and delete configurations.

    GET Parameters:
    err: [Optional] error message to display to the user as a simple popup.
    """

    error_msg = request.args.get("err", None)

    configs = ConfigModel.get_all()

    print(configs)

    return render_template('config_list.html', configs=configs, popup_success=False if error_msg else None,
                           popup_msg=error_msg)


@cfg_bp.route("/delete/<int:cfg_id>", methods=["GET"])
def delete(cfg_id: int):
    """
    Deletes a configuration from the database.
    """
    db.session.delete(ConfigModel.query.filter(ConfigModel.id == cfg_id).first())
    db.session.commit()

    return redirect(url_for(".index"))


@cfg_bp.route("/create", methods=["POST", "GET"])
def create():
    """
    GET REQUEST:
    Renders a page with configuration creation form.

    POST REQUEST:
    Creates a new configuration for the user. and redirects to configuration list page.
    The configuration values are passed as form parameters.

    """
    if request.method == "GET":
        return render_template("config_create.html", available_models=AppConfig.AVAILABLE_MODELS,available_config_fields=AppConfig.AVAILABLE_CONFIG_FIELDS)

    config_name = request.form.get("name", None)
    model_id: str = request.form.get("model_id", None)
    chunk_size = request.form.get("chunkSize", type=int)

    selected_model = next((x for x in AppConfig.AVAILABLE_MODELS if x["id"] == model_id), None)

    if selected_model is None:
        return redirect(url_for(".index", err="Couldn't find selected model."))

    if any([(True if field is None else False) for field in [config_name, chunk_size]]):
        return redirect(url_for(".index", err="All fields must be filled out."))

    print(selected_model)
    new_config = ConfigModel(name=config_name, model_id=selected_model['id'], model_name=selected_model['name'],
                             chunk_size=chunk_size)
    db.session.add(new_config)
    db.session.commit()

    return redirect(url_for(".index"))
