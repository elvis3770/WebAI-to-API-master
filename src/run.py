# src/run.py
import argparse
import asyncio
import uvicorn
import multiprocessing
import time
import sys
import threading
import os
import signal
from typing import Dict, Union, Tuple
from fastapi.routing import APIRoute
from typing import TYPE_CHECKING

# This block is only processed by type checkers like Pylance
if TYPE_CHECKING:
    from multiprocessing.synchronize import Event as MultiprocessingEvent

# Import tomli to read pyproject.toml
try:
    import tomli
except ImportError:
    # For Python 3.11+, tomllib is in the standard library
    try:
        import tomllib as tomli
    except ImportError:
        tomli = None

# --- App and Service Imports ---
from app.config import load_config
from app.main import app as webai_app
from app.services.gemini_client import init_gemini_client

# Conditionally import g4f runner function
try:
    from g4f.api import run_api as run_g4f_api

    G4F_AVAILABLE = True
except ImportError:
    G4F_AVAILABLE = False


# Helper class for terminal colors
class Colors:
    """A class to hold ANSI color codes for terminal output."""

    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


# --- Helper function to get app info ---
def get_app_info() -> Tuple[str, str]:
    """Reads application name and version from pyproject.toml."""
    if not tomli:
        return "WebAI to API", "N/A (tomli not installed)"
    try:
        with open("pyproject.toml", "rb") as f:
            toml_data = tomli.load(f)
        poetry_data = toml_data.get("tool", {}).get("poetry", {})
        name = poetry_data.get("name", "WebAI-to-API").replace("-", " ").title()
        version = poetry_data.get("version", "N/A")
        return name, version
    except (FileNotFoundError, KeyError):
        return "WebAI-to-API", "N/A"


# --- UNIFIED Server Runner Functions ---


def start_webai_server(
    host: str, port: int, reload: bool, stop_event: "MultiprocessingEvent"
):
    """Starts the WebAI Uvicorn server with a graceful shutdown mechanism."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    config = uvicorn.Config(
        webai_app, host=host, port=port, reload=reload, log_config=None
    )
    server = uvicorn.Server(config)

    def shutdown_monitor():
        stop_event.wait()
        server.should_exit = True

    monitor_thread = threading.Thread(target=shutdown_monitor, daemon=True)
    monitor_thread.start()

    print_server_info(host, port, "webai")
    server.run()
    print(f"\n[WebAI Server] Process exited gracefully.")


def start_g4f_server(host: str, port: int, stop_event: "MultiprocessingEvent"):
    """Starts the G4F server with a graceful shutdown mechanism."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    def shutdown_monitor():
        stop_event.wait()
        print(f"\n[G4F Server] Stop signal received. Exiting.")
        os._exit(0)

    monitor_thread = threading.Thread(target=shutdown_monitor, daemon=True)
    monitor_thread.start()

    print_server_info(host, port, "g4f")
    run_g4f_api(host=host, port=port, proxy=None)


# --- Standard Input Listener ---
def input_listener(shared_state: Dict):
    """Listens for user input in a separate thread to avoid blocking."""
    while True:
        try:
            choice = input()
            if choice == "1":
                shared_state["requested_mode"] = "webai"
            elif choice == "2":
                shared_state["requested_mode"] = "g4f"
        except (EOFError, KeyboardInterrupt):
            break


# --- Helper Function for Printing Info ---
def print_server_info(host: str, port: int, mode: str):
    """Displays complete, formatted information about the running server."""
    protocol = "http"
    base_url = f"{protocol}://{host}:{port}"
    app_name, app_version = get_app_info()
    app_info_line = f"{app_name} v{app_version}".center(80)
    print("\n" + "=" * 80)
    print(f"{Colors.BOLD}{Colors.YELLOW}{app_info_line}{Colors.RESET}")
    if mode == "webai":
        print("🚀 WebAI-to-API Server is RUNNING (Primary Mode) 🚀".center(80))
        print("=" * 80)
        print("\n✨ Available Services:")
        print(f"  - Docs (Swagger): {base_url}/docs")
        print("\n⚙️ Config.conf:")
        try:
            CONFIG = load_config()
            print(f"  - Browser: {CONFIG['Browser']['name']}")
            print(f"  - Model: {CONFIG['AI']['default_model_gemini']}")
        except Exception:
            print("  - Could not load config details.")
        print("\n🔗 API Endpoints:")
        paths = sorted(
            list(
                set(
                    route.path
                    for route in webai_app.routes
                    if isinstance(route, APIRoute)
                )
            )
        )
        for path in paths:
            if path.startswith("/") and path not in [
                "/docs",
                "/redoc",
                "/openapi.json",
            ]:
                print(f"  - {base_url}{path}")
    elif mode == "g4f":
        print("🚀 gpt4free Server is RUNNING 🚀".center(80))
        print("=" * 80)
        g4f_base_url = f"{base_url}/v1"
        print("\n✨ gpt4free Service Info:")
        print(f"  - Base URL: {g4f_base_url}")
        print(f"  - Docs (Swagger): {base_url}/docs")
        print("\n🔍 API Discovery Endpoints:")
        print(f"  - Models   : {g4f_base_url}/models")
        print(f"  - Providers: {g4f_base_url}/providers")
        print("\n🔗 Main API Endpoints:")
        print(f"  - Chat Completions: {g4f_base_url}/chat/completions")
        print(f"  - Image Generation: {g4f_base_url}/images/generate")

        print(
            f"\n{Colors.BOLD}{Colors.YELLOW}IMPORTANT USAGE NOTES FOR gpt4free MODE:{Colors.RESET}"
        )
        print(
            f"  - {Colors.YELLOW}To avoid {Colors.BOLD}ProviderNotFoundError{Colors.RESET}{Colors.YELLOW}, your client must send a valid provider name (not a model name).{Colors.RESET}"
        )
        print(
            f"    {Colors.YELLOW}Check the list of valid providers at the {Colors.CYAN}/v1/providers{Colors.YELLOW} endpoint.{Colors.RESET}"
        )
    print("\n" + "=" * 80)
    instruction_text = "Press '1' then Enter for WebAI (Faster) | '2' then Enter for gpt4free | Ctrl+C to Quit"
    colored_instructions = (
        f"{Colors.BOLD}{Colors.YELLOW}{instruction_text.center(80)}{Colors.RESET}"
    )
    print(colored_instructions)
    print("=" * 80)


# --- Main Execution Block ---
if __name__ == "__main__":
    print("\n" + "="*80)
    print("WebAI-to-API v0.5.0 - FORCED WEBAI MODE (Cookies)")
    print("="*80)
    
    # Windows fix
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        multiprocessing.freeze_support()
    
    # Parse args
    parser = argparse.ArgumentParser(description="WebAI-to-API Server")
    parser.add_argument("--host", type=str, default="localhost", help="Host address")
    parser.add_argument("--port", type=int, default=6969, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()
    
    # Check if Gemini client can initialize
    print("INFO:     Checking Gemini client (cookies)...")
    webai_is_available = asyncio.run(init_gemini_client())
    
    if not webai_is_available:
        print("ERROR:    Gemini client failed to initialize. Check cookies in .env")
        sys.exit(1)
    
    print("INFO:     ✅ Gemini client initialized successfully")
    print("INFO:     🚀 Starting server in WEBAI mode (forced)")
    print(f"INFO:     Server will run on http://{args.host}:{args.port}")
    print("="*80)
    
    # Start WebAI server directly - NO INPUT REQUIRED
    stop_event = multiprocessing.Event()
    start_webai_server(args.host, args.port, args.reload, stop_event)
