"""
Simple Receiver - Extracts encrypted message
Usage: python receive.py <stego.png> <password> <salt_hex> <iv_hex>
"""
import sys
sys.path.append('01. Encryption Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')

from a1_encryption import decrypt_message
from a4_compression import decompress_huffman, parse_payload
from a5_embedding_extraction import extract

if len(sys.argv) < 5:
    print(__doc__)
    print("\nExample:")
    print("  python receive.py stego.png mypassword <salt_hex> <iv_hex>")
    print("\n(Get salt/IV from sender output)")
    sys.exit(1)

stego, password, salt_hex, iv_hex = sys.argv[1:5]

print("="*80)
print("RECEIVER - Extracting Message")
print("="*80)

try:
    # Convert hex to bytes
    salt = bytes.fromhex(salt_hex)
    iv = bytes.fromhex(iv_hex)
    
    print(f"✓ Using salt/IV from sender")
    
    # Extract (use default optimization, no parameter)
    extracted = extract(stego)
    print(f"✓ Extracted {len(extracted)} bytes")
    
    # Parse & decompress
    msg_len, tree_ext, compressed_ext = parse_payload(extracted)
    ciphertext = decompress_huffman(compressed_ext, tree_ext)
    print(f"✓ Decompressed")
    
    # Decrypt
    message = decrypt_message(ciphertext, password, salt, iv)
    
    print(f"\n✅ SUCCESS!")
    print("="*80)
    print(f"MESSAGE: {message}")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
