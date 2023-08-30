from app.performance import init_performance_monitoring
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.samplers import ProbabilitySampler

init_performance_monitoring()

from flask import Flask  # noqa
from app import create_app  # noqa

application = Flask("app")


def callback_function(envelope):
    envelope.tags['ai.cloud.role'] = 'admin'


azure_exporter = AzureExporter()
azure_exporter.add_telemetry_processor(callback_function)

FlaskMiddleware(
    application,
    exporter=azure_exporter,
    sampler=ProbabilitySampler(rate=1.0),
)

create_app(application)
