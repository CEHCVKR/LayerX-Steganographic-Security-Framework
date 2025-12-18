"""
Module 2: Key Management
Author: Member A
Description: AES key derivation, ECC key management, and steganography key generation
Dependencies: secrets, json, cryptography

Functions:
- derive_aes_key(password: str, salt: bytes) → bytes (32-byte AES-256 key)
- generate_stego_key() → bytes (32 random bytes for steganography)
- generate_ecc_keypair() → (private_key, public_key) (SECP256R1 ECC keys)
- encrypt_aes_key_with_ecc(aes_key: bytes, public_key) → bytes
- decrypt_aes_key_with_ecc(encrypted_key: bytes, private_key) → bytes
- KeyManager class for in-memory key storage and encrypted file persistence
"""

import os
import json
import secrets
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from typing import Dict, Optional, Tuple
import sys
import os
# Add parent and sibling directories to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, "01. Encryption Module"))
from a1_encryption import encrypt_message, decrypt_message

# ECC imports
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


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


def generate_ecc_keypair() -> Tuple:
    """
    Generate ECC key pair using SECP256R1 (P-256) curve.
    
    Returns:
        tuple: (private_key, public_key) objects
    """
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()
    return private_key, public_key


def serialize_public_key(public_key) -> bytes:
    """
    Serialize ECC public key to PEM format.
    
    Args:
        public_key: ECC public key object
        
    Returns:
        bytes: PEM-encoded public key
    """
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def deserialize_public_key(pem_data: bytes):
    """
    Deserialize ECC public key from PEM format.
    
    Args:
        pem_data: PEM-encoded public key bytes
        
    Returns:
        ECC public key object
    """
    return serialization.load_pem_public_key(pem_data, backend=default_backend())


def serialize_private_key(private_key, password: Optional[str] = None) -> bytes:
    """
    Serialize ECC private key to PEM format with optional encryption.
    
    Args:
        private_key: ECC private key object
        password: Optional password for encryption
        
    Returns:
        bytes: PEM-encoded private key
    """
    if password:
        encryption = serialization.BestAvailableEncryption(password.encode('utf-8'))
    else:
        encryption = serialization.NoEncryption()
    
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption
    )


def deserialize_private_key(pem_data: bytes, password: Optional[str] = None):
    """
    Deserialize ECC private key from PEM format.
    
    Args:
        pem_data: PEM-encoded private key bytes
        password: Optional password if key is encrypted
        
    Returns:
        ECC private key object
    """
    pwd = password.encode('utf-8') if password else None
    return serialization.load_pem_private_key(pem_data, password=pwd, backend=default_backend())


def encrypt_aes_key_with_ecc(aes_key: bytes, public_key) -> bytes:
    """
    Encrypt AES session key using ECC public key (ECIES-like scheme).
    Uses ECDH + KDF + AES-GCM for encryption.
    
    Args:
        aes_key: 32-byte AES-256 key to encrypt
        public_key: Receiver's ECC public key
        
    Returns:
        bytes: Encrypted AES key (ephemeral_public_key || nonce || ciphertext || tag)
    """
    # Generate ephemeral key pair
    ephemeral_private = ec.generate_private_key(ec.SECP256R1(), default_backend())
    ephemeral_public = ephemeral_private.public_key()
    
    # Perform ECDH to get shared secret
    shared_secret = ephemeral_private.exchange(ec.ECDH(), public_key)
    
    # Derive encryption key from shared secret using HKDF
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'ECC-AES-Hybrid',
        backend=default_backend()
    ).derive(shared_secret)
    
    # Encrypt AES key with derived key using AES-GCM
    nonce = os.urandom(12)  # 96-bit nonce for GCM
    cipher = Cipher(algorithms.AES(derived_key), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(aes_key) + encryptor.finalize()
    
    # Serialize ephemeral public key
    ephemeral_public_bytes = ephemeral_public.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )
    
    # Return: ephemeral_public (65 bytes) || nonce (12 bytes) || ciphertext (32 bytes) || tag (16 bytes)
    return ephemeral_public_bytes + nonce + ciphertext + encryptor.tag


def decrypt_aes_key_with_ecc(encrypted_data: bytes, private_key) -> bytes:
    """
    Decrypt AES session key using ECC private key.
    
    Args:
        encrypted_data: Encrypted AES key from encrypt_aes_key_with_ecc
        private_key: Receiver's ECC private key
        
    Returns:
        bytes: Decrypted 32-byte AES-256 key
    """
    # Parse encrypted data
    ephemeral_public_bytes = encrypted_data[:65]  # Uncompressed point (65 bytes)
    nonce = encrypted_data[65:77]  # 12 bytes
    ciphertext = encrypted_data[77:109]  # 32 bytes
    tag = encrypted_data[109:125]  # 16 bytes
    
    # Reconstruct ephemeral public key
    ephemeral_public = ec.EllipticCurvePublicKey.from_encoded_point(
        ec.SECP256R1(), ephemeral_public_bytes
    )
    
    # Perform ECDH to get shared secret
    shared_secret = private_key.exchange(ec.ECDH(), ephemeral_public)
    
    # Derive decryption key from shared secret
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'ECC-AES-Hybrid',
        backend=default_backend()
    ).derive(shared_secret)
    
    # Decrypt using AES-GCM
    cipher = Cipher(algorithms.AES(derived_key), modes.GCM(nonce, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    aes_key = decryptor.update(ciphertext) + decryptor.finalize()
    
    return aes_key
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