import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any


class DashboardHandler(BaseHTTPRequestHandler):
    queue_ref: Any = None
    budget_ref: Any = None
    engine_ref: Any = None

    def log_message(self, format: str, *args: Any):
        # Override to suppress standard console server request log spam
        pass

    def do_GET(self):
        if self.path == "/status":
            self.send_json(
                {
                    "status": (
                        "active"
                        if self.engine_ref and self.engine_ref.is_running
                        else "idle"
                    ),
                    "progress": (
                        self.engine_ref.get_progress() if self.engine_ref else {}
                    ),
                }
            )
        elif self.path == "/queue":
            self.send_json(self.queue_ref.jobs if self.queue_ref else {})
        elif self.path == "/jobs":
            self.send_json(list(self.queue_ref.jobs.values()) if self.queue_ref else [])
        elif self.path == "/budget":
            self.send_json(self.budget_ref.get_summary() if self.budget_ref else {})
        elif self.path == "/episodes":
            self.send_json(
                {
                    "episodes": (
                        [self.engine_ref.current_episode_id] if self.engine_ref else []
                    )
                }
            )
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not Found"}).encode("utf-8"))

    def send_json(self, data: dict[str, Any] | list):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))


def start_dashboard(
    queue: Any, budget: Any, engine: Any, port: int = 8080
) -> HTTPServer:
    """Start local background REST API for Web Dashboard integration."""
    DashboardHandler.queue_ref = queue
    DashboardHandler.budget_ref = budget
    DashboardHandler.engine_ref = engine

    server = HTTPServer(("127.0.0.1", port), DashboardHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
