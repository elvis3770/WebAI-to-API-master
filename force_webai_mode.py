"""
Force WebAI mode in run.py - bypass input listener completely
"""

# Read run.py
with open('src/run.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with initial_mode and add forced mode right after
modified_lines = []
for i, line in enumerate(lines):
    modified_lines.append(line)
    
    # After initial_mode is set, force it to webai
    if 'initial_mode = "webai"' in line or 'initial_mode = "g4f"' in line:
        # Add forced mode selection right after
        modified_lines.append('\n')
        modified_lines.append('    # === FORCE WEBAI MODE - BYPASS INPUT LISTENER ===\n')
        modified_lines.append('    print("🚀 Cookies detected → Forcing WebAI mode (no input required)")\n')
        modified_lines.append('    selected_mode = "webai"  # Force WebAI mode\n')
        modified_lines.append('    # === END FORCE ===\n')
        modified_lines.append('\n')

# Write back
with open('src/run.py', 'w', encoding='utf-8') as f:
    f.writelines(modified_lines)

print("✅ run.py modified to force WebAI mode automatically")
print("Restart server - it will start directly in WebAI mode")
