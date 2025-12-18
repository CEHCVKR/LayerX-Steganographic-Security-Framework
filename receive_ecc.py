"""
Hybrid Receiver - AES-ECC Decryption + Steganography
Usage: python receive_ecc.py <stego.png> <receiver_private_key.pem> <salt_hex> <iv_hex> [password]
"""
import sys
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')
sys.path.append('02. Key Management Module')

from a4_compression import decompress_huffman, parse_payload
from a5_embedding_extraction import extract
from a2_key_management import deserialize_private_key
from hybrid_encryption import hybrid_decrypt, parse_hybrid_payload

if len(sys.argv) < 5:
    print(__doc__)
    print("\nExample:")
    print("  python receive_ecc.py stego.png private_key.pem <salt_hex> <iv_hex>")
    print("  python receive_ecc.py stego.png private_key.pem <salt_hex> <iv_hex> key_password")
    sys.exit(1)

stego = sys.argv[1]
privkey_file = sys.argv[2]
salt_hex = sys.argv[3]
iv_hex = sys.argv[4]
key_password = sys.argv[5] if len(sys.argv) > 5 else None

print("="*80)
print("HYBRID RECEIVER - AES-ECC Decryption + Steganography")
print("="*80)

try:
    # Load receiver's private key
    with open(privkey_file, 'rb') as f:
        private_key = deserialize_private_key(f.read(), key_password)
    print(f"✓ Loaded receiver's ECC private key")
    
    # Convert hex to bytes
    salt = bytes.fromhex(salt_hex)
    iv = bytes.fromhex(iv_hex)
    print(f"✓ Using salt/IV from sender")
    
    # Extract from image
    hybrid_payload = extract(stego)
    print(f"✓ Extracted {len(hybrid_payload)} bytes")
    
    # Parse hybrid payload
    encrypted_aes_key, compressed_payload = parse_hybrid_payload(hybrid_payload)
    print(f"✓ Parsed hybrid payload:")
    print(f"  - Encrypted AES key: {len(encrypted_aes_key)} bytes")
    print(f"  - Compressed data: {len(compressed_payload)} bytes")
    
    # Decompress
    msg_len, tree_ext, compressed_ext = parse_payload(compressed_payload)
    ciphertext = decompress_huffman(compressed_ext, tree_ext)
    print(f"✓ Decompressed")
    
    # Hybrid decrypt: ECC to get AES key, then AES to decrypt message
    message = hybrid_decrypt(ciphertext, encrypted_aes_key, salt, iv, private_key)
    
    print(f"\n✅ SUCCESS!")
    print("="*80)
    print(f"MESSAGE: {message}")
    print("="*80)
    
except FileNotFoundError as e:
    print(f"❌ Error: File not found - {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
