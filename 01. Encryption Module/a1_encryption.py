"""
Module 1: Encryption
Author: Member A
Description: AES-256 encryption/decryption with PBKDF2 key derivation
Dependencies: pycryptodome (install: pip install pycryptodome)

Functions:
- encrypt_message(plaintext: str, password: str) → (ciphertext: bytes, salt: bytes, iv: bytes)
- decrypt_message(ciphertext: bytes, password: str, salt: bytes, iv: bytes) → plaintext: str
"""

import os
import secrets
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256


def encrypt_message(plaintext: str, password: str) -> tuple[bytes, bytes, bytes]:
    """
    Encrypts plaintext using AES-256-CBC with PBKDF2 key derivation.
    
    Args:
        plaintext (str): Message to encrypt
        password (str): User password for key derivation
        
    Returns:
        tuple: (ciphertext: bytes, salt: bytes, iv: bytes)
    """
    try:
        # Convert plaintext to bytes
        data = plaintext.encode('utf-8')
        
        # Generate random 16-byte salt and IV
        salt = secrets.token_bytes(16)
        iv = secrets.token_bytes(16)
        
        # Derive 32-byte AES-256 key using PBKDF2
        key = PBKDF2(
            password.encode('utf-8'),
            salt,
            dkLen=32,  # 256 bits
            count=100000,  # 100k iterations
            hmac_hash_module=SHA256
        )
        
        # Create AES cipher in CBC mode
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Pad data and encrypt
        padded_data = pad(data, AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        
        return ciphertext, salt, iv
        
    except Exception as e:
        raise RuntimeError(f"Encryption failed: {str(e)}")


def decrypt_message(ciphertext: bytes, password: str, salt: bytes, iv: bytes) -> str:
    """
    Decrypts ciphertext using AES-256-CBC with PBKDF2 key derivation.
    
    Args:
        ciphertext (bytes): Encrypted data
        password (str): User password for key derivation
        salt (bytes): 16-byte salt used in encryption
        iv (bytes): 16-byte initialization vector
        
    Returns:
        str: Decrypted plaintext message
    """
    try:
        # Derive the same key using password and salt
        key = PBKDF2(
            password.encode('utf-8'),
            salt,
            dkLen=32,  # 256 bits
            count=100000,  # 100k iterations
            hmac_hash_module=SHA256
        )
        
        # Create AES cipher in CBC mode
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Decrypt and unpad
        padded_data = cipher.decrypt(ciphertext)
        data = unpad(padded_data, AES.block_size)
        
        # Convert back to string
        return data.decode('utf-8')
        
    except Exception as e:
        raise RuntimeError(f"Decryption failed: {str(e)}")


def test_encryption_module():
    """Test function to verify encryption/decryption works correctly"""
    test_cases = [
        "",  # Empty string
        "Hello",  # Short string
        "This is a longer test message with special characters: !@#$%^&*()",  # Long with special chars
        "Ω≈ç√∫˜µ≤≥÷",  # Unicode characters
        "A" * 1000,  # Very long string
        "Line1\nLine2\nLine3",  # Multi-line
        "Tab\tSeparated\tText",  # Tabs
        "Password123!",  # Password-like
        "JSON: {\"key\": \"value\", \"number\": 42}",  # JSON-like
        "SQL: SELECT * FROM users WHERE id = 1;"  # SQL-like
    ]
    
    password = "test_password_123"
    
    print("=== Module 1: Encryption Tests ===")
    print(f"Testing {len(test_cases)} test cases...")
    
    for i, plaintext in enumerate(test_cases, 1):
        try:
            # Encrypt
            ciphertext, salt, iv = encrypt_message(plaintext, password)
            
            # Decrypt
            decrypted = decrypt_message(ciphertext, password, salt, iv)
            
            # Verify round-trip
            assert decrypted == plaintext, f"Round-trip failed for test case {i}"
            
            print(f"✅ Test {i:2d}: {'Empty string' if not plaintext else plaintext[:50]+'...' if len(plaintext) > 50 else plaintext}")
            
        except Exception as e:
            print(f"❌ Test {i:2d}: FAILED - {str(e)}")
            return False
    
    # Test wrong password
    try:
        ciphertext, salt, iv = encrypt_message("test", "correct_password")
        decrypt_message(ciphertext, "wrong_password", salt, iv)
        print("❌ Wrong password test: FAILED - Should have raised exception")
        return False
    except:
        print("✅ Wrong password test: PASSED - Correctly rejected wrong password")
    
    print(f"✅ All encryption tests PASSED! Module 1 ready.")
    return True


if __name__ == "__main__":
    test_encryption_module()