#!/usr/bin/env python3
"""
Fix OCR System - Configure and test OCR properly
"""

import os
import subprocess
import sys
from pathlib import Path

def fix_tesseract_configuration():
    """Fix Tesseract OCR configuration"""
    
    print("🔧 FIXING TESSERACT OCR CONFIGURATION")
    print("=" * 50)
    
    # Check if Tesseract is installed
    try:
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        print(f"✅ Tesseract found: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Tesseract not found. Please install Tesseract OCR")
        return False
    
    # Find tessdata directory
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tessdata",
        r"C:\Program Files (x86)\Tesseract-OCR\tessdata",
        r"C:\Users\hp\scoop\apps\tesseract\current\tessdata",
        r"C:\Users\hp\scoop\persist\tesseract\tessdata"
    ]
    
    tessdata_path = None
    for path in possible_paths:
        if os.path.exists(path):
            tessdata_path = path
            print(f"✅ Found tessdata directory: {path}")
            break
    
    if not tessdata_path:
        print("❌ tessdata directory not found")
        return False
    
    # Check for English language data
    eng_file = os.path.join(tessdata_path, "eng.traineddata")
    if os.path.exists(eng_file):
        print(f"✅ English language data found: {eng_file}")
    else:
        print(f"❌ English language data not found at: {eng_file}")
        print("Please download English language data for Tesseract")
        return False
    
    # Set environment variable
    os.environ['TESSDATA_PREFIX'] = tessdata_path
    print(f"✅ Set TESSDATA_PREFIX to: {tessdata_path}")
    
    # Test Tesseract with the configuration
    try:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Test with a simple image
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # Create a test image with text
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            # Try to use a default font
            draw.text((10, 10), "TEST OCR SYSTEM", fill='black')
            draw.text((10, 50), "Business Document Sample", fill='black')
        except:
            # Fallback to simple text
            pass
        
        # Test OCR
        text = pytesseract.image_to_string(img, lang='eng')
        print(f"✅ OCR Test Result: \"{text.strip()}\"")
        
        if "TEST" in text.upper() or "OCR" in text.upper():
            print("✅ OCR system is working correctly!")
            return True
        else:
            print("⚠️ OCR test produced unexpected results")
            return False
            
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        return False

def create_working_ocr_test():
    """Create a working OCR test with proper configuration"""
    
    print("\n🧪 CREATING WORKING OCR TEST")
    print("=" * 50)
    
    # Test content that should work
    test_content = [
        {
            "url": "https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/eng.traineddata",
            "category": "language_data",
            "description": "English Language Data",
            "filename": "eng.traineddata"
        }
    ]
    
    return True

if __name__ == "__main__":
    success = fix_tesseract_configuration()
    
    if success:
        print("\n🎉 OCR SYSTEM FIXED SUCCESSFULLY!")
        print("You can now run comprehensive OCR tests")
    else:
        print("\n❌ OCR SYSTEM STILL NEEDS FIXING")
        print("Please install Tesseract and language data")
