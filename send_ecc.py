"""
Hybrid Sender - AES-ECC Encryption + Steganography
Usage: python send_ecc.py <cover.png> <stego.png> <message> <receiver_public_key.pem>
"""
import sys
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')
sys.path.append('02. Key Management Module')

from a4_compression import compress_huffman, create_payload
from a5_embedding_extraction import embed
from a2_key_management import deserialize_public_key
from hybrid_encryption import hybrid_encrypt, create_hybrid_payload

if len(sys.argv) < 5:
    print(__doc__)
    print("\nExample: python send_ecc.py cover.png stego.png 'Secret message' receiver_public.pem")
    sys.exit(1)

cover, stego, message, pubkey_file = sys.argv[1:5]

print("="*80)
print("HYBRID SENDER - AES-ECC Encryption + Steganography")
print("="*80)

try:
    # Load receiver's public key
    with open(pubkey_file, 'rb') as f:
        public_key = deserialize_public_key(f.read())
    print(f"✓ Loaded receiver's ECC public key")
    
    # Hybrid encrypt: AES for message, ECC for AES key
    ciphertext, encrypted_aes_key, salt, iv = hybrid_encrypt(message, public_key)
    print(f"✓ Encrypted {len(message)} chars with hybrid AES-ECC")
    print(f"  - Message encrypted with AES-256")
    print(f"  - AES key encrypted with ECC (SECP256R1)")
    
    # Compress encrypted message
    compressed, tree = compress_huffman(ciphertext)
    compressed_payload = create_payload(ciphertext, tree, compressed)
    print(f"✓ Compressed: {len(ciphertext)} → {len(compressed_payload)} bytes")
    
    # Create hybrid payload (encrypted AES key + compressed data)
    hybrid_payload = create_hybrid_payload(compressed_payload, encrypted_aes_key)
    print(f"✓ Hybrid payload: {len(hybrid_payload)} bytes")
    
    # Embed in image
    success = embed(hybrid_payload, cover, stego)
    
    if success:
        print(f"✓ Embedded successfully")
        print(f"\n✅ SUCCESS! Saved: {stego}")
        print(f"\n📋 IMPORTANT - Send to receiver:")
        print(f"   Salt: {salt.hex()}")
        print(f"   IV:   {iv.hex()}")
        print(f"\nReceiver needs their private key to decrypt!")
    else:
        print(f"❌ Embedding failed")
        sys.exit(1)
        
except FileNotFoundError:
    print(f"❌ Error: Public key file '{pubkey_file}' not found")
    print("   Generate keys first: python generate_keys.py")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("="*80)
