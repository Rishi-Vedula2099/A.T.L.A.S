try:
    from prometheus_client import Counter, Histogram, CollectorRegistry
except ImportError:
    Counter = None
    Histogram = None
    CollectorRegistry = None

class PrometheusRegistry:
    def __init__(self):
        self.registry = CollectorRegistry() if CollectorRegistry else None
        if Counter:
            self.agent_runs = Counter(
                "atlas_agent_runs_total", 
                "Total number of agent runs executed", 
                ["agent_name", "status"],
                registry=self.registry
            )
            self.latency = Histogram(
                "atlas_agent_run_latency_seconds",
                "Execution latency for agents",
                ["agent_name"],
                registry=self.registry
            )
        else:
            self.agent_runs = None
            self.latency = None

    def track_run(self, agent: str, status: str, duration: float):
        print(f"[Metrics] Tracked {agent} run ({status}) in {duration:.3f}s")
        if self.agent_runs:
            self.agent_runs.labels(agent_name=agent, status=status).inc()
            self.latency.labels(agent_name=agent).observe(duration)
        # In actual setups, expose this registry to a scraping endpoint
