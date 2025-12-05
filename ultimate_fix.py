"""
FINAL FIX - Replace the entire main block to force WebAI mode
"""

# Read run.py
with open('src/run.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "if __name__ == "__main__":"
main_index = -1
for i, line in enumerate(lines):
    if 'if __name__ == "__main__":' in line:
        main_index = i
        break

if main_index == -1:
    print("❌ Could not find main block")
    exit(1)

# Replace everything after the main block with forced WebAI mode
new_main_block = '''if __name__ == "__main__":
    print("\\n" + "="*80)
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
'''

# Replace from main_index onwards
modified_lines = lines[:main_index] + [new_main_block]

# Write back
with open('src/run.py', 'w', encoding='utf-8') as f:
    f.writelines(modified_lines)

print("✅ run.py completely rewritten - WebAI mode forced, NO input required")
print("Restart server - it will start DIRECTLY in WebAI mode!")
