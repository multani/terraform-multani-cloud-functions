import os
from urllib.parse import urlparse

import structlog
from flask import current_app
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.wsgi import OpenTelemetryMiddleware
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.cloud_trace_propagator import CloudTraceFormatPropagator
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export import SpanExporter

LOGGER = structlog.get_logger()

TRACE = None


class NullSpanExporter(SpanExporter):
    pass


def get_tracer(name, trace=None):
    if trace is None:
        global TRACE
        trace = TRACE

    if trace is None:
        raise RuntimeError("tracing is not enabled yet")

    tracer = trace.get_tracer(name)
    return tracer


def build_exporter(uri):

    exporter = NullSpanExporter()
    u = urlparse(uri)

    if u.scheme == "gcp":
        exporter = CloudTraceSpanExporter(resource_regex="service.*")

    elif u.scheme == "otel+grpc":
        if u.netloc == "":
            endpoint = "localhost:4317"
        else:
            endpoint = u.netloc

        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    elif u.scheme == "console":
        exporter = ConsoleSpanExporter()

    LOGGER.debug("Tracing exporter configured", exporter=exporter)
    return exporter


def get_current_span():
    return trace.get_current_span()


def global_setup(exporter=None):
    logger = LOGGER.bind(kind="setup-otel")
    logger.debug("Setting up tracing")

    if exporter is None:
        exporter = build_exporter("gcp:")

    set_global_textmap(CloudTraceFormatPropagator())
    service_name = os.environ.get("K_SERVICE", "functions")
    resource = Resource(attributes={SERVICE_NAME: service_name})
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(tracer_provider)

    # Flask Telemetry
    try:
        current_app.wsgi_app
    except RuntimeError:
        # We are not running in a Flask context, let's skip the initialization
        # of the HTTP middleware in this case.
        pass
    else:
        current_app.wsgi_app = OpenTelemetryMiddleware(current_app.wsgi_app)

    # httpx telemetry
    HTTPXClientInstrumentor().instrument()

    global TRACE
    TRACE = trace

    logger.debug("Tracing setup complete")
