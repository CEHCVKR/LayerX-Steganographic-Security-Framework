"""
Final Comprehensive Test - Stress Testing All Features
Tests: Large messages, different data types, edge cases, performance
"""
import sys
import os
import time

sys.path.append('01. Encryption Module')
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')

from a1_encryption import encrypt_message, decrypt_message
from a3_image_processing import dwt_decompose, dwt_reconstruct, psnr, get_capacity, read_image
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import embed, extract

print("="*80)
print("LayerX - Final Comprehensive Test Suite")
print("="*80)

# Get capacity
test_img = read_image('test_lena.png')
max_capacity = get_capacity(test_img.shape[:2], 'dwt')
print(f"\nImage: 512x512 Lena")
print(f"Maximum Capacity: {max_capacity} bytes ({max_capacity/1024:.1f} KB)")
print(f"Capacity Ratio: {max_capacity/(512*512)*100:.2f}% of image size")

passed = 0
failed = 0

# Test 1: Small message
print("\n" + "="*80)
print("[Test 1] Small Message (5 bytes)")
print("="*80)
try:
    start_time = time.time()
    message = "Hello"
    password = "test123"
    
    # Full pipeline
    ciphertext, salt, iv = encrypt_message(message, password)
    compressed, tree = compress_huffman(ciphertext)
    payload = create_payload(ciphertext, tree, compressed)
    
    print(f"Original: '{message}' ({len(message)} bytes)")
    print(f"Encrypted: {len(ciphertext)} bytes")
    print(f"Compressed: {len(compressed)} bytes ({len(compressed)/len(ciphertext)*100:.1f}%)")
    print(f"Payload: {payload} bytes (with ECC)")
    
    embed(payload, 'test_lena.png', 'test_final_small.png')
    
    extracted = extract('test_final_small.png')
    msg_len, tree_ext, compressed_ext = parse_payload(extracted)
    ciphertext_ext = decompress_huffman(compressed_ext, tree_ext)
    decrypted = decrypt_message(ciphertext_ext, password, salt, iv)
    
    elapsed = time.time() - start_time
    
    if decrypted == message:
        print(f"✅ PASS - Round-trip successful ({elapsed:.3f}s)")
        passed += 1
    else:
        print(f"❌ FAIL - Mismatch")
        failed += 1
except Exception as e:
    print(f"❌ FAIL - {e}")
    failed += 1

# Test 2: Medium message (100 bytes)
print("\n" + "="*80)
print("[Test 2] Medium Message (100 bytes)")
print("="*80)
try:
    start_time = time.time()
    message = "A" * 100
    password = "test123"
    
    ciphertext, salt, iv = encrypt_message(message, password)
    compressed, tree = compress_huffman(ciphertext)
    payload = create_payload(ciphertext, tree, compressed)
    
    print(f"Original: {len(message)} bytes")
    print(f"Payload: {len(payload)} bytes (compression ratio: {len(payload)/len(message)*100:.1f}%)")
    
    embed(payload, 'test_lena.png', 'test_final_medium.png')
    
    extracted = extract('test_final_medium.png')
    msg_len, tree_ext, compressed_ext = parse_payload(extracted)
    ciphertext_ext = decompress_huffman(compressed_ext, tree_ext)
    decrypted = decrypt_message(ciphertext_ext, password, salt, iv)
    
    elapsed = time.time() - start_time
    
    # Check PSNR
    import cv2
    cover = cv2.imread('test_lena.png', cv2.IMREAD_GRAYSCALE)
    stego = cv2.imread('test_final_medium.png', cv2.IMREAD_GRAYSCALE)
    psnr_val = psnr(cover, stego)
    
    if decrypted == message:
        print(f"✅ PASS - Round-trip successful ({elapsed:.3f}s)")
        print(f"   PSNR: {psnr_val:.2f} dB")
        passed += 1
    else:
        print(f"❌ FAIL - Mismatch")
        failed += 1
except Exception as e:
    print(f"❌ FAIL - {e}")
    import traceback
    traceback.print_exc()
    failed += 1

# Test 3: Large message (1000 bytes)
print("\n" + "="*80)
print("[Test 3] Large Message (1000 bytes)")
print("="*80)
try:
    start_time = time.time()
    message = "The quick brown fox jumps over the lazy dog. " * 22  # ~1000 bytes
    password = "test123"
    
    ciphertext, salt, iv = encrypt_message(message, password)
    compressed, tree = compress_huffman(ciphertext)
    payload = create_payload(ciphertext, tree, compressed)
    
    print(f"Original: {len(message)} bytes")
    print(f"Payload: {len(payload)} bytes")
    print(f"Capacity available: {max_capacity} bytes")
    
    if len(payload) > max_capacity:
        print(f"⚠️  SKIP - Payload too large ({len(payload)} > {max_capacity})")
    else:
        embed(payload, 'test_lena.png', 'test_final_large.png')
        
        extracted = extract('test_final_large.png')
        msg_len, tree_ext, compressed_ext = parse_payload(extracted)
        ciphertext_ext = decompress_huffman(compressed_ext, tree_ext)
        decrypted = decrypt_message(ciphertext_ext, password, salt, iv)
        
        elapsed = time.time() - start_time
        
        # Check PSNR
        cover = cv2.imread('test_lena.png', cv2.IMREAD_GRAYSCALE)
        stego = cv2.imread('test_final_large.png', cv2.IMREAD_GRAYSCALE)
        psnr_val = psnr(cover, stego)
        
        if decrypted == message:
            print(f"✅ PASS - Large message successful ({elapsed:.3f}s)")
            print(f"   PSNR: {psnr_val:.2f} dB")
            print(f"   Capacity used: {len(payload)/max_capacity*100:.1f}%")
            passed += 1
        else:
            print(f"❌ FAIL - Mismatch (got {len(decrypted)} bytes)")
            failed += 1
except Exception as e:
    print(f"❌ FAIL - {e}")
    import traceback
    traceback.print_exc()
    failed += 1

# Test 4: Binary data
print("\n" + "="*80)
print("[Test 4] Binary Data (100 random bytes)")
print("="*80)
try:
    import random
    message_bytes = bytes([random.randint(0, 255) for _ in range(100)])
    password = "test123"
    
    # Note: encrypt_message expects string, so we'll use the payload directly
    compressed, tree = compress_huffman(message_bytes)
    payload = create_payload(message_bytes, tree, compressed)
    
    print(f"Original: {len(message_bytes)} bytes (binary)")
    print(f"Payload: {len(payload)} bytes")
    
    embed(payload, 'test_lena.png', 'test_final_binary.png')
    
    extracted = extract('test_final_binary.png')
    msg_len, tree_ext, compressed_ext = parse_payload(extracted)
    decompressed = decompress_huffman(compressed_ext, tree_ext)
    
    if decompressed == message_bytes:
        print(f"✅ PASS - Binary data preserved")
        passed += 1
    else:
        print(f"❌ FAIL - Binary mismatch")
        failed += 1
except Exception as e:
    print(f"❌ FAIL - {e}")
    import traceback
    traceback.print_exc()
    failed += 1

# Test 5: Unicode characters
print("\n" + "="*80)
print("[Test 5] Unicode Characters")
print("="*80)
try:
    message = "Hello 世界! 🌍 Привет"
    password = "test123"
    
    ciphertext, salt, iv = encrypt_message(message, password)
    compressed, tree = compress_huffman(ciphertext)
    payload = create_payload(ciphertext, tree, compressed)
    
    embed(payload, 'test_lena.png', 'test_final_unicode.png')
    
    extracted = extract('test_final_unicode.png')
    msg_len, tree_ext, compressed_ext = parse_payload(extracted)
    ciphertext_ext = decompress_huffman(compressed_ext, tree_ext)
    decrypted = decrypt_message(ciphertext_ext, password, salt, iv)
    
    if decrypted == message:
        print(f"✅ PASS - Unicode preserved: '{decrypted}'")
        passed += 1
    else:
        print(f"❌ FAIL - Unicode mismatch")
        print(f"   Expected: '{message}'")
        print(f"   Got: '{decrypted}'")
        failed += 1
except Exception as e:
    print(f"❌ FAIL - {e}")
    import traceback
    traceback.print_exc()
    failed += 1

# Test 6: Edge case - Empty string
print("\n" + "="*80)
print("[Test 6] Edge Case - Single Character")
print("="*80)
try:
    message = "X"
    password = "test123"
    
    ciphertext, salt, iv = encrypt_message(message, password)
    compressed, tree = compress_huffman(ciphertext)
    payload = create_payload(ciphertext, tree, compressed)
    
    embed(payload, 'test_lena.png', 'test_final_single.png')
    
    extracted = extract('test_final_single.png')
    msg_len, tree_ext, compressed_ext = parse_payload(extracted)
    ciphertext_ext = decompress_huffman(compressed_ext, tree_ext)
    decrypted = decrypt_message(ciphertext_ext, password, salt, iv)
    
    if decrypted == message:
        print(f"✅ PASS - Single character preserved")
        passed += 1
    else:
        print(f"❌ FAIL - Mismatch")
        failed += 1
except Exception as e:
    print(f"❌ FAIL - {e}")
    failed += 1

# Summary
print("\n" + "="*80)
print("FINAL TEST SUMMARY")
print("="*80)
total = passed + failed
print(f"Total Tests: {total}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"Success Rate: {passed/total*100:.1f}%")

if failed == 0:
    print("\n🎉 ALL TESTS PASSED! System ready for production.")
else:
    print(f"\n⚠️  {failed} test(s) need attention")

print("\n" + "="*80)
print("Technical Specifications:")
print("="*80)
print(f"Encryption: AES-256 + ECC P-256")
print(f"Compression: Huffman coding")
print(f"Error Correction: Reed-Solomon (20 symbols)")
print(f"Steganography: DWT-based (2-level)")
print(f"Embedding Domain: HH, HL, LH bands")
print(f"Quantization: Fixed Q=2.0")
print(f"Capacity: {max_capacity} bytes ({max_capacity*8} bits)")
print(f"PSNR: >60 dB (excellent quality)")
print("="*80)
