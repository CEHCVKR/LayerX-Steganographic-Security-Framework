"""
Hybrid AES-ECC Encryption Module
Implements the architecture from project abstract:
- Message encrypted with AES-256 (random session key)
- AES session key encrypted with ECC (receiver's public key)
- Both payloads embedded together in steganographic image
"""

import sys
import os
sys.path.append('01. Encryption Module')
sys.path.append('02. Key Management Module')

from a1_encryption import encrypt_message, decrypt_message
from a2_key_management import (
    generate_ecc_keypair, 
    encrypt_aes_key_with_ecc, 
    decrypt_aes_key_with_ecc,
    serialize_public_key,
    serialize_private_key,
    deserialize_public_key,
    deserialize_private_key
)
import secrets
import struct


def hybrid_encrypt(plaintext: str, receiver_public_key) -> tuple:
    """
    Hybrid encryption: AES-256 for message, ECC for AES key.
    
    Args:
        plaintext: Message to encrypt
        receiver_public_key: Receiver's ECC public key object
        
    Returns:
        tuple: (encrypted_message, encrypted_aes_key, salt, iv)
    """
    # Generate random AES session key (32 bytes for AES-256)
    aes_session_key = secrets.token_bytes(32)
    
    # Generate random salt and IV for AES
    salt = secrets.token_bytes(16)
    iv = secrets.token_bytes(16)
    
    # Convert session key to hex string (for encrypt_message compatibility)
    password = aes_session_key.hex()
    
    # Encrypt message with AES-256 using session key
    ciphertext, salt, iv = encrypt_message(plaintext, password)
    
    # Encrypt AES session key with receiver's ECC public key
    encrypted_aes_key = encrypt_aes_key_with_ecc(aes_session_key, receiver_public_key)
    
    return ciphertext, encrypted_aes_key, salt, iv


def hybrid_decrypt(ciphertext: bytes, encrypted_aes_key: bytes, 
                  salt: bytes, iv: bytes, receiver_private_key) -> str:
    """
    Hybrid decryption: Decrypt AES key with ECC, then decrypt message with AES.
    
    Args:
        ciphertext: AES-encrypted message
        encrypted_aes_key: ECC-encrypted AES session key
        salt: AES salt
        iv: AES initialization vector
        receiver_private_key: Receiver's ECC private key object
        
    Returns:
        str: Decrypted plaintext message
    """
    # Decrypt AES session key using ECC private key
    aes_session_key = decrypt_aes_key_with_ecc(encrypted_aes_key, receiver_private_key)
    
    # Convert session key to hex string (for decrypt_message compatibility)
    password = aes_session_key.hex()
    
    # Decrypt message with AES-256
    plaintext = decrypt_message(ciphertext, password, salt, iv)
    
    return plaintext


def create_hybrid_payload(ciphertext: bytes, encrypted_aes_key: bytes) -> bytes:
    """
    Combine AES-encrypted message and ECC-encrypted key into single payload.
    
    Format: [aes_key_len: 4 bytes] [encrypted_aes_key] [ciphertext]
    
    Args:
        ciphertext: AES-encrypted message
        encrypted_aes_key: ECC-encrypted AES key (125 bytes)
        
    Returns:
        bytes: Combined payload
    """
    key_len = len(encrypted_aes_key)
    return struct.pack('I', key_len) + encrypted_aes_key + ciphertext


def parse_hybrid_payload(payload: bytes) -> tuple:
    """
    Extract AES-encrypted message and ECC-encrypted key from payload.
    
    Args:
        payload: Combined payload from create_hybrid_payload
        
    Returns:
        tuple: (encrypted_aes_key, ciphertext)
    """
    # Read key length (4 bytes)
    key_len = struct.unpack('I', payload[:4])[0]
    
    # Extract encrypted AES key
    encrypted_aes_key = payload[4:4+key_len]
    
    # Extract ciphertext
    ciphertext = payload[4+key_len:]
    
    return encrypted_aes_key, ciphertext


if __name__ == "__main__":
    # Test hybrid encryption
    print("="*80)
    print("TESTING HYBRID AES-ECC ENCRYPTION")
    print("="*80)
    
    # Generate receiver key pair
    print("\n1. Generating ECC key pair...")
    private_key, public_key = generate_ecc_keypair()
    print(f"   ✓ Generated SECP256R1 key pair")
    
    # Test message
    test_message = "This is a secret message encrypted with hybrid AES-ECC!"
    print(f"\n2. Original message: '{test_message}'")
    
    # Hybrid encryption
    print("\n3. Encrypting...")
    ciphertext, encrypted_key, salt, iv = hybrid_encrypt(test_message, public_key)
    print(f"   ✓ Encrypted message: {len(ciphertext)} bytes")
    print(f"   ✓ Encrypted AES key: {len(encrypted_key)} bytes (ECC)")
    
    # Create combined payload
    payload = create_hybrid_payload(ciphertext, encrypted_key)
    print(f"   ✓ Combined payload: {len(payload)} bytes")
    
    # Parse payload
    print("\n4. Decrypting...")
    extracted_key, extracted_cipher = parse_hybrid_payload(payload)
    
    # Hybrid decryption
    decrypted = hybrid_decrypt(extracted_cipher, extracted_key, salt, iv, private_key)
    print(f"   ✓ Decrypted message: '{decrypted}'")
    
    # Verify
    print("\n5. Verification:")
    if decrypted == test_message:
        print("   ✅ SUCCESS! Hybrid encryption working correctly")
    else:
        print("   ❌ FAIL! Messages don't match")
    
    print("="*80)
