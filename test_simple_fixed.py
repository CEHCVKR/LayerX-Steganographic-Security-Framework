"""
Simple test for Fixed method only
"""
import sys
sys.path.append('01. Encryption Module')
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')

from a1_encryption import encrypt_message, decrypt_message
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import embed, extract

# Simple test
message = "Hello World! Testing optimization methods."
password = "test123"

print(f"Original message: '{message}'")

# Encrypt + compress + create payload
ciphertext, salt, iv = encrypt_message(message, password)
compressed, tree = compress_huffman(ciphertext)
payload = create_payload(ciphertext, tree, compressed)

print(f"Payload size: {len(payload)} bytes")

# Embed
success = embed(payload, 'test_lena.png', 'test_fixed_simple.png', optimization='fixed')
print(f"Embedding: {'SUCCESS' if success else 'FAILED'}")

if success:
    # Extract
    extracted = extract('test_fixed_simple.png', optimization='fixed')
    print(f"Extracted size: {len(extracted)} bytes")
    
    if len(extracted) > 0:
        # Decompress + decrypt
        try:
            msg_len, tree_ext, compressed_ext = parse_payload(extracted)
            print(f"Parsed: msg_len={msg_len}")
            ciphertext_ext = decompress_huffman(compressed_ext, tree_ext)
            decrypted = decrypt_message(ciphertext_ext, password, salt, iv)
            print(f"Decrypted message: '{decrypted}'")
            print(f"Match: {decrypted == message}")
        except Exception as e:
            print(f"Error: {e}")
