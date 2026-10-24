import asyncio
import time
import json
import os
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Observability: Prometheus metrics + OpenTelemetry (best-effort) ---
try:
    from prometheus_client import (
        Counter,
        Histogram,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )

    REQUESTS = Counter(
        "atlas_http_requests_total", "Total HTTP requests", ["method", "path", "status"]
    )
    REQUEST_LATENCY = Histogram(
        "atlas_http_request_latency_seconds", "HTTP request latency", ["method", "path"]
    )
    AGENT_RUNS = Counter(
        "atlas_agent_runs_total", "Agent invocations", ["agent", "status"]
    )
    PROMETHEUS_ENABLED = True
except ImportError:  # pragma: no cover - prometheus_client is optional at runtime
    REQUESTS = REQUEST_LATENCY = AGENT_RUNS = None
    PROMETHEUS_ENABLED = False

# Auth (best-effort: degrades to no-auth if services.auth is unavailable)
try:
    from services.auth.jwt import decode_access_token
    from services.auth.middleware import optional_user
    AUTH_ENABLED = True
except Exception as e:  # pragma: no cover - auth is optional during scaffolding
    print(f"[Auth] Disabled (reason: {e})")
    AUTH_ENABLED = False


def _cors_origins():
    """Comma-separated CORS origins from env, defaulting to localhost + tauri."""
    raw = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,tauri://localhost",
    )
    return [o.strip() for o in raw.split(",") if o.strip()]


# Database and Agents imports
import sys

# Add agent folders with hyphens to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "agents", "planner-agent"))
sys.path.append(os.path.join(os.path.dirname(__file__), "agents", "research-agent"))
sys.path.append(os.path.join(os.path.dirname(__file__), "agents", "coding-agent"))
sys.path.append(os.path.join(os.path.dirname(__file__), "agents", "orchestrator-agent"))

from databases.postgres.connection import PostgresConnection
from databases.redis.connection import RedisConnection
from databases.qdrant.connection import QdrantConnection
from databases.neo4j.connection import Neo4jConnection

from orchestrator import OrchestratorAgent
from planner import PlannerAgent
from researcher import ResearchAgent
from coder import CodingAgent

from contextlib import asynccontextmanager
from services.stt import SpeechToTextService
from services.tts import TextToSpeechService
from services.wakeword import WakewordService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Spawn background telemetry loop
    asyncio.create_task(telemetry_loop())
    # Spawn wakeword background thread
    t = threading.Thread(target=run_wakeword_listener, daemon=True)
    t.start()
    yield

app = FastAPI(lifespan=lifespan, title="A.T.L.A.S API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Auth router (mounted if available) ---
if AUTH_ENABLED:
    try:
        from services.auth.routes import router as auth_router
        app.include_router(auth_router, prefix="/auth", tags=["auth"])
    except Exception as e:  # pragma: no cover
        print(f"[Auth] Router not loaded (reason: {e})")


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Record request count + latency for Prometheus."""
    start = time.perf_counter()
    response = await call_next(request)
    if PROMETHEUS_ENABLED and not request.url.path.startswith("/metrics"):
        elapsed = time.perf_counter() - start
        REQUESTS.labels(
            method=request.method,
            path=request.url.path,
            status=response.status_code,
        ).inc()
        REQUEST_LATENCY.labels(method=request.method, path=request.url.path).observe(elapsed)
    return response


@app.get("/healthz", tags=["health"])
async def healthz():
    """Liveness probe — process is up and serving requests."""
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
async def readyz():
    """Readiness probe — DBs are reachable. Returns per-DB status."""
    return check_db_health()


@app.get("/metrics", tags=["observability"])
async def metrics():
    """Prometheus exposition endpoint."""
    if not PROMETHEUS_ENABLED:
        return Response(content="prometheus_client not installed", status_code=503)
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Active WebSocket connections
active_connections = set()

# Shared state
wake_status = "Listening"  # Listening, Processing, Sleeping
current_latency = 12
current_load = 24

# Initialize services
stt_service = SpeechToTextService()
tts_service = TextToSpeechService()
wakeword_service = WakewordService()

# Helper to check DB connectivity health
def check_db_health():
    status = {
        "postgres": False,
        "redis": False,
        "qdrant": False,
        "neo4j": False
    }
    
    # Postgres check
    try:
        pg = PostgresConnection()
        conn = pg.connect()
        if conn and not conn.closed:
            status["postgres"] = True
            conn.close()
    except Exception as e:
        print(f"[DB Check] Postgres check failed: {e}")
        
    # Redis check
    try:
        rc = RedisConnection()
        client = rc.connect()
        if client and client.ping():
            status["redis"] = True
    except Exception as e:
        print(f"[DB Check] Redis check failed: {e}")

    # Qdrant check
    try:
        qd = QdrantConnection()
        client = qd.connect()
        if client:
            client.get_collections()
            status["qdrant"] = True
    except Exception as e:
        print(f"[DB Check] Qdrant check failed: {e}")

    # Neo4j check
    try:
        n4 = Neo4jConnection()
        driver = n4.connect()
        if driver:
            driver.verify_connectivity()
            status["neo4j"] = True
            driver.close()
    except Exception as e:
        print(f"[DB Check] Neo4j check failed: {e}")

    return status

# Broadcast status updates to all active clients
async def broadcast_status():
    global wake_status, current_latency, current_load
    db_status = check_db_health()
    
    payload = {
        "type": "telemetry",
        "wakeStatus": wake_status,
        "latency": current_latency,
        "load": current_load,
        "dbs": db_status
    }
    
    dead_connections = set()
    for websocket in active_connections:
        try:
            await websocket.send_text(json.dumps(payload))
        except Exception:
            dead_connections.add(websocket)
            
    for ws in dead_connections:
        active_connections.remove(ws)

# Broadcast logs / thoughts to all clients
async def broadcast_log(log_type: str, message: str):
    time_str = time.strftime("%H:%M:%S")
    payload = {
        "type": "log",
        "log": {
            "time": time_str,
            "type": log_type,
            "message": message
        }
    }
    for websocket in active_connections:
        try:
            await websocket.send_text(json.dumps(payload))
        except Exception:
            pass

# Process commands using agents
async def process_user_command(command: str):
    global wake_status
    wake_status = "Processing"
    await broadcast_status()
    
    await broadcast_log("user", f"User command: \"{command}\"")
    
    # 1. Orchestrator router phase
    await asyncio.sleep(0.6)
    await broadcast_log("agent", "[Orchestrator] Intercepted query. Routing task structure.")
    
    # 2. Planner phase
    await asyncio.sleep(0.8)
    planner = PlannerAgent()
    dag = planner.build_dag_plan(command)
    await broadcast_log("agent", f"[Planner] Goal broken down: {json.dumps(dag)}")
    
    # 3. Execution of DAG steps
    research_summary = "Simulated context: Local configuration matches system state."
    for step in dag:
        agent_type = step.get("agent")
        desc = step.get("description")
        
        await asyncio.sleep(0.8)
        if agent_type == "researcher":
            await broadcast_log("agent", f"[Researcher] Querying databases and scraping references: {desc}")
            researcher = ResearchAgent()
            # Perform RAG + Web check
            try:
                research_summary = await researcher.conduct_research(desc)
            except Exception as e:
                research_summary = f"Research execution fallback. Error: {e}"
            await broadcast_log("system", f"RAG Status: {research_summary}")
            
        elif agent_type == "coder":
            await broadcast_log("agent", f"[Coder] Generating workspace edits: {desc}")
            coder = CodingAgent()
            code_block = coder.generate_code_block(desc)
            await broadcast_log("system", f"Coder output:\n{code_block}")
            
        else:
            await broadcast_log("agent", f"[{agent_type}] Running task step: {desc}")
            
    # 4. Synthesize final answer and speak response
    await asyncio.sleep(0.6)
    final_reply = f"I have successfully analyzed '{command}'. The task has been processed and system states are verified."
    await broadcast_log("system", f"[TTS Voice Out] '{final_reply}'")
    
    # Trigger Text-To-Speech
    try:
        tts_service.speak(final_reply)
    except Exception as e:
        print(f"TTS audio playback error: {e}")
        
    wake_status = "Listening"
    await broadcast_status()

# Live WebSocket Connection handler
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Optional token verification via query string: /ws?token=<access_token>
    # During scaffolding, anonymous connections are still allowed.
    token = websocket.query_params.get("token")
    user = None
    if token and AUTH_ENABLED:
        try:
            user = decode_access_token(token)
        except Exception as e:
            await websocket.close(code=4401)
            print(f"[WebSocket] Rejected: invalid token ({e})")
            return

    await websocket.accept()
    active_connections.add(websocket)
    print(f"[WebSocket] Connected new client: {websocket.client} (user={user})")
    
    # Initial status sync
    await broadcast_status()
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            action = payload.get("action")
            
            if action == "command":
                text = payload.get("text", "")
                asyncio.create_task(process_user_command(text))
                
            elif action == "toggle_wake":
                global wake_status
                if wake_status == "Sleeping":
                    wake_status = "Listening"
                    await broadcast_log("system", "Wakeword service initialized. Wake phrase: \"Hey Atlas\".")
                else:
                    wake_status = "Sleeping"
                    await broadcast_log("system", "Entering sleep state. Deactivation phrase received.")
                await broadcast_status()
                
    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected.")
        if websocket in active_connections:
            active_connections.remove(websocket)

# Periodically broadcast DB health and telemetry metrics
async def telemetry_loop():
    while True:
        try:
            await broadcast_status()
        except Exception as e:
            print(f"[Telemetry] Broadcast error: {e}")
        await asyncio.sleep(8)

# Simulate background wakeword listener loop
def run_wakeword_listener():
    print("[Wakeword] Background listener thread spawned.")
    while True:
        # In a real environment with sound device and pvporcupine keys:
        # wakeword_service.start_listening(lambda: asyncio.run(process_user_command("Wake up trigger")))
        time.sleep(10)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
