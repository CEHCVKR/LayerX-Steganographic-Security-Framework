"""
Module 2: Key Management
Author: Member A
Description: AES key derivation and steganography key generation/storage
Dependencies: secrets, json

Functions:
- derive_aes_key(password: str, salt: bytes) → bytes (32-byte AES-256 key)
- generate_stego_key() → bytes (32 random bytes for steganography)
- KeyManager class for in-memory key storage and encrypted file persistence
"""

import os
import json
import secrets
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from typing import Dict, Optional
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from a1_encryption import encrypt_message, decrypt_message


def derive_aes_key(password: str, salt: bytes) -> bytes:
    """
    Derive 32-byte AES-256 key from password and salt using PBKDF2.
    
    Args:
        password (str): User password
        salt (bytes): 16-byte random salt
        
    Returns:
        bytes: 32-byte AES-256 key (deterministic for same password+salt)
    """
    return PBKDF2(
        password.encode('utf-8'),
        salt,
        dkLen=32,  # 256 bits
        count=100000,  # 100k iterations for security
        hmac_hash_module=SHA256
    )


def generate_stego_key() -> bytes:
    """
    Generate cryptographically secure 32-byte steganography key.
    
    Returns:
        bytes: 32 random bytes for steganography operations
    """
    return secrets.token_bytes(32)


class KeyManager:
    """
    Manages AES and steganography keys in memory with encrypted file persistence.
    """
    
    def __init__(self):
        self.keys: Dict[str, bytes] = {}
        self._master_password: Optional[str] = None
    
    def set_aes_key(self, password: str, salt: bytes) -> bytes:
        """
        Set AES key by deriving from password and salt.
        
        Args:
            password (str): User password
            salt (bytes): Salt for key derivation
            
        Returns:
            bytes: The derived AES key
        """
        key = derive_aes_key(password, salt)
        self.keys['aes'] = key
        return key
    
    def set_stego_key(self, key: Optional[bytes] = None) -> bytes:
        """
        Set steganography key (generate new if not provided).
        
        Args:
            key (bytes, optional): Existing stego key, or None to generate new
            
        Returns:
            bytes: The steganography key
        """
        if key is None:
            key = generate_stego_key()
        self.keys['stego'] = key
        return key
    
    def get_key(self, key_type: str) -> Optional[bytes]:
        """
        Get stored key by type.
        
        Args:
            key_type (str): 'aes' or 'stego'
            
        Returns:
            bytes or None: The requested key if exists
        """
        return self.keys.get(key_type)
    
    def clear_keys(self):
        """Clear all keys from memory."""
        self.keys.clear()
        self._master_password = None
    
    def save_to_file(self, filepath: str, master_password: str):
        """
        Save keys to encrypted JSON file.
        
        Args:
            filepath (str): Path to save encrypted keys file
            master_password (str): Password to encrypt the keys file
        """
        try:
            # Convert keys to base64 for JSON serialization
            import base64
            keys_data = {
                key_type: base64.b64encode(key_bytes).decode('ascii')
                for key_type, key_bytes in self.keys.items()
            }
            
            # Serialize to JSON
            json_data = json.dumps(keys_data, indent=2)
            
            # Encrypt the JSON data
            ciphertext, salt, iv = encrypt_message(json_data, master_password)
            
            # Save encrypted data with metadata
            save_data = {
                'ciphertext': base64.b64encode(ciphertext).decode('ascii'),
                'salt': base64.b64encode(salt).decode('ascii'),
                'iv': base64.b64encode(iv).decode('ascii'),
                'version': '1.0'
            }
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
                
            self._master_password = master_password
            
        except Exception as e:
            raise RuntimeError(f"Failed to save keys: {str(e)}")
    
    def load_from_file(self, filepath: str, master_password: str):
        """
        Load keys from encrypted JSON file.
        
        Args:
            filepath (str): Path to encrypted keys file
            master_password (str): Password to decrypt the keys file
        """
        try:
            import base64
            
            # Load encrypted data
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            # Extract encryption components
            ciphertext = base64.b64decode(save_data['ciphertext'])
            salt = base64.b64decode(save_data['salt'])
            iv = base64.b64decode(save_data['iv'])
            
            # Decrypt JSON data
            json_data = decrypt_message(ciphertext, master_password, salt, iv)
            
            # Parse keys
            keys_data = json.loads(json_data)
            
            # Convert from base64 back to bytes
            self.keys = {
                key_type: base64.b64decode(key_b64)
                for key_type, key_b64 in keys_data.items()
            }
            
            self._master_password = master_password
            
        except Exception as e:
            raise RuntimeError(f"Failed to load keys: {str(e)}")
    
    def has_keys(self) -> bool:
        """Check if any keys are loaded."""
        return len(self.keys) > 0
    
    def list_keys(self) -> list:
        """List available key types."""
        return list(self.keys.keys())


def test_key_management_module():
    """Test function to verify key management works correctly"""
    print("=== Module 2: Key Management Tests ===")
    
    # Test 1: Key derivation deterministic
    password = "test_password"
    salt = b"1234567890123456"  # 16 bytes
    
    key1 = derive_aes_key(password, salt)
    key2 = derive_aes_key(password, salt)
    
    assert key1 == key2, "Key derivation should be deterministic"
    assert len(key1) == 32, "AES key should be 32 bytes"
    print("✅ Test 1: Key derivation is deterministic")
    
    # Test 2: Different salt = different key
    salt2 = b"6543210987654321"  # Different salt
    key3 = derive_aes_key(password, salt2)
    assert key1 != key3, "Different salt should produce different key"
    print("✅ Test 2: Different salt produces different key")
    
    # Test 3: Stego key generation
    stego1 = generate_stego_key()
    stego2 = generate_stego_key()
    
    assert len(stego1) == 32, "Stego key should be 32 bytes"
    assert stego1 != stego2, "Stego keys should be random"
    print("✅ Test 3: Stego key generation works")
    
    # Test 4: KeyManager operations
    km = KeyManager()
    
    # Set keys
    aes_key = km.set_aes_key(password, salt)
    stego_key = km.set_stego_key()
    
    assert km.get_key('aes') == aes_key, "AES key storage failed"
    assert km.get_key('stego') == stego_key, "Stego key storage failed"
    assert km.has_keys(), "Should have keys"
    assert 'aes' in km.list_keys(), "Should list AES key"
    assert 'stego' in km.list_keys(), "Should list stego key"
    print("✅ Test 4: KeyManager basic operations work")
    
    # Test 5: File persistence
    import tempfile
    temp_file = tempfile.mktemp(suffix='.keys')
    master_password = "master_123"
    
    try:
        # Save keys
        km.save_to_file(temp_file, master_password)
        
        # Create new manager and load
        km2 = KeyManager()
        km2.load_from_file(temp_file, master_password)
        
        assert km2.get_key('aes') == aes_key, "AES key not restored correctly"
        assert km2.get_key('stego') == stego_key, "Stego key not restored correctly"
        print("✅ Test 5: File persistence works")
        
        # Test wrong password
        km3 = KeyManager()
        try:
            km3.load_from_file(temp_file, "wrong_password")
            assert False, "Should have failed with wrong password"
        except:
            print("✅ Test 6: Wrong password correctly rejected")
        
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    print("✅ All key management tests PASSED! Module 2 ready.")
    return True


if __name__ == "__main__":
    test_key_management_module()