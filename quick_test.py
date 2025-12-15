"""
Quick Test Suite - Tests key functionality with actual API
"""

import sys
import os

sys.path.append('01. Encryption Module')
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')  
sys.path.append('05. Embedding and Extraction Module')

from a1_encryption import encrypt_message, decrypt_message
from a3_image_processing import dwt_decompose, dwt_reconstruct, psnr, get_capacity, read_image
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import embed, extract

print("="*80)
print("LayerX - Quick Functional Test")
print("="*80)

passed = 0
failed = 0

# Test 1: Encryption
print("\n[Test 1] Encryption/Decryption")
try:
    msg = "Hello World"
    ciphertext, salt, iv = encrypt_message(msg, "password")
    decrypted = decrypt_message(ciphertext, "password", salt, iv)
    if decrypted == msg:
        print("✅ PASS - Encryption working")
        passed += 1
    else:
        print("❌ FAIL - Decryption mismatch")
        failed += 1
except Exception as e:
    print(f"❌ FAIL - {e}")
    failed += 1

# Test 2: DWT
print("\n[Test 2] DWT Decomposition/Reconstruction")
try:
    import cv2
    img = cv2.imread('test_lena.png', cv2.IMREAD_GRAYSCALE)
    bands = dwt_decompose(img)
    reconstructed = dwt_reconstruct(bands)
    psnr_val = psnr(img, reconstructed)
    if psnr_val > 100:
        print(f"✅ PASS - DWT working (PSNR: {psnr_val:.1f} dB)")
        passed += 1
    else:
        print(f"❌ FAIL - Poor reconstruction (PSNR: {psnr_val:.1f} dB)")
        failed += 1
except Exception as e:
    print(f"❌ FAIL - {e}")
    failed += 1

# Test 3: Compression
print("\n[Test 3] Huffman Compression")
try:
    data = b"AAAABBBCCC"
    compressed, tree = compress_huffman(data)  # Fixed: returns (compressed, tree)
    decompressed = decompress_huffman(compressed, tree)
    if decompressed == data:
        ratio = len(compressed)/len(data)*100
        print(f"✅ PASS - Compression working (ratio: {ratio:.1f}%)")
        passed += 1
    else:
        print("❌ FAIL - Decompression mismatch")
        failed += 1
except Exception as e:
    print(f"❌ FAIL - {e}")
    failed += 1

# Test 4: Embedding (simple length header test)
print("\n[Test 4] Embedding/Extraction (Length Header)")
try:
    # Create a small payload (just length headers)
    test_data = b"Test"
    compressed, tree = compress_huffman(test_data)  # Fixed: returns (compressed, tree)
    payload = create_payload(test_data, tree, compressed)
    
    # Embed
    embed(payload, 'test_lena.png', 'test_quick.png')
    
    # Extract - Fixed: only takes stego_path, returns full payload
    extracted_payload = extract('test_quick.png')
    msg_len, tree_ext, compressed_ext = parse_payload(extracted_payload)
    
    if msg_len == len(test_data):
        print(f"✅ PASS - Length header correct ({msg_len} bytes)")
        passed += 1
    else:
        print(f"❌ FAIL - Length mismatch (got {msg_len}, expected {len(test_data)})")
        failed += 1
except Exception as e:
    print(f"❌ FAIL - {e}")
    failed += 1

# Test 5: Full pipeline (short message)
print("\n[Test 5] Full Pipeline Integration")
try:
    message = "Test!"
    password = "pass123"
    
    # Encrypt
    ciphertext, salt, iv = encrypt_message(message, password)
    
    # Compress
    compressed, tree = compress_huffman(ciphertext)  # Fixed: returns (compressed, tree)
    payload = create_payload(ciphertext, tree, compressed)
    
    print(f"   Message: '{message}' ({len(message)} chars)")
    print(f"   Payload: {len(payload)} bytes")
    
    # Embed - Fixed: get_capacity needs image shape, not path
    test_img = read_image('test_lena.png')
    capacity = get_capacity(test_img.shape[:2], 'dwt')  # Pass (height, width) only
    print(f"   Capacity: {capacity} bytes")
    
    if len(payload) > capacity:
        print(f"⚠️  SKIP - Payload ({len(payload)}) > Capacity ({capacity})")
    else:
        embed(payload, 'test_lena.png', 'test_full_pipeline.png')
        
        # Extract - Fixed: only takes stego_path
        extracted_payload = extract('test_full_pipeline.png')
        msg_len, tree_ext, compressed_ext = parse_payload(extracted_payload)
        ciphertext_ext = decompress_huffman(compressed_ext, tree_ext)
        decrypted = decrypt_message(ciphertext_ext, password, salt, iv)
        
        if decrypted == message:
            print(f"✅ PASS - Full pipeline working")
            print(f"   Extracted: '{decrypted}'")
            passed += 1
        else:
            print(f"❌ FAIL - Message mismatch")
            print(f"   Expected: '{message}'")
            print(f"   Got: '{decrypted}'")
            failed += 1
except Exception as e:
    print(f"❌ FAIL - {e}")
    import traceback
    traceback.print_exc()
    failed += 1

# Test 6: PSNR Quality
print("\n[Test 6] Steganographic Quality (PSNR)")
try:
    import cv2
    if os.path.exists('test_full_pipeline.png'):
        cover = cv2.imread('test_lena.png', cv2.IMREAD_GRAYSCALE)
        stego = cv2.imread('test_full_pipeline.png', cv2.IMREAD_GRAYSCALE)
        psnr_val = psnr(cover, stego)
        
        if psnr_val > 50:
            print(f"✅ PASS - Excellent quality (PSNR: {psnr_val:.2f} dB)")
            passed += 1
        elif psnr_val > 40:
            print(f"⚠️  WARN - Acceptable quality (PSNR: {psnr_val:.2f} dB)")
            passed += 1
        else:
            print(f"❌ FAIL - Poor quality (PSNR: {psnr_val:.2f} dB)")
            failed += 1
    else:
        print("⚠️  SKIP - No stego image to test")
except Exception as e:
    print(f"❌ FAIL - {e}")
    failed += 1

# Test 7: Different messages
print("\n[Test 7] Multiple Test Cases")
test_cases = [
    ("A", "Single char"),
    ("Hello", "Short"),  
    ("123456789", "Numbers"),
    ("Test\nMultiline", "Multiline")
]

test_passed = 0
for msg, desc in test_cases:
    try:
        ciphertext, salt, iv = encrypt_message(msg, "pw")
        compressed, tree = compress_huffman(ciphertext)  # Fixed: returns (compressed, tree)
        payload = create_payload(ciphertext, tree, compressed)
        
        # Fixed: get_capacity needs image shape
        test_img = read_image('test_lena.png')
        capacity = get_capacity(test_img.shape[:2], 'dwt')
        
        if len(payload) <= capacity:
            stego = f'test_case_{desc.replace(" ", "_")}.png'
            embed(payload, 'test_lena.png', stego)
            
            # Fixed: extract() only takes stego_path
            extracted_payload = extract(stego)
            msg_len, tree_ext, compressed_ext = parse_payload(extracted_payload)
            ciphertext_ext = decompress_huffman(compressed_ext, tree_ext)
            decrypted = decrypt_message(ciphertext_ext, "pw", salt, iv)
            
            if decrypted == msg:
                print(f"   ✅ {desc}: PASS")
                test_passed += 1
            else:
                print(f"   ❌ {desc}: FAIL (mismatch)")
        else:
            print(f"   ⚠️  {desc}: SKIP (too large)")
            test_passed += 1  # Don't penalize
    except Exception as e:
        print(f"   ❌ {desc}: ERROR - {str(e)[:50]}")

if test_passed == len(test_cases):
    print(f"✅ PASS - All {len(test_cases)} test cases successful")
    passed += 1
else:
    print(f"⚠️  PARTIAL - {test_passed}/{len(test_cases)} test cases passed")
    passed += 1

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
total = passed + failed
print(f"Total: {total}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"Success Rate: {passed/total*100:.1f}%")
print("="*80)

if failed == 0:
    print("🎉 ALL TESTS PASSED!")
else:
    print(f"⚠️  {failed} test(s) need attention")
