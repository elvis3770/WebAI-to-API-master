"""
Extract Gemini cookies from browser automatically
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.utils.browser import get_cookie_from_browser
from app.config import CONFIG
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    print("\n" + "="*70)
    print("  GEMINI COOKIE EXTRACTOR")
    print("="*70)
    
    # Get browser from config - handle dict properly
    try:
        browser_config = CONFIG.get("Browser", {})
        if isinstance(browser_config, dict):
            browser_name = browser_config.get("name", "chrome")
        else:
            browser_name = "chrome"
    except:
        browser_name = "chrome"
    
    browser_name = str(browser_name).lower()
    
    print(f"\nBrowser configured: {browser_name}")
    print(f"\nIMPORTANT: Make sure you are logged into Gemini at:")
    print(f"  https://gemini.google.com/app")
    print(f"\nAttempting to extract cookies from {browser_name}...")
    print("-" * 70)
    
    try:
        # Extract cookies
        result = get_cookie_from_browser("gemini")
        
        if result:
            secure_1psid, secure_1psidts = result
            
            print("\n" + "="*70)
            print("  SUCCESS! Cookies extracted")
            print("="*70)
            
            print(f"\n__Secure-1PSID (length: {len(secure_1psid)}):")
            print(f"  {secure_1psid[:50]}...")
            
            print(f"\n__Secure-1PSIDTS (length: {len(secure_1psidts)}):")
            print(f"  {secure_1psidts[:50]}...")
            
            # Save to .env format
            env_file = os.path.join(os.path.dirname(__file__), '.env')
            
            print(f"\n" + "-"*70)
            print("Add these lines to your .env file:")
            print("-"*70)
            print(f"\nGEMINI_COOKIE_1PSID={secure_1psid}")
            print(f"GEMINI_COOKIE_1PSIDTS={secure_1psidts}")
            print(f"USE_G4F=false")
            print(f"COOKIE_AUTO_REFRESH=true")
            
            # Optionally save to file
            print(f"\n" + "-"*70)
            response = input("\nSave to .env automatically? (y/n): ").strip().lower()
            
            if response == 'y':
                # Read existing .env
                env_lines = []
                if os.path.exists(env_file):
                    with open(env_file, 'r') as f:
                        env_lines = f.readlines()
                
                # Remove old cookie lines
                env_lines = [line for line in env_lines if not any(
                    key in line for key in ['GEMINI_COOKIE_1PSID', 'GEMINI_COOKIE_1PSIDTS', 'USE_G4F', 'COOKIE_AUTO_REFRESH']
                )]
                
                # Add new cookie lines
                env_lines.append('\n# Gemini Cookie Authentication\n')
                env_lines.append(f'GEMINI_COOKIE_1PSID={secure_1psid}\n')
                env_lines.append(f'GEMINI_COOKIE_1PSIDTS={secure_1psidts}\n')
                env_lines.append('USE_G4F=false\n')
                env_lines.append('COOKIE_AUTO_REFRESH=true\n')
                
                # Write back
                with open(env_file, 'w') as f:
                    f.writelines(env_lines)
                
                print(f"\n✅ Cookies saved to {env_file}")
                print(f"\nNext steps:")
                print(f"  1. Restart the server (or press '1' in the running terminal)")
                print(f"  2. Test with: curl http://localhost:6969/v1/chat/completions")
            else:
                print(f"\n⏭️  Skipped saving. Copy the lines above to your .env manually.")
            
            print("\n" + "="*70)
            
        else:
            print("\n" + "="*70)
            print("  FAILED to extract cookies")
            print("="*70)
            print(f"\nPossible reasons:")
            print(f"  1. Not logged into Gemini (visit https://gemini.google.com/app)")
            print(f"  2. Browser not supported or not configured correctly")
            print(f"  3. Cookies are encrypted (Windows issue)")
            print(f"\nFallback: Extract cookies manually:")
            print(f"  1. Open https://gemini.google.com/app")
            print(f"  2. Press F12 → Application → Cookies")
            print(f"  3. Copy __Secure-1PSID and __Secure-1PSIDTS values")
            print(f"  4. Add to .env file")
            print("\n" + "="*70)
            
    except Exception as e:
        logger.error(f"Error extracting cookies: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print(f"\nTry manual extraction instead (see COOKIE_GUIDE.py)")

if __name__ == "__main__":
    main()
