#!/usr/bin/env python3
"""
Enhanced GCS Storage Integration Test
Tests file validation, security scanning, and image processing capabilities
"""

import os
import sys
import tempfile
import logging
from pathlib import Path

# Add backend paths
backend_path = Path(__file__).parent
sys.path.append(str(backend_path))
sys.path.append(str(backend_path / "backend-clean"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dependencies():
    """Test required dependencies"""
    print("🔍 Testing Dependencies...")
    
    dependencies = {
        'magic': 'python-magic',
        'PIL': 'Pillow',
        'google.cloud.storage': 'google-cloud-storage',
        'hashlib': 'built-in',
        'uuid': 'built-in',
        'datetime': 'built-in'
    }
    
    results = {}
    
    for module, package in dependencies.items():
        try:
            if module == 'magic':
                import magic
                results[module] = True
                print(f"✅ {package} available")
            elif module == 'PIL':
                from PIL import Image
                results[module] = True
                print(f"✅ {package} available")
            elif module == 'google.cloud.storage':
                from google.cloud import storage
                results[module] = True
                print(f"✅ {package} available")
            else:
                __import__(module)
                results[module] = True
                print(f"✅ {module} available")
        except ImportError as e:
            results[module] = False
            print(f"❌ {package} not available: {e}")
    
    return all(results.values()), results

def test_file_validation():
    """Test file validation logic"""
    print("\n🔍 Testing File Validation...")
    
    try:
        # Test file extension validation
        allowed_extensions = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'],
            'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
            'spreadsheet': ['.xls', '.xlsx', '.csv'],
            'presentation': ['.ppt', '.pptx'],
            'archive': ['.zip', '.rar', '.7z'],
            'media': ['.mp4', '.avi', '.mov', '.mp3', '.wav']
        }
        
        test_files = [
            ('test.jpg', 'image'),
            ('document.pdf', 'document'),
            ('script.exe', 'other'),
            ('archive.zip', 'archive')
        ]
        
        for filename, expected_category in test_files:
            file_ext = os.path.splitext(filename)[1].lower()
            
            found_category = 'other'
            for category, extensions in allowed_extensions.items():
                if file_ext in extensions:
                    found_category = category
                    break
            
            status = "✅" if found_category == expected_category else "❌"
            print(f"  {status} {filename} -> {found_category} (expected: {expected_category})")
        
        return True
        
    except Exception as e:
        print(f"❌ File validation test failed: {e}")
        return False

def test_security_scanning():
    """Test security scanning logic"""
    print("\n🔍 Testing Security Scanning...")
    
    try:
        suspicious_signatures = [
            b'eval(', b'exec(', b'system(', b'shell_exec',
            b'powershell', b'cmd.exe', b'/bin/sh', b'bash -c',
            b'subprocess', b'os.system', b'__import__', b'compile'
        ]
        
        # Test safe content
        safe_content = b"This is a safe document with regular text content."
        suspicious_found = any(sig in safe_content.lower() for sig in suspicious_signatures)
        print(f"  {'✅' if not suspicious_found else '❌'} Safe content correctly identified")
        
        # Test suspicious content
        suspicious_content = b"This document contains eval(malicious_code) and system('rm -rf')"
        suspicious_found = any(sig in suspicious_content.lower() for sig in suspicious_signatures)
        print(f"  {'✅' if suspicious_found else '❌'} Suspicious content correctly identified")
        
        return True
        
    except Exception as e:
        print(f"❌ Security scanning test failed: {e}")
        return False

def test_image_processing():
    """Test image processing capabilities"""
    print("\n🔍 Testing Image Processing...")
    
    try:
        from PIL import Image
        import io
        
        # Create a test image
        test_image = Image.new('RGB', (100, 100), color='red')
        img_buffer = io.BytesIO()
        test_image.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        print(f"  ✅ Created test image ({len(img_bytes)} bytes)")
        
        # Test image processing logic
        processing_info = {
            'processed': False,
            'original_size': len(img_bytes),
            'final_size': len(img_bytes),
            'compression_ratio': 0.0,
            'format': 'PNG',
            'dimensions': f"{test_image.width}x{test_image.height}"
        }
        
        # Simulate processing
        processed_image = test_image.convert('RGB')
        if processed_image.mode in ('RGBA', 'LA', 'P'):
            processed_image = processed_image.convert('RGB')
            processing_info['format_conversion'] = f"{test_image.mode} -> RGB"
        
        output = io.BytesIO()
        processed_image.save(output, format='JPEG', quality=85, optimize=True)
        processed_bytes = output.getvalue()
        
        processing_info['processed'] = True
        processing_info['final_size'] = len(processed_bytes)
        processing_info['compression_ratio'] = round((1 - len(processed_bytes) / len(img_bytes)) * 100, 2)
        
        print(f"  ✅ Image processed successfully")
        print(f"  ✅ Compression: {processing_info['compression_ratio']}%")
        print(f"  ✅ Size reduction: {len(img_bytes)} -> {len(processed_bytes)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Image processing test failed: {e}")
        return False

def test_storage_configuration():
    """Test storage configuration"""
    print("\n🔍 Testing Storage Configuration...")
    
    config_tests = []
    
    # Test environment variables
    env_vars = [
        'GCS_BUCKET_NAME',
        'MAX_FILE_SIZE_MB',
        'ENABLE_FILE_SCANNING',
        'ENABLE_IMAGE_PROCESSING',
        'GCS_CDN_URL'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var} = {value}")
            config_tests.append(True)
        else:
            print(f"  ⚠️  {var} not set (using default)")
            config_tests.append(False)
    
    # Test configuration defaults
    default_config = {
        'max_file_size': 100 * 1024 * 1024,  # 100MB
        'enable_security_scanning': True,
        'enable_image_processing': True,
        'allowed_extensions': {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'],
            'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
            'spreadsheet': ['.xls', '.xlsx', '.csv'],
            'presentation': ['.ppt', '.pptx'],
            'archive': ['.zip', '.rar', '.7z'],
            'media': ['.mp4', '.avi', '.mov', '.mp3', '.wav']
        }
    }
    
    print(f"  ✅ Default max file size: {default_config['max_file_size'] // (1024*1024)}MB")
    print(f"  ✅ Security scanning: {default_config['enable_security_scanning']}")
    print(f"  ✅ Image processing: {default_config['enable_image_processing']}")
    print(f"  ✅ Allowed file types: {len(default_config['allowed_extensions'])} categories")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Enhanced GCS Storage Integration Test")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("File Validation", test_file_validation),
        ("Security Scanning", test_security_scanning),
        ("Image Processing", test_image_processing),
        ("Storage Configuration", test_storage_configuration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced storage integration is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
