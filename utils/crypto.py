from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib
import base64

def encrypt_message(message, password):
    """Encrypt message with AES-256-GCM"""
    try:
        # Generate salt
        kdf_salt = get_random_bytes(16)
        
        # Derive key
        key = hashlib.scrypt(
            password.encode('utf-8'), 
            salt=kdf_salt, 
            n=16384, r=8, p=1, dklen=32
        )
        
        # Encrypt
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, auth_tag = cipher.encrypt_and_digest(message.encode('utf-8'))
        
        return {
            'kdf_salt': base64.b64encode(kdf_salt).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'nonce': base64.b64encode(cipher.nonce).decode('utf-8'),
            'auth_tag': base64.b64encode(auth_tag).decode('utf-8')
        }
        
    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")

def decrypt_message(encrypted_data, password):
    """Decrypt message"""
    try:
        # Decode components
        kdf_salt = base64.b64decode(encrypted_data['kdf_salt'])
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        nonce = base64.b64decode(encrypted_data['nonce'])
        auth_tag = base64.b64decode(encrypted_data['auth_tag'])
        
        # Derive key
        key = hashlib.scrypt(
            password.encode('utf-8'),
            salt=kdf_salt,
            n=16384, r=8, p=1, dklen=32
        )
        
        # Decrypt
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, auth_tag)
        
        return plaintext.decode('utf-8')
        
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")
