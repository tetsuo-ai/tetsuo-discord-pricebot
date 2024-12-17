from playwright.sync_api import sync_playwright
import time
import os

class CloudflareSession:
    def __init__(self):
        self.cf_cookies = [
            {
                "name": "cf_clearance",
                "value": "0mBg5GJTKnBffTGYbk3IsZ.XYsk5f4bPTW2m7M73A44-1734386419-1.2.1.1-gfMuswlWrgsh0D.WAX0jH00y316mimWSZ4EnnXNSq0LWI5WuFNHdhlnV1mSzLr1Cxytd5oebnC5MWc.C2FLgnEdnAzzIsm5VIPFHDsTCbMj4PdA473ph7HfK3.2rGSOM2_gmQwSrxQa4PLF8odRWPbswmv1g6yFfNDNCcF98DjU8Bn1Fri4gkqu18q4OEqXPd55353leKq5NxCHZmuS_8ZPPEQakV_jp5WJ_klmTNT4PCRXDuxskyQipcE6A8tyU5cisUo3g4vPyPoKmukDSqk.JN25sFo31Do5BIgTZzXWFnTc8L59HOPRxOLwPkocwyqlNJGSw56EpYT6R9AGBC4JbaNyXqMRwTPAEl5X5pU_dqrONDo3OqL.0PY3kCJQ1XERvYf6N4WofgPlapRCeV8G5mZts64qun3CgbWdbQRcu6uvwSGY6deij0jM.jsx_",
                "domain": ".dexscreener.com",
                "path": "/"
            }
        ]
        
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.9',
            'upgrade-insecure-requests': '1'
        }

def capture_chart(token_type: str = 'tetsuo'):
    """
    Capture chart for specified token
    
    Args:
        token_type (str): Token to capture chart for ('tetsuo' or 'sol')
    
    Returns:
        str: Path to saved screenshot or None if error
    """
    # URLs for different tokens
    urls = {
        'tetsuo': "https://dexscreener.com/solana/2kb3i5ulkhucjuwq3poxhpuggqbwywttk5eg9e5wnlg6",
        'sol': "https://dexscreener.com/osmosis/1960"  # Using your SOL pair from bot.py
    }
    
    if token_type.lower() not in urls:
        print(f"Unsupported token type: {token_type}")
        return None
        
    session = CloudflareSession()
    url = urls[token_type.lower()]
    
    with sync_playwright() as p:
        try:
            print(f"\nStarting chart capture for {token_type.upper()}...")
            
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = browser.new_context(
                extra_http_headers=session.headers,
                viewport={'width': 1920, 'height': 1080},
                screen={'width': 1920, 'height': 1080}
            )
            
            context.add_cookies(session.cf_cookies)
            page = context.new_page()
            
            print("\nAccessing page...")
            response = page.goto(url, wait_until='networkidle', timeout=30000)
            print(f"Response status: {response.status}")
            
            # Wait for initial page load
            time.sleep(5)
            
            # Find iframe with dynamic name
            iframe = page.wait_for_selector("iframe[name^='tradingview_']")
            frame = iframe.content_frame()
            
            print("Setting 1h timeframe...")
            frame.get_by_role("radio", name="1 hour").click()
            
            # Wait for chart update
            time.sleep(2)
            
            print("Taking screenshot...")
            os.makedirs("screenshots", exist_ok=True)
            
            # Use static filename based on token
            screenshot_path = f"screenshots/{token_type.lower()}_chart.png"
            
            # Get the chart widget container and take screenshot
            chart_widget = frame.locator(".chart-widget").first
            chart_widget.screenshot(path=screenshot_path)
            
            print(f"✅ Screenshot saved to: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            print(f"Error during capture: {str(e)}")
            return None
        finally:
            browser.close()

if __name__ == "__main__":
    # Example usage
    capture_chart('tetsuo')  # Will save as tetsuo_chart.png
    # capture_chart('sol')   # Will save as sol_chart.png