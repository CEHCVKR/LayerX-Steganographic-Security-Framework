"""
Simple Sender - Embeds encrypted message
Usage: python send.py <cover.png> <stego.png> <message> <password>
"""
import sys
sys.path.append('01. Encryption Module')
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')

from a1_encryption import encrypt_message
from a4_compression import compress_huffman, create_payload
from a5_embedding_extraction import embed

if len(sys.argv) < 5:
    print(__doc__)
    print("\nExample: python send.py cover.png stego.png 'Hello World' mypassword")
    sys.exit(1)

cover, stego, message, password = sys.argv[1:5]

print("="*80)
print("SENDER - Security + Quality + Speed")
print("="*80)

# Encrypt
ciphertext, salt, iv = encrypt_message(message, password)
print(f"✓ Encrypted {len(message)} chars")

# Compress
compressed, tree = compress_huffman(ciphertext)
payload = create_payload(ciphertext, tree, compressed)
print(f"✓ Payload: {len(payload)} bytes")

# Embed (use default optimization, no parameter)
success = embed(payload, cover, stego)

if success:
    print(f"✓ Embedded successfully")
    print(f"\n✅ SUCCESS! Saved: {stego}")
    print(f"\n📋 IMPORTANT - Save these values:")
    print(f"   Salt: {salt.hex()}")
    print(f"   IV:   {iv.hex()}")
    print(f"\nShare salt/IV securely with receiver!")
else:
    print(f"❌ Embedding failed")
    sys.exit(1)

print("="*80)
