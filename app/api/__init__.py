from flask import Blueprint
from flask_restful import Api

from app.api.report import ReportGenerator, Report

api_blueprint = Blueprint("api", __name__)
_api = Api(api_blueprint)

# Register the resources of the API to it.
_api.add_resource(ReportGenerator, "/trigger_report")
_api.add_resource(Report, "/get_report")
