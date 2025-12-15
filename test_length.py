#!/usr/bin/env python3
import numpy as np
import struct
import sys

# Add module paths
sys.path.append("01. Encryption Module")
sys.path.append("03. Image Processing Module")
sys.path.append("05. Embedding and Extraction Module")

from a3_image_processing import *
from a5_embedding_extraction import *

def test_length_header():
    """Test length header embedding and extraction specifically"""
    print("=== Testing Length Header ===")
    
    # Read test image
    image = read_image('test_lena.png')
    bands = dwt_decompose(image, levels=2)
    
    # Test payload: just the length header
    test_length = 11  # bytes (for "Hello World")
    length_bytes = struct.pack('I', test_length)
    print(f"Length bytes: {length_bytes.hex()} (little-endian uint32)")
    print(f"Length value: {test_length}")
    
    # Convert to bits
    length_bits = ''.join(format(byte, '08b') for byte in length_bytes)
    print(f"Length bits (32): {length_bits}")
    
    # Embed length header
    print(f"\n--- Embedding Length Header ---")
    modified_bands = embed_in_dwt_bands(length_bits, bands)
    
    # Reconstruct
    stego_image = dwt_reconstruct(modified_bands)
    stego_bands = dwt_decompose(stego_image, levels=2)
    
    # Extract length header
    print(f"\n--- Extracting Length Header ---")
    extracted_bits = extract_from_dwt_bands(stego_bands, 32)
    print(f"Extracted bits: {extracted_bits}")
    
    # Convert back to length
    length_bytes_extracted = []
    for i in range(0, 32, 8):
        byte_bits = extracted_bits[i:i+8]
        byte_value = int(byte_bits, 2)
        length_bytes_extracted.append(byte_value)
    
    length_bytes_extracted = bytes(length_bytes_extracted)
    print(f"Extracted bytes: {length_bytes_extracted.hex()}")
    
    try:
        extracted_length = struct.unpack('I', length_bytes_extracted)[0]
        print(f"Extracted length: {extracted_length}")
        
        if extracted_length == test_length:
            print("✅ Length header extraction SUCCESSFUL!")
        else:
            print(f"❌ Length mismatch: expected {test_length}, got {extracted_length}")
    except struct.error as e:
        print(f"❌ Length unpacking failed: {e}")
    
    # Bit-by-bit comparison
    print(f"\nBit-by-bit comparison:")
    for i in range(32):
        expected = length_bits[i]
        actual = extracted_bits[i] if i < len(extracted_bits) else 'X'
        status = "✓" if expected == actual else "✗"
        if i % 8 == 0:
            print(f"\nByte {i//8}: ", end="")
        print(f"{expected}/{actual}{status}", end=" ")
    print()

if __name__ == "__main__":
    test_length_header()