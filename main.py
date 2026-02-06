import os
import time
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright
from PIL import Image
import img2pdf

# Chrome browser location (adjust for your system)
CHROME_PATH = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

# Temporary profile directory for Chrome (keeps you logged in)
USER_DATA_DIR = Path(r"C:\chrome_temp_bot")

# Port for remote debugging - usually don't need to change this
PORT = 9222

# The Studocu document URL you want to capture
URL = "https://www.studocu.com/bg/document/university-of-national-and-world-economy/osnovi-na-publichnata-administratsiya/public-finance-publichni-finansi/115470016"

# Where to save temporary screenshots
OUTPUT_DIR = Path("pub_finance")

# Where to save cleaned images (subfolder)
CROPPED_DIR = OUTPUT_DIR / "cropped"

# Final PDF filename
OUTPUT_PDF = Path("pub_finance.pdf")

# Screenshot settings - helps keep images consistent
VIEWPORT_WIDTH = 1225
VIEWPORT_HEIGHT = 1585

# Small buffer around each page capture (in pixels)
TOP_PADDING = 10
BOTTOM_PADDING = 10

# How much of the top/bottom to crop out (as a ratio of total height)
# These values remove headers and footers from the screenshots
TOP_CROP_RATIO = 0.08      # Remove top 8% (header area)
BOTTOM_CROP_RATIO = 0.07   # Remove bottom 7% (footer area)

# PDF quality settings
PDF_DPI = 300


def launch_chrome():
    if not CHROME_PATH.exists():
        raise FileNotFoundError(
            f"Chrome not found at: {CHROME_PATH}\n"
            f"Please update CHROME_PATH in the script to your Chrome location."
        )

    # Create the profile directory if it doesn't exist
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Build the command to launch Chrome
    command = [
        str(CHROME_PATH),
        f"--remote-debugging-port={PORT}",
        f"--user-data-dir={USER_DATA_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
    ]

    print(f"Starting Chrome from: {CHROME_PATH}")
    
    # Launch Chrome in the background
    subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Give Chrome a few seconds to fully start up
    time.sleep(3)


def remove_header_bar(page):
    print("Attempting to remove header bar...")
    
    try:
        # Run JavaScript to find and remove the header element
        page.evaluate("""
            const header = 
                document.querySelector('header.NewViewerTopbar_topbar__Xrfah') ||
                document.querySelector('header');
            
            if (header) {
                header.remove();
            }
        """)
        print("Header removed successfully")
        
    except Exception as e:
        print(f"Couldn't remove header (this is okay): {e}")


def capture_all_pages():
    # Make sure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        print("Connecting to Chrome...")
        
        try:
            browser = playwright.chromium.connect_over_cdp(f"http://localhost:{PORT}")
        except Exception as e:
            print(f"Failed to connect to Chrome on port {PORT} ")
            print(f"Make sure Chrome is running with remote debugging enabled ")
            print(f"Error: {e}")
            return 0

        # Use existing Chrome context or create new one
        if browser.contexts:
            context = browser.contexts[0]
        else:
            context = browser.new_context()

        # Use existing tab or open new one
        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()

        print(f"Navigating to: {URL}")
        page.goto(URL, wait_until="domcontentloaded")

        # Try to set consistent viewport size
        try:
            page.set_viewport_size({
                "width": VIEWPORT_WIDTH,
                "height": VIEWPORT_HEIGHT
            })
            page.evaluate(f"window.resizeTo({VIEWPORT_WIDTH}, {VIEWPORT_HEIGHT})")
        except Exception:
            pass

        print("  MANUAL VERIFICATION MAY BE REQUIRED")


        try:
            page.wait_for_selector('div[data-page-index]', state="visible", timeout=0)
            print("Document viewer loaded successfully")
        except Exception:
            print("Document viewer didn't load. The page may require login or the URL might be incorrect. ")
            browser.close()
            return 0

        # Remove header for cleaner screenshots
        remove_header_bar(page)

        # Scroll to bottom to trigger lazy loading of all pages
        print("Loading all pages...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000) 

        # Find all page elements
        page_elements = page.query_selector_all('div[data-page-index]')
        total_pages = len(page_elements)
        print(f"Found {total_pages} pages to capture\n")

        captured_count = 0
        
        for page_num, page_div in enumerate(page_elements, start=1):
            page_div.scroll_into_view_if_needed()
            page.wait_for_timeout(200) 

            # Get the position and size of this page element
            bounding_box = page_div.bounding_box()
            if not bounding_box:
                continue

            # Calculate screenshot area with padding
            screenshot_area = {
                "x": bounding_box["x"],
                "y": max(bounding_box["y"] - TOP_PADDING, 0),
                "width": bounding_box["width"],
                "height": bounding_box["height"] + TOP_PADDING + BOTTOM_PADDING,
            }

            # Skip if dimensions are invalid
            if screenshot_area["width"] <= 0 or screenshot_area["height"] <= 0:
                continue

            # Save screenshot
            output_file = OUTPUT_DIR / f"page_{page_num:03d}.png"
            print(f" Capturing page {page_num}/{total_pages}... ", end="", flush=True)
            
            page.screenshot(path=str(output_file), clip=screenshot_area)
            
            captured_count += 1

        print(f"Captured {captured_count} pages successfully")
        browser.close()

    return captured_count


def clean_and_create_pdf():
    # Make sure output directory exists
    CROPPED_DIR.mkdir(parents=True, exist_ok=True)

    # Get all screenshots, sorted by page number
    screenshot_files = sorted(OUTPUT_DIR.glob("page_*.png"))
    
    if not screenshot_files:
        print(f"No screenshots found in {OUTPUT_DIR}")
        return

    print(f"\nProcessing {len(screenshot_files)} pages...")
    
    cleaned_images = []

    for screenshot_path in screenshot_files:
        # Open the image
        img = Image.open(screenshot_path)
        width, height = img.size

        # Calculate how many pixels to crop from top and bottom
        top_crop_pixels = int(height * TOP_CROP_RATIO)
        bottom_crop_pixels = int(height * BOTTOM_CROP_RATIO)
        
        # Calculate the content area 
        content_height = max(1, height - top_crop_pixels - bottom_crop_pixels)

        # removing header and footer areas
        content = img.crop((
            0,                              # left
            top_crop_pixels,                # top
            width,                          # right
            top_crop_pixels + content_height  # bottom
        ))

        # Create a new white image with original dimensions
        # This keeps page sizes consistent in the final PDF
        clean_page = Image.new("RGB", (width, height), "white")
        
        # Paste the content back in the middle
        clean_page.paste(content, (0, top_crop_pixels))

        # Save the cleaned image
        output_path = CROPPED_DIR / screenshot_path.name
        clean_page.save(output_path)
        cleaned_images.append(str(output_path))

        print(f"Processed {screenshot_path.name}")

    # Create the PDF
    print("\nCreating PDF file...")
    
    with open(OUTPUT_PDF, "wb") as pdf_file:
        pdf_file.write(img2pdf.convert(cleaned_images, dpi=PDF_DPI))

    print(f"\nSuccess! PDF saved as: {OUTPUT_PDF}")
    print(f"Total pages: {len(cleaned_images)}")
    print(f"File size: {OUTPUT_PDF.stat().st_size / 1024 / 1024:.1f} MB")


def main():
    print("  Studocu Document Capture Tool")

    # Step 1: Launch Chrome
    print("Step 1: Launching Chrome with remote debugging...")
    launch_chrome()

    # Step 2: Capture screenshots
    print("\nStep 2: Capturing document pages...")
    pages_captured = capture_all_pages()
    
    if pages_captured == 0:
        print("\nNo pages were captured. Exiting.")
        return

    # Step 3: Process images and create PDF
    print("\nStep 3: Processing images and creating PDF...")
    clean_and_create_pdf()


if __name__ == "__main__":
    main()