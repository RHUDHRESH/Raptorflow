#!/usr/bin/env python3
"""
Working OCR Test - Downloads real content and tests OCR accuracy
Compares OCR results with known content to verify system performance
"""

import os
import requests
import json
from datetime import datetime
import time
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from typing import List, Dict, Any

class WorkingOCRTester:
    """Working OCR testing with knowledge verification"""
    
    def __init__(self):
        self.test_dir = "working_ocr_test"
        os.makedirs(self.test_dir, exist_ok=True)
        self.setup_ocr()
        
    def setup_ocr(self):
        """Setup OCR configuration"""
        try:
            # Set Tesseract path
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
            # Set tessdata prefix
            tessdata_path = r'C:\Program Files\Tesseract-OCR\tessdata'
            os.environ['TESSDATA_PREFIX'] = tessdata_path
            
            # Test OCR
            test_img = Image.new('RGB', (200, 50), color='white')
            draw = ImageDraw.Draw(test_img)
            draw.text((10, 10), "TEST", fill='black')
            
            result = pytesseract.image_to_string(test_img, lang='eng')
            print("✅ OCR system initialized successfully")
            
        except Exception as e:
            print(f"❌ OCR setup failed: {e}")
    
    def download_test_content(self) -> List[Dict[str, Any]]:
        """Download test content with known text for OCR verification"""
        
        # Test content with predictable text
        test_content = [
            {
                "url": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=800&h=600",
                "category": "business_document",
                "description": "Business Document with Text",
                "expected_keywords": ["business", "document", "text"],
                "filename": "business_doc.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=800&h=600",
                "category": "spreadsheet_data",
                "description": "Spreadsheet/Financial Data",
                "expected_keywords": ["data", "spreadsheet", "financial"],
                "filename": "spreadsheet.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1554224154-2603ffc5d8b2?w=800&h=600",
                "category": "legal_document",
                "description": "Legal Contract Document",
                "expected_keywords": ["legal", "contract", "document"],
                "filename": "legal_doc.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1560185007-c5ca9d2c014d?w=800&h=600",
                "category": "invoice_document",
                "description": "Invoice/Billing Document",
                "expected_keywords": ["invoice", "billing", "payment"],
                "filename": "invoice.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1554469384-e58e1667c219?w=800&h=600",
                "category": "report_document",
                "description": "Business Report Document",
                "expected_keywords": ["report", "business", "analysis"],
                "filename": "report.jpg"
            }
        ]
        
        print("🌐 DOWNLOADING TEST CONTENT FOR OCR VERIFICATION")
        print("=" * 60)
        
        downloaded_files = []
        
        for i, item in enumerate(test_content):
            try:
                print(f"\n📥 [{i+1}/{len(test_content)}] Downloading: {item['description']}")
                print(f"    Expected Keywords: {', '.join(item['expected_keywords'])}")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(item["url"], headers=headers, timeout=30)
                
                if response.status_code == 200:
                    content = response.content
                    
                    # Add timestamp to filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{item['category']}_{timestamp}_{item['filename']}"
                    filepath = os.path.join(self.test_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    
                    file_info = {
                        "filename": filename,
                        "filepath": filepath,
                        "size": len(content),
                        "category": item["category"],
                        "description": item["description"],
                        "expected_keywords": item["expected_keywords"],
                        "url": item["url"],
                        "success": True
                    }
                    
                    downloaded_files.append(file_info)
                    print(f"    ✅ Downloaded: {filename} ({len(content):,} bytes)")
                else:
                    print(f"    ❌ Failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
            
            # Add delay to avoid rate limiting
            time.sleep(1)
        
        return downloaded_files
    
    def create_test_documents(self) -> List[Dict[str, Any]]:
        """Create test documents with known content"""
        
        print("\n📝 CREATING TEST DOCUMENTS WITH KNOWN CONTENT")
        print("=" * 50)
        
        test_docs = []
        
        # Create a business letter
        img = Image.new('RGB', (800, 1000), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add business letter content
        business_text = [
            "BUSINESS LETTER",
            "",
            "Dear Mr. Smith,",
            "",
            "I am writing to inform you about our new business proposal.",
            "Our company offers comprehensive solutions for your needs.",
            "We have been in business for over 10 years.",
            "",
            "Key Benefits:",
            "- Cost effective solutions",
            "- Professional service",
            "- Quick turnaround time",
            "",
            "Please contact us at your earliest convenience.",
            "",
            "Sincerely,",
            "John Doe",
            "Business Manager",
            "ABC Corporation",
            "Phone: (555) 123-4567",
            "Email: john@abccorp.com"
        ]
        
        y_pos = 50
        for line in business_text:
            draw.text((50, y_pos), line, fill='black')
            y_pos += 30
        
        # Save business letter
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"business_letter_{timestamp}.png"
        filepath = os.path.join(self.test_dir, filename)
        img.save(filepath)
        
        test_docs.append({
            "filename": filename,
            "filepath": filepath,
            "category": "business_letter",
            "description": "Business Letter with Known Content",
            "expected_keywords": ["business", "letter", "proposal", "solutions", "corporation"],
            "success": True
        })
        
        print(f"✅ Created: {filename}")
        
        # Create a financial report
        img = Image.new('RGB', (800, 1000), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add financial report content
        financial_text = [
            "FINANCIAL REPORT",
            "Q4 2023 Results",
            "",
            "Revenue: $1,234,567",
            "Expenses: $890,123",
            "Net Profit: $344,444",
            "",
            "Revenue Breakdown:",
            "Product Sales: $800,000",
            "Services: $400,000",
            "Licensing: $34,567",
            "",
            "Expense Breakdown:",
            "Salaries: $500,000",
            "Operations: $200,000",
            "Marketing: $150,123",
            "Other: $40,000",
            "",
            "Key Metrics:",
            "Gross Margin: 67.8%",
            "Net Margin: 27.9%",
            "ROI: 145.6%"
        ]
        
        y_pos = 50
        for line in financial_text:
            draw.text((50, y_pos), line, fill='black')
            y_pos += 30
        
        # Save financial report
        filename = f"financial_report_{timestamp}.png"
        filepath = os.path.join(self.test_dir, filename)
        img.save(filepath)
        
        test_docs.append({
            "filename": filename,
            "filepath": filepath,
            "category": "financial_report",
            "description": "Financial Report with Numbers",
            "expected_keywords": ["financial", "report", "revenue", "profit", "margin"],
            "success": True
        })
        
        print(f"✅ Created: {filename}")
        
        # Create a technical document
        img = Image.new('RGB', (800, 1000), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add technical document content
        technical_text = [
            "TECHNICAL SPECIFICATION",
            "System Architecture Document",
            "",
            "Overview:",
            "This document describes the system architecture",
            "for our advanced OCR processing platform.",
            "",
            "Components:",
            "1. Image Processing Module",
            "2. Text Recognition Engine",
            "3. Data Validation System",
            "4. Output Generation",
            "",
            "Technical Requirements:",
            "- Python 3.8+",
            "- Tesseract OCR 5.5+",
            "- OpenCV 4.5+",
            "- PIL/Pillow",
            "",
            "Performance Metrics:",
            "Processing Speed: < 2 seconds per page",
            "Accuracy Rate: > 95%",
            "Supported Formats: PDF, JPG, PNG, TIFF"
        ]
        
        y_pos = 50
        for line in technical_text:
            draw.text((50, y_pos), line, fill='black')
            y_pos += 30
        
        # Save technical document
        filename = f"technical_spec_{timestamp}.png"
        filepath = os.path.join(self.test_dir, filename)
        img.save(filepath)
        
        test_docs.append({
            "filename": filename,
            "filepath": filepath,
            "category": "technical_document",
            "description": "Technical Specification Document",
            "expected_keywords": ["technical", "specification", "system", "architecture", "ocr"],
            "success": True
        })
        
        print(f"✅ Created: {filename}")
        
        return test_docs
    
    def extract_text_with_ocr(self, filepath: str) -> Dict[str, Any]:
        """Extract text using multiple OCR methods"""
        
        results = {
            "filepath": filepath,
            "methods": [],
            "best_result": None,
            "errors": []
        }
        
        try:
            # Load image
            image = Image.open(filepath)
            
            # Method 1: Basic OCR
            try:
                text = pytesseract.image_to_string(image, lang='eng')
                confidence = pytesseract.image_to_data(image, lang='eng', output_type=pytesseract.Output.DICT)
                avg_conf = sum([int(c) for c in confidence['conf'] if int(c) > 0]) / len(confidence['conf'])
                
                result = {
                    "method": "basic_ocr",
                    "text": text.strip(),
                    "confidence": avg_conf / 100,
                    "word_count": len(text.split()),
                    "char_count": len(text)
                }
                results["methods"].append(result)
                
            except Exception as e:
                results["errors"].append(f"Basic OCR failed: {e}")
            
            # Method 2: Preprocessed OCR
            try:
                # Convert to OpenCV
                cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Convert to grayscale
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
                
                # Apply threshold
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                # Convert back to PIL
                thresh_pil = Image.fromarray(thresh)
                
                text = pytesseract.image_to_string(thresh_pil, lang='eng')
                confidence = pytesseract.image_to_data(thresh_pil, lang='eng', output_type=pytesseract.Output.DICT)
                avg_conf = sum([int(c) for c in confidence['conf'] if int(c) > 0]) / len(confidence['conf'])
                
                result = {
                    "method": "preprocessed_ocr",
                    "text": text.strip(),
                    "confidence": avg_conf / 100,
                    "word_count": len(text.split()),
                    "char_count": len(text)
                }
                results["methods"].append(result)
                
            except Exception as e:
                results["errors"].append(f"Preprocessed OCR failed: {e}")
            
            # Method 3: Enhanced OCR with contrast
            try:
                # Enhance contrast
                enhancer = ImageEnhance.Contrast(image)
                enhanced = enhancer.enhance(2.0)
                
                text = pytesseract.image_to_string(enhanced, lang='eng')
                confidence = pytesseract.image_to_data(enhanced, lang='eng', output_type=pytesseract.Output.DICT)
                avg_conf = sum([int(c) for c in confidence['conf'] if int(c) > 0]) / len(confidence['conf'])
                
                result = {
                    "method": "enhanced_ocr",
                    "text": text.strip(),
                    "confidence": avg_conf / 100,
                    "word_count": len(text.split()),
                    "char_count": len(text)
                }
                results["methods"].append(result)
                
            except Exception as e:
                results["errors"].append(f"Enhanced OCR failed: {e}")
            
            # Select best result
            if results["methods"]:
                results["best_result"] = max(results["methods"], key=lambda x: x["confidence"])
            
        except Exception as e:
            results["errors"].append(f"Image processing failed: {e}")
        
        return results
    
    def verify_ocr_accuracy(self, file_info: Dict[str, Any], ocr_results: Dict[str, Any]) -> Dict[str, Any]:
        """Verify OCR accuracy against expected content"""
        
        verification = {
            "file_info": file_info,
            "ocr_results": ocr_results,
            "expected_keywords": file_info.get("expected_keywords", []),
            "accuracy_assessment": "unknown",
            "keyword_matches": [],
            "missing_keywords": [],
            "confidence_score": 0.0,
            "is_working": False,
            "sample_text": "",
            "assessment_details": {}
        }
        
        try:
            if ocr_results["best_result"]:
                extracted_text = ocr_results["best_result"]["text"].lower()
                confidence = ocr_results["best_result"]["confidence"]
                verification["confidence_score"] = confidence
                verification["sample_text"] = extracted_text[:200]
                
                # Check for keyword matches
                expected_keywords = [kw.lower() for kw in verification["expected_keywords"]]
                matches = []
                missing = []
                
                for keyword in expected_keywords:
                    if keyword in extracted_text:
                        matches.append(keyword)
                    else:
                        missing.append(keyword)
                
                verification["keyword_matches"] = matches
                verification["missing_keywords"] = missing
                
                # Calculate accuracy
                if expected_keywords:
                    keyword_accuracy = len(matches) / len(expected_keywords)
                else:
                    keyword_accuracy = 0.0
                
                # Assess if OCR is working
                if confidence >= 0.7 and keyword_accuracy >= 0.5:
                    verification["is_working"] = True
                    verification["accuracy_assessment"] = "WORKING_WELL"
                elif confidence >= 0.5 and keyword_accuracy >= 0.3:
                    verification["is_working"] = True
                    verification["accuracy_assessment"] = "WORKING_MODERATELY"
                elif confidence >= 0.3 and len(extracted_text.strip()) > 10:
                    verification["is_working"] = True
                    verification["accuracy_assessment"] = "WORKING_POORLY"
                else:
                    verification["is_working"] = False
                    verification["accuracy_assessment"] = "NOT_WORKING"
                
                verification["assessment_details"] = {
                    "confidence": confidence,
                    "keyword_accuracy": keyword_accuracy,
                    "text_length": len(extracted_text),
                    "methods_tried": len(ocr_results["methods"])
                }
            else:
                verification["accuracy_assessment"] = "NO_OCR_RESULTS"
                verification["is_working"] = False
                
        except Exception as e:
            verification["accuracy_assessment"] = f"VERIFICATION_ERROR: {e}"
            verification["is_working"] = False
        
        return verification
    
    def run_comprehensive_test(self):
        """Run comprehensive OCR testing"""
        
        # Download content
        downloaded_files = self.download_test_content()
        
        # Create test documents
        created_docs = self.create_test_documents()
        
        # Combine all test files
        all_test_files = downloaded_files + created_docs
        
        if not all_test_files:
            print("❌ No files available for testing")
            return
        
        print(f"\n🧪 RUNNING COMPREHENSIVE OCR TESTING")
        print("=" * 60)
        
        test_results = []
        
        for file_info in all_test_files:
            print(f"\n🔍 Testing: {file_info['description']}")
            print(f"   File: {file_info['filename']}")
            print(f"   Expected Keywords: {', '.join(file_info['expected_keywords'])}")
            
            # Extract text using OCR
            ocr_results = self.extract_text_with_ocr(file_info["filepath"])
            
            # Verify accuracy
            verification = self.verify_ocr_accuracy(file_info, ocr_results)
            
            test_results.append(verification)
            
            # Display results
            if ocr_results["best_result"]:
                best_result = ocr_results["best_result"]
                method = best_result["method"]
                confidence = best_result["confidence"]
                word_count = best_result["word_count"]
                
                print(f"   ✅ Best Method: {method}")
                print(f"   📊 Confidence: {confidence:.1%}")
                print(f"   📝 Words Found: {word_count}")
                
                # Show verification results
                assessment = verification["accuracy_assessment"]
                print(f"   🎯 Assessment: {assessment}")
                
                if verification["keyword_matches"]:
                    print(f"   ✅ Keywords Found: {', '.join(verification['keyword_matches'])}")
                
                if verification["missing_keywords"]:
                    print(f"   ❌ Keywords Missing: {', '.join(verification['missing_keywords'])}")
                
                # Show sample text
                sample = verification["sample_text"]
                if sample:
                    print(f"   📄 Sample Text: \"{sample}...\"")
            else:
                print(f"   ❌ No OCR results obtained")
                if verification["errors"]:
                    for error in verification["errors"]:
                        print(f"   ❌ Error: {error}")
        
        # Generate comprehensive report
        self.generate_test_report(test_results)
        
        return test_results
    
    def generate_test_report(self, test_results: List[Dict[str, Any]]):
        """Generate comprehensive test report"""
        
        print(f"\n📊 COMPREHENSIVE OCR TEST REPORT")
        print("=" * 60)
        
        # Summary statistics
        total_tests = len(test_results)
        working_tests = sum(1 for r in test_results if r["is_working"])
        failed_tests = total_tests - working_tests
        
        working_rate = working_tests / total_tests * 100 if total_tests > 0 else 0
        
        print(f"📈 SUMMARY STATISTICS")
        print(f"   Total Tests: {total_tests}")
        print(f"   Working OCR: {working_tests} ({working_rate:.1f}%)")
        print(f"   Failed OCR: {failed_tests}")
        
        # Assessment breakdown
        print(f"\n🎯 OCR PERFORMANCE BREAKDOWN")
        assessments = {}
        for result in test_results:
            assessment = result["accuracy_assessment"]
            if assessment not in assessments:
                assessments[assessment] = 0
            assessments[assessment] += 1
        
        for assessment, count in assessments.items():
            percentage = count / total_tests * 100 if total_tests > 0 else 0
            print(f"   {assessment}: {count} ({percentage:.1f}%)")
        
        # Category breakdown
        print(f"\n📂 CATEGORY PERFORMANCE")
        categories = {}
        for result in test_results:
            category = result["file_info"]["category"]
            if category not in categories:
                categories[category] = {"total": 0, "working": 0}
            categories[category]["total"] += 1
            if result["is_working"]:
                categories[category]["working"] += 1
        
        for category, stats in categories.items():
            rate = stats["working"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"   {category}: {stats['working']}/{stats['total']} ({rate:.1f}%)")
        
        # Method performance
        print(f"\n🔧 OCR METHOD PERFORMANCE")
        methods = {}
        for result in test_results:
            if result["ocr_results"]["best_result"]:
                method = result["ocr_results"]["best_result"]["method"]
                if method not in methods:
                    methods[method] = {"total": 0, "confidence_sum": 0}
                methods[method]["total"] += 1
                methods[method]["confidence_sum"] += result["ocr_results"]["best_result"]["confidence"]
        
        for method, stats in methods.items():
            avg_confidence = stats["confidence_sum"] / stats["total"] if stats["total"] > 0 else 0
            print(f"   {method}: {stats['total']} uses, avg confidence: {avg_confidence:.1%}")
        
        # Save detailed results
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "working_tests": working_tests,
                "failed_tests": failed_tests,
                "working_rate": working_rate
            },
            "assessment_breakdown": assessments,
            "category_performance": categories,
            "method_performance": methods,
            "detailed_results": test_results
        }
        
        with open('working_ocr_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: working_ocr_test_report.json")
        
        # Overall assessment
        if working_rate >= 80:
            print(f"\n🎉 OCR SYSTEM STATUS: EXCELLENT ✅")
            print("OCR is working well and accurately extracting text")
        elif working_rate >= 60:
            print(f"\n✅ OCR SYSTEM STATUS: GOOD ✅")
            print("OCR is working with reasonable accuracy")
        elif working_rate >= 40:
            print(f"\n⚠️  OCR SYSTEM STATUS: MODERATE ⚠️")
            print("OCR is working but with limited accuracy")
        else:
            print(f"\n❌ OCR SYSTEM STATUS: NEEDS IMPROVEMENT ❌")
            print("OCR is not working properly")

def main():
    """Main execution"""
    print("🧪 WORKING OCR TESTING SYSTEM")
    print("=" * 50)
    print("Testing OCR accuracy on real and created content...")
    
    tester = WorkingOCRTester()
    results = tester.run_comprehensive_test()
    
    print(f"\n🏁 TESTING COMPLETE")
    print(f"Results: {len(results)} files tested")

if __name__ == "__main__":
    main()
