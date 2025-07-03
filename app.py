from flask import Flask, request, render_template, jsonify, session
import os
import base64
import json
import traceback
import tempfile
import threading
import time
import uuid
from datetime import datetime, timedelta
from utils.crypto import encrypt_message, decrypt_message
from utils.qr_handler import generate_qr_code, decode_qr_code, decode_qr_from_bytes

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# ============== ZERO PERSISTENCE CONFIGURATION ==============
# Use system temp directory that gets cleaned automatically
app.config['TEMP_FOLDER'] = tempfile.gettempdir()
app.config['SESSION_PERMANENT'] = False  # Sessions expire when browser closes
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # 30 min max

# In-memory storage for temporary data (gets cleared on server restart)
temp_storage = {}
cleanup_times = {}

# ============== AUTO-CLEANUP FUNCTIONS ==============
def cleanup_temp_files():
    """Background thread to cleanup temporary files"""
    while True:
        try:
            current_time = time.time()
            files_to_delete = []
            
            # Find expired files
            for file_path, expire_time in cleanup_times.items():
                if current_time > expire_time:
                    files_to_delete.append(file_path)
            
            # Delete expired files
            for file_path in files_to_delete:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"🧹 Cleaned up: {file_path}")
                except:
                    pass
                finally:
                    cleanup_times.pop(file_path, None)
            
            # Clean expired sessions from memory
            expired_sessions = []
            for session_id, data in temp_storage.items():
                if current_time > data.get('expire_time', 0):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                temp_storage.pop(session_id, None)
                print(f"🧹 Cleaned session: {session_id[:8]}...")
            
            time.sleep(60)  # Run cleanup every minute
            
        except Exception as e:
            print(f"Cleanup error: {e}")
            time.sleep(60)

def schedule_file_cleanup(file_path, minutes=5):
    """Schedule a file for cleanup after specified minutes"""
    expire_time = time.time() + (minutes * 60)
    cleanup_times[file_path] = expire_time

def get_session_id():
    """Get or create session ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session.permanent = False  # Session expires when browser closes
    return session['session_id']

def store_temp_data(data, expire_minutes=5):
    """Store data temporarily in memory"""
    session_id = get_session_id()
    expire_time = time.time() + (expire_minutes * 60)
    
    temp_storage[session_id] = {
        'data': data,
        'expire_time': expire_time,
        'created_at': datetime.now().isoformat()
    }
    
    print(f"💾 Stored temp data for session: {session_id[:8]}... (expires in {expire_minutes}min)")

def get_temp_data():
    """Get temporary data for current session"""
    session_id = get_session_id()
    
    if session_id in temp_storage:
        data_entry = temp_storage[session_id]
        
        # Check if expired
        if time.time() > data_entry['expire_time']:
            temp_storage.pop(session_id, None)
            return None
        
        return data_entry['data']
    
    return None

def clear_session_data():
    """Clear all data for current session"""
    session_id = get_session_id()
    temp_storage.pop(session_id, None)
    session.clear()
    print(f"🧹 Cleared session data: {session_id[:8]}...")

# ============== ROUTES ==============
@app.route('/')
def index():
    """Landing page - clears any existing session data"""
    clear_session_data()  # Clear data on homepage visit
    return render_template('index.html')

@app.route('/encrypt')
def encrypt_page():
    """Encryption interface"""
    return render_template('encrypt.html')

@app.route('/decrypt')
def decrypt_page():
    """Decryption interface"""
    return render_template('decrypt.html')

@app.route('/api/clear-session', methods=['POST'])
def clear_session():
    """Manually clear session data"""
    clear_session_data()
    return jsonify({'success': True, 'message': 'Session cleared'})

@app.route('/api/encrypt', methods=['POST'])
def api_encrypt():
    """Encrypt message and generate QR code - NO PERMANENT STORAGE"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        message = data.get('message', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        if len(message) > 500:
            return jsonify({'error': 'Message too long (max 500 characters)'}), 400
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        print(f"🔐 Encrypting message (session: {get_session_id()[:8]}...)")
        
        # Encrypt message
        encrypted_data = encrypt_message(message, password)
        qr_data = json.dumps(encrypted_data)
        
        if len(qr_data) > 1500:
            return jsonify({'error': 'Data too large for QR code'}), 400
        
        # Generate QR code in temp directory
        temp_dir = tempfile.mkdtemp()  # Creates unique temp directory
        qr_image_path = generate_qr_code(qr_data, temp_dir)
        
        # Schedule cleanup of temp directory
        schedule_file_cleanup(qr_image_path, minutes=5)
        schedule_file_cleanup(temp_dir, minutes=5)
        
        # Read QR image and convert to base64
        with open(qr_image_path, 'rb') as img_file:
            qr_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Immediately delete the file after reading
        try:
            os.remove(qr_image_path)
            os.rmdir(temp_dir)
        except:
            pass  # Will be cleaned up by background thread anyway
        
        # Store encrypted data temporarily (expires in 30 minutes)
        store_temp_data({
            'encrypted_data': encrypted_data,
            'type': 'encryption'
        }, expire_minutes=30)
        
        print("✅ QR code generated (no permanent storage)")
        
        return jsonify({
            'success': True,
            'qr_code': f"data:image/png;base64,{qr_base64}",
            'encrypted_data': encrypted_data,
            'session_info': {
                'session_id': get_session_id()[:8] + '...',
                'expires_in': '30 minutes',
                'storage': 'temporary_memory_only'
            }
        })
        
    except Exception as e:
        print(f"❌ Encryption error: {e}")
        return jsonify({'error': 'Encryption failed'}), 500

@app.route('/api/decrypt', methods=['POST'])
def api_decrypt():
    """Decrypt message from QR code - NO PERMANENT STORAGE"""
    try:
        print(f"📥 Decrypt request (session: {get_session_id()[:8]}...)")
        
        # Handle file upload
        if request.files and 'qr_file' in request.files:
            qr_file = request.files['qr_file']
            password = request.form.get('password', '')
            
            if not qr_file or qr_file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not password:
                return jsonify({'error': 'Password is required'}), 400
            
            # Read file into memory (NO DISK STORAGE)
            file_data = qr_file.read()
            if len(file_data) == 0:
                return jsonify({'error': 'File is empty'}), 400
            
            print(f"📁 Processing file in memory: {len(file_data)} bytes")
            
            # Decode QR directly from memory
            qr_data = decode_qr_from_bytes(file_data)
            
            if not qr_data:
                return jsonify({
                    'error': 'Could not decode QR code. Please ensure the image contains a valid QR code generated by this application.'
                }), 400
            
        # Handle JSON data
        elif request.is_json:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data'}), 400
            
            qr_data = data.get('encrypted_data', '')
            password = data.get('password', '')
            
            if not password or not qr_data:
                return jsonify({'error': 'Password and encrypted data required'}), 400
        
        else:
            return jsonify({'error': 'Invalid request format'}), 400
        
        # Parse encrypted data
        try:
            encrypted_data = json.loads(qr_data) if isinstance(qr_data, str) else qr_data
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid encrypted data format'}), 400
        
        # Validate structure
        required_fields = ['kdf_salt', 'ciphertext', 'nonce', 'auth_tag']
        if not all(field in encrypted_data for field in required_fields):
            return jsonify({'error': 'Invalid encrypted data structure'}), 400
        
        # Decrypt message
        decrypted_message = decrypt_message(encrypted_data, password)
        
        # Store decryption result temporarily (expires in 5 minutes)
        store_temp_data({
            'decrypted_message': decrypted_message,
            'type': 'decryption'
        }, expire_minutes=5)
        
        print(f"✅ Message decrypted (temporary storage only)")
        
        return jsonify({
            'success': True,
            'message': decrypted_message,
            'session_info': {
                'session_id': get_session_id()[:8] + '...',
                'expires_in': '5 minutes',
                'storage': 'temporary_memory_only'
            }
        })
        
    except ValueError as e:
        if 'Decryption failed' in str(e):
            return jsonify({'error': 'Incorrect password or corrupted data'}), 400
        return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        print(f"❌ Decryption error: {e}")
        return jsonify({'error': 'Decryption failed'}), 500

@app.route('/api/status')
def api_status():
    """Get current session status"""
    session_id = get_session_id()
    temp_data = get_temp_data()
    
    return jsonify({
        'session_id': session_id[:8] + '...',
        'has_temp_data': temp_data is not None,
        'data_type': temp_data.get('type') if temp_data else None,
        'total_sessions': len(temp_storage),
        'temp_files_scheduled': len(cleanup_times),
        'storage_type': 'memory_only_no_persistence'
    })

# ============== ERROR HANDLERS ==============
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def not_found(e):
    clear_session_data()  # Clear data on 404
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(e):
    clear_session_data()  # Clear data on error
    return jsonify({'error': 'Internal server error'}), 500

# ============== STARTUP ==============
if __name__ == '__main__':
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_temp_files, daemon=True)
    cleanup_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
