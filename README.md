# Studocu Document Capture Tool

A Python tool to capture documents from Studocu and convert them into clean, single-file PDFs. Automates screenshot capture while giving you control over login and verification steps.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

---

## Important Legal Notice

**Use this tool responsibly and ethically:**

- Only capture documents you have legal access to
- Respect copyright and intellectual property rights
- Follow Studocu's Terms of Service
- Use for personal study purposes only
- Do not redistribute copyrighted material
- IMPORTANT: If the document is 'premium', and some of the pages are blurred, this script doesn't works!

This tool is provided for educational purposes. The author is not responsible for misuse.

---

## Features

- **Automated Screenshot Capture** - Automatically captures all pages from a Studocu document
- **Manual Verification Support** - Pauses for you to handle login prompts or challenges
- **Clean Output** - Removes headers and footers from screenshots automatically
- **Single PDF Output** - Combines all pages into one high-quality PDF file
- **Persistent Login** - Remembers your login between sessions
- **High Resolution** - 300 DPI output for crisp, readable text

---

## Prerequisites

- **Windows** (can be adapted for macOS/Linux)
- **Python 3.8 or newer**
- **Google Chrome** installed
- **Internet connection**

---

## Quick Start

### Installation

```bash
# Install dependencies
pip install playwright pillow img2pdf

# Install Playwright browsers
playwright install chromium
```

### Usage

1. **Edit the script** - Set your document URL:
   ```python
   URL = "https://www.studocu.com/en/document/your-document"
   ```

2. **Run the script**:
   ```bash
   python studocu_capture.py
   ```

3. **Handle verification** if needed in the Chrome window

4. **Wait for completion** - PDF will be saved automatically

---

## Configuration

### Essential Settings

Edit these at the top of `studocu_capture.py`:

```python
# Your Studocu document URL
URL = "https://www.studocu.com/bg/document/..."

# Output filenames
OUTPUT_DIR = Path("my_document")        # Temp folder
OUTPUT_PDF = Path("my_document.pdf")    # Final PDF

# Chrome location (update if different)
CHROME_PATH = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
```


##  How It Works

### The Process

```
1. Launch Chrome with remote debugging
2. Navigate to your document URL  
3. Wait for manual verification (if needed)
4. Detect all pages in the viewer
5. Screenshot each page
6. Crop headers/footers
7. Combine into single PDF
```

### What You'll See

```
======================================================================
  Studocu Document Capture Tool
======================================================================

Step 1: Launching Chrome with remote debugging...
✓ Chrome started

Step 2: Capturing document pages...
✓ Document viewer loaded successfully
Found 15 pages to capture

  Capturing page 1/15... ✓
  Capturing page 2/15... ✓
  ...

Step 3: Processing images and creating PDF...
  Processed page_001.png
  Processed page_002.png
  ...

✓ Success! PDF saved as: my_document.pdf
  Total pages: 15
  File size: 12.3 MB
```

---

## Troubleshooting

### Chrome doesn't open

**Problem:** `FileNotFoundError: Chrome not found`

**Fix:** Update `CHROME_PATH` in the script
```python
# Find Chrome location:
# Windows: C:\Program Files\Google\Chrome\Application\chrome.exe
# Mac: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome  
# Linux: /usr/bin/google-chrome
```

### Can't connect to Chrome

**Problem:** `Failed to connect to Chrome on port 9222`

**Fix:**
1. Close all Chrome windows
2. Run script again
3. If still failing, change `PORT = 9222` to `9223`

### Document doesn't load

**Problem:** `Document viewer didn't load`

**Fix:**
- Check URL is correct
- Make sure you're logged into Studocu
- Try opening URL manually in the Chrome window first

### Login required every time

**Problem:** Chrome doesn't remember login

**Fix:** Don't delete `USER_DATA_DIR` folder between runs. Keep it to maintain sessions.

### Blurry PDF

**Problem:** Text isn't crisp

**Fix:** Increase quality settings
```python
PDF_DPI = 600              # Higher quality
VIEWPORT_WIDTH = 1600      # Larger screenshots
VIEWPORT_HEIGHT = 2000
```

### Headers/footers still visible

**Problem:** UI elements in screenshots

**Fix:** Adjust crop ratios
```python
TOP_CROP_RATIO = 0.12      # Crop more from top
BOTTOM_CROP_RATIO = 0.10   # Crop more from bottom
```

---

## Tips

### First Time Setup

1. **Run once to log in:**
   ```bash
   python studocu_capture.py
   ```
2. **Log into Studocu** in the Chrome window
3. **Close Chrome**
4. **Run again** - you'll stay logged in

### Multiple Documents

Create a simple loop:
```python
documents = [
    ("doc1", "https://studocu.com/document/1"),
    ("doc2", "https://studocu.com/document/2"),
]

for name, url in documents:
    URL = url
    OUTPUT_PDF = Path(f"{name}.pdf")
    # ... run capture
```

### Optimize File Size

Reduce PDF size:
```python
PDF_DPI = 150              # Lower quality
VIEWPORT_WIDTH = 1000      # Smaller screenshots
VIEWPORT_HEIGHT = 1300
```

---

## File Structure

```
studocu-capture/
│
├── studocu_capture.py          # Main script
├── README.md                   # Documentation
│
├── my_document/                # Created during run
│   ├── page_001.png           # Raw screenshots
│   ├── page_002.png
│   └── cropped/               # Cleaned images
│       ├── page_001.png
│       └── page_002.png
│
└── my_document.pdf            # Final output ✓
```

---

## Privacy

**What gets stored:**
- Chrome profile in `USER_DATA_DIR` (local only)
- Screenshots in `OUTPUT_DIR` (local only)
- PDF in current directory (local only)

**Nothing is uploaded anywhere.** All processing is local.

**Clean up:**
```bash
# Remove temp files
rm -rf my_document/

# Remove Chrome profile (clears login)
rm -rf C:\chrome_temp_bot
```

---

## FAQ

**Q: Is this legal?**  
A: The tool is legal. Your use must comply with copyright law and Terms of Service.

**Q: Why does Chrome stay open?**  
A: The script needs to connect to it. Close manually after completion.

**Q: Can I capture 100+ page documents?**  
A: Depends if the document is 'premium'

**Q: Does this work on Mac/Linux?**  
A: Yes, just update `CHROME_PATH` to your Chrome location.

**Q: Is my login safe?**  
A: Yes, it's stored locally just like normal Chrome usage.

**Q: Can I use this on other sites?**  
A: No, it's specifically designed for Studocu's viewer structure.

---

## Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

Ideas:
- GUI interface
- Progress bars
- Multi-threading
- Other platform support

---

## License

MIT License - See LICENSE file

---

## Disclaimer

This tool is for educational and personal use only. Users are responsible for:
- Complying with all applicable laws
- Respecting copyright
- Following Terms of Service
- Ethical use of captured content

The author assumes no liability for misuse.

---

**Made for students who want organized study materials** 📚
