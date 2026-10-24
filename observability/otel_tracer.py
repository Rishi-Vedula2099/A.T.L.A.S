try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
except ImportError:
    trace = None
    TracerProvider = None
    SimpleSpanProcessor = None
    ConsoleSpanExporter = None

class OTELTracer:
    def __init__(self):
        self.tracer = None

    def initialize(self):
        if not trace:
            print("[OTEL] OpenTelemetry is not installed. Mocking traces.")
            return
            
        provider = TracerProvider()
        processor = SimpleSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer("atlas-ai-os")
        print("[OTEL] Tracer configured to dump logs to Console.")

    def get_tracer(self):
        if not self.tracer:
            self.initialize()
        return self.tracer
