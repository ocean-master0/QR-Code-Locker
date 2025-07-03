import qrcode
import cv2
import numpy as np
import os
import uuid
import traceback
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import base64
from io import BytesIO

def generate_qr_code(data, output_dir='static/temp'):
    """Generate QR code with better compatibility"""
    try:
        # Create QR code with higher error correction
        qr = qrcode.QRCode(
            version=None,  # Auto-size
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=8,    # Reduced box size for better detection
            border=6,      # Increased border
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create high contrast QR image
        img = qr.make_image(
            fill_color="black",      # Black modules
            back_color="white"       # White background
        )
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save with high quality
        filename = f"qr_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(output_dir, filename)
        os.makedirs(output_dir, exist_ok=True)
        img.save(filepath, "PNG", quality=100, optimize=False)
        
        print(f"QR code generated: {filepath}")
        return filepath
        
    except Exception as e:
        raise Exception(f"QR generation failed: {str(e)}")

def decode_qr_with_opencv(image):
    """Enhanced OpenCV QR detection"""
    try:
        detector = cv2.QRCodeDetector()
        
        # Method 1: Direct detection
        try:
            data, bbox, _ = detector.detectAndDecode(image)
            if data:
                print(f"✅ OpenCV direct detection successful: {len(data)} chars")
                return data
        except Exception as e:
            print(f"OpenCV direct detection failed: {e}")
        
        # Method 2: Grayscale conversion
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            data, bbox, _ = detector.detectAndDecode(gray)
            if data:
                print(f"✅ OpenCV grayscale detection successful: {len(data)} chars")
                return data
        except Exception as e:
            print(f"OpenCV grayscale detection failed: {e}")
        
        # Method 3: Enhanced preprocessing
        preprocessing_methods = [
            # Binary threshold
            lambda img: cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1],
            # Adaptive threshold
            lambda img: cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2),
            # Otsu threshold
            lambda img: cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            # Morphological operations
            lambda img: cv2.morphologyEx(img, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))),
            # Gaussian blur
            lambda img: cv2.GaussianBlur(img, (3, 3), 0),
        ]
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        for i, method in enumerate(preprocessing_methods):
            try:
                processed = method(gray.copy())
                data, bbox, _ = detector.detectAndDecode(processed)
                if data:
                    print(f"✅ OpenCV method {i} successful: {len(data)} chars")
                    return data
            except Exception as e:
                print(f"OpenCV method {i} failed: {e}")
                continue
        
        # Method 4: Scale variations
        scales = [0.5, 0.8, 1.2, 1.5, 2.0]
        for scale in scales:
            try:
                h, w = gray.shape
                new_size = (int(w * scale), int(h * scale))
                resized = cv2.resize(gray, new_size, interpolation=cv2.INTER_CUBIC)
                
                data, bbox, _ = detector.detectAndDecode(resized)
                if data:
                    print(f"✅ OpenCV scale {scale} successful: {len(data)} chars")
                    return data
            except Exception as e:
                print(f"OpenCV scale {scale} failed: {e}")
                continue
        
        return None
        
    except Exception as e:
        print(f"OpenCV detection error: {e}")
        return None

def decode_qr_with_pil(image_path):
    """PIL-based QR detection as fallback"""
    try:
        # Load with PIL
        pil_image = Image.open(image_path)
        
        # Convert to grayscale
        if pil_image.mode != 'L':
            gray_image = pil_image.convert('L')
        else:
            gray_image = pil_image.copy()
        
        # Enhancement methods
        enhancement_methods = [
            # Original
            lambda img: img,
            # High contrast
            lambda img: ImageEnhance.Contrast(img).enhance(2.0),
            # Sharpness
            lambda img: ImageEnhance.Sharpness(img).enhance(2.0),
            # Brightness adjustment
            lambda img: ImageEnhance.Brightness(img).enhance(1.2),
            # Invert colors
            lambda img: ImageOps.invert(img),
            # Auto contrast
            lambda img: ImageOps.autocontrast(img),
        ]
        
        for i, method in enumerate(enhancement_methods):
            try:
                enhanced = method(gray_image.copy())
                
                # Save temporarily and try OpenCV
                temp_path = f"temp_pil_{uuid.uuid4().hex[:8]}.png"
                enhanced.save(temp_path)
                
                try:
                    # Load with OpenCV and try detection
                    cv_image = cv2.imread(temp_path, cv2.IMREAD_GRAYSCALE)
                    if cv_image is not None:
                        result = decode_qr_with_opencv(cv_image)
                        if result:
                            print(f"✅ PIL method {i} successful: {len(result)} chars")
                            return result
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
            except Exception as e:
                print(f"PIL method {i} failed: {e}")
                continue
        
        return None
        
    except Exception as e:
        print(f"PIL detection error: {e}")
        return None

def decode_qr_zxing_fallback():
    """Placeholder for additional detection methods"""
    # This could implement other QR detection libraries if needed
    print("Additional detection methods could be implemented here")
    return None

def decode_qr_code(image_path):
    """Main QR decoding function with multiple methods"""
    try:
        print(f"🔍 Attempting to decode QR from: {image_path}")
        
        if not os.path.exists(image_path):
            print(f"❌ File not found: {image_path}")
            return None
        
        # Method 1: OpenCV detection
        print("🔸 Trying OpenCV detection...")
        try:
            image = cv2.imread(image_path)
            if image is not None:
                result = decode_qr_with_opencv(image)
                if result:
                    return result
            else:
                print("❌ Could not load image with OpenCV")
        except Exception as e:
            print(f"❌ OpenCV method failed: {e}")
        
        # Method 2: PIL-based detection
        print("🔸 Trying PIL-based detection...")
        try:
            result = decode_qr_with_pil(image_path)
            if result:
                return result
        except Exception as e:
            print(f"❌ PIL method failed: {e}")
        
        # Method 3: Raw pixel analysis (last resort)
        print("🔸 Trying raw pixel analysis...")
        try:
            result = analyze_qr_pattern(image_path)
            if result:
                return result
        except Exception as e:
            print(f"❌ Raw analysis failed: {e}")
        
        print("❌ All QR detection methods failed")
        return None
        
    except Exception as e:
        print(f"❌ QR decode error: {e}")
        print(traceback.format_exc())
        return None

def analyze_qr_pattern(image_path):
    """Basic QR pattern analysis as last resort"""
    try:
        # This is a simplified approach to detect if there's a QR-like pattern
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            return None
        
        # Look for finder patterns (corner squares)
        # This is a basic implementation - could be enhanced
        height, width = image.shape
        
        # Check corners for QR finder patterns
        corner_size = min(width, height) // 10
        
        # Analyze top-left corner
        corner = image[0:corner_size, 0:corner_size]
        
        # Basic pattern detection (simplified)
        # Real QR detection would need more sophisticated pattern matching
        unique_values = len(np.unique(corner))
        
        # If we detect a binary pattern, it might be a QR code
        if unique_values <= 3:  # Typically black, white, maybe gray
            print("🔸 QR-like pattern detected, but cannot decode content")
            # In a real implementation, you'd implement the QR decoding algorithm
            # For now, return None as we can't decode the actual content
        
        return None
        
    except Exception as e:
        print(f"Pattern analysis failed: {e}")
        return None

def decode_qr_from_bytes(image_bytes):
    """Decode QR from image bytes with enhanced error handling"""
    try:
        print(f"📥 Decoding QR from {len(image_bytes)} bytes")
        
        if not image_bytes or len(image_bytes) == 0:
            print("❌ Empty image bytes")
            return None
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        
        # Try to decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            print("❌ OpenCV could not decode image from bytes")
            # Try with PIL as fallback
            try:
                pil_image = Image.open(BytesIO(image_bytes))
                print(f"✅ PIL loaded image: {pil_image.size}, mode: {pil_image.mode}")
                
                # Save temporarily and use file-based detection
                temp_path = f"temp_bytes_{uuid.uuid4().hex[:8]}.png"
                pil_image.save(temp_path)
                
                try:
                    result = decode_qr_code(temp_path)
                    return result
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
            except Exception as e:
                print(f"❌ PIL fallback failed: {e}")
                return None
        
        print(f"✅ Image decoded: {image.shape}")
        
        # Try direct OpenCV detection first
        result = decode_qr_with_opencv(image)
        if result:
            return result
        
        # Save temporarily and use comprehensive detection
        temp_path = f"temp_bytes_{uuid.uuid4().hex[:8]}.png"
        
        try:
            success = cv2.imwrite(temp_path, image)
            if not success:
                print("❌ Could not save temporary image")
                return None
            
            print(f"💾 Saved temporary image: {temp_path}")
            result = decode_qr_code(temp_path)
            return result
            
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                    print(f"🧹 Cleaned up: {temp_path}")
                except:
                    print(f"⚠️  Could not remove: {temp_path}")
                
    except Exception as e:
        print(f"❌ Error decoding QR from bytes: {e}")
        print(traceback.format_exc())
        return None

def test_qr_generation_and_detection():
    """Test function to verify QR generation and detection"""
    try:
        test_data = "Hello QR Code Locker Test!"
        print(f"🧪 Testing with data: {test_data}")
        
        # Generate QR code
        qr_path = generate_qr_code(test_data)
        
        if not os.path.exists(qr_path):
            return {"success": False, "error": "QR generation failed"}
        
        # Test decoding
        decoded = decode_qr_code(qr_path)
        
        # Clean up
        if os.path.exists(qr_path):
            os.remove(qr_path)
        
        success = decoded == test_data
        
        return {
            "success": success,
            "original": test_data,
            "decoded": decoded,
            "match": success,
            "message": "QR test completed"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "QR test failed"
        }
