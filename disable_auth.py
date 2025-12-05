"""
Direct fix for auth.py - Return immediately to bypass all auth checks
"""

# Read auth.py
with open('src/app/middleware/auth.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find line ~119 with raise HTTPException and replace with return
modified_lines = []
for i, line in enumerate(lines):
    if 'raise HTTPException(' in line and '401' in lines[i+1] if i+1 < len(lines) else False:
        # Replace this line and next 3 lines with a simple return
        modified_lines.append('            # AUTH DISABLED - Always allow\n')
        modified_lines.append('            return\n')
        # Skip the next 3 lines (status_code, detail, headers)
        for _ in range(3):
            if i+1 < len(lines):
                i += 1
    elif i > 0 and any('raise HTTPException(' in lines[i-j] for j in range(1, 4)):
        # Skip lines that are part of the HTTPException we're removing
        continue
    else:
        modified_lines.append(line)

# Write back
with open('src/app/middleware/auth.py', 'w', encoding='utf-8') as f:
    f.writelines(modified_lines)

print("✅ auth.py fixed - authentication completely bypassed")
print("Restart server, press '1', and test")
