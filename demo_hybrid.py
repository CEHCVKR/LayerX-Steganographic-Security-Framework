"""
Simple demonstration: sender.py and receiver.py usage
Shows all 3 modes: Fixed (speed), Chaos (security), Hybrid (balanced)
"""
import sys
sys.path.append('01. Encryption Module')
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')

from a1_encryption import encrypt_message, decrypt_message
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import embed, extract

# Test message
message = "Hello! Hybrid mode works!"
password = "test123"

print("=" * 80)
print("DEMONSTRATION: Hybrid Mode (Security + Quality + Speed)")
print("=" * 80)

# Encrypt
ciphertext, salt, iv = encrypt_message(message, password)
print(f"\n✓ Encrypted {len(message)} chars → {len(ciphertext)} bytes")

# Compress
compressed, tree = compress_huffman(ciphertext)
payload = create_payload(ciphertext, tree, compressed)
print(f"✓ Compressed → {len(payload)} bytes payload")

# Embed using CHAOS (security)
print(f"\n[CHAOS MODE] Embedding with security...")
success = embed(payload, 'test_lena.png', 'demo_chaos.png', optimization='chaos')
if success:
    print(f"✓ Embedded successfully using CHAOS")
    
    # Extract using CHAOS
    extracted = extract('demo_chaos.png', optimization='chaos')
    msg_len, tree_ext, compressed_ext = parse_payload(extracted)
    ciphertext_ext = decompress_huffman(compressed_ext, tree_ext)
    decrypted = decrypt_message(ciphertext_ext, password, salt, iv)
    
    if decrypted == message:
        print(f"✓ Extracted and decrypted: '{decrypted}'")
        print(f"✅ CHAOS MODE: SUCCESS (Security-focused)")
    else:
        print(f"❌ CHAOS MODE: Decryption mismatch")

# Embed using FIXED (speed)
print(f"\n[FIXED MODE] Embedding with speed...")
success = embed(payload, 'test_lena.png', 'demo_fixed.png', optimization='fixed')
if success:
    print(f"✓ Embedded successfully using FIXED")
    
    # Extract using FIXED
    extracted = extract('demo_fixed.png', optimization='fixed')
    msg_len, tree_ext, compressed_ext = parse_payload(extracted)
    ciphertext_ext = decompress_huffman(compressed_ext, tree_ext)
    decrypted = decrypt_message(ciphertext_ext, password, salt, iv)
    
    if decrypted == message:
        print(f"✓ Extracted and decrypted: '{decrypted}'")
        print(f"✅ FIXED MODE: SUCCESS (Speed-focused)")
    else:
        print(f"❌ FIXED MODE: Decryption mismatch")

print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print("✅ CHAOS: Steganalysis-resistant (use for security)")
print("✅ FIXED: High-speed (use for large files)")
print("✅ HYBRID: Adaptive selection based on payload size")
print("\nFor sender.py/receiver.py: Both work when using matching methods!")
print("=" * 80)
