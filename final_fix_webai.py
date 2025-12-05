"""
Final fix for run.py - Force webai mode in the controller loop
"""

# Read run.py
with open('src/run.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the line where current_mode is set from requested or initial_mode
# and force it to always be "webai"
import re

# Pattern: current_mode = requested or initial_mode
pattern = r'(current_mode = requested or initial_mode)'
replacement = r'current_mode = "webai"  # FORCED WEBAI MODE - Always use cookies\n                # \1'

content_modified = re.sub(pattern, replacement, content)

# Also force shared_state to webai at the start
pattern2 = r'(shared_state = manager\.dict\(\{"requested_mode": None\}\))'
replacement2 = r'\1\n    shared_state["requested_mode"] = "webai"  # Force WebAI from start'

content_modified = re.sub(pattern2, replacement2, content_modified)

# Write back
with open('src/run.py', 'w', encoding='utf-8') as f:
    f.write(content_modified)

print("✅ run.py modified - WebAI mode forced in controller loop")
print("Restart server - it will start directly in WebAI mode and work!")
