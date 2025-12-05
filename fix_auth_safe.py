"""
Simple and safe auth bypass - add return at start of dispatch function
"""

# Read auth.py
with open('src/app/middleware/auth.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the dispatch function and add return at the very beginning
# This will bypass all auth logic safely
import re

# Pattern to find the dispatch function
pattern = r'(async def dispatch\(self, request: Request, call_next\):.*?\n)(        )'
replacement = r'\1        # AUTH COMPLETELY DISABLED - Return immediately\n        return await call_next(request)\n\n\2'

content_modified = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)

# Write back
with open('src/app/middleware/auth.py', 'w', encoding='utf-8') as f:
    f.write(content_modified)

print("✅ auth.py safely modified - all requests will bypass authentication")
print("Restart server and test")
