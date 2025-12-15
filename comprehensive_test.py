"""
Comprehensive Test Suite for LayerX Steganographic Security Framework
Tests all modules with various test cases, edge cases, and use cases
"""

import sys
import os
import time
import numpy as np
from PIL import Image

# Add module paths
sys.path.append('01. Encryption Module')
sys.path.append('02. Key Management Module')
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')

from a1_encryption import encrypt_message, decrypt_message
from a3_image_processing import dwt_decompose, dwt_reconstruct, psnr
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import embed, extract, get_capacity

print("=" * 80)
print("🚀 LayerX Steganographic Security Framework - Comprehensive Test Suite")
print("=" * 80)

# Test results tracker
test_results = {
    'passed': 0,
    'failed': 0,
    'total': 0
}

def run_test(test_name, test_func):
    """Run a single test and track results"""
    test_results['total'] += 1
    print(f"\n{'='*80}")
    print(f"Test {test_results['total']}: {test_name}")
    print(f"{'='*80}")
    try:
        result = test_func()
        if result:
            test_results['passed'] += 1
            print(f"✅ PASSED: {test_name}")
            return True
        else:
            test_results['failed'] += 1
            print(f"❌ FAILED: {test_name}")
            return False
    except Exception as e:
        test_results['failed'] += 1
        print(f"❌ ERROR: {test_name}")
        print(f"   Exception: {str(e)}")
        return False

# ============================================================================
# MODULE 1: ENCRYPTION TESTS
# ============================================================================

def test_encryption_basic():
    """Test basic encryption/decryption"""
    message = "Hello, World!"
    password = "test_password_123"
    
    ciphertext, salt, iv = encrypt_message(message, password)
    decrypted = decrypt_message(ciphertext, password, salt, iv)
    
    success = decrypted == message
    print(f"   Original: {message}")
    print(f"   Encrypted length: {len(ciphertext)} bytes")
    print(f"   Decrypted: {decrypted}")
    print(f"   Match: {success}")
    return success

def test_encryption_empty():
    """Test encryption with empty message"""
    message = ""
    password = "test_password"
    
    ciphertext, salt, iv = encrypt_message(message, password)
    decrypted = decrypt_message(ciphertext, password, salt, iv)
    
    success = decrypted == message
    print(f"   Empty message encryption: {success}")
    return success

def test_encryption_large():
    """Test encryption with large message (1MB)"""
    message = "X" * (1024 * 1024)  # 1MB
    password = "large_test_123"
    
    start = time.time()
    ciphertext, salt, iv = encrypt_message(message, password)
    encrypt_time = time.time() - start
    
    start = time.time()
    decrypted = decrypt_message(ciphertext, password, salt, iv)
    decrypt_time = time.time() - start
    
    success = decrypted == message
    print(f"   Message size: {len(message)} bytes")
    print(f"   Encrypt time: {encrypt_time:.3f}s")
    print(f"   Decrypt time: {decrypt_time:.3f}s")
    print(f"   Match: {success}")
    return success

def test_encryption_unicode():
    """Test encryption with Unicode characters"""
    message = "Hello 世界 🌍 Привет مرحبا"
    password = "unicode_test"
    
    ciphertext, salt, iv = encrypt_message(message, password)
    decrypted = decrypt_message(ciphertext, password, salt, iv)
    
    success = decrypted == message
    print(f"   Original: {message}")
    print(f"   Decrypted: {decrypted}")
    print(f"   Match: {success}")
    return success

def test_encryption_wrong_password():
    """Test decryption with wrong password"""
    message = "Secret message"
    password = "correct_password"
    wrong_password = "wrong_password"
    
    ciphertext, salt, iv = encrypt_message(message, password)
    try:
        decrypted = decrypt_message(ciphertext, wrong_password, salt, iv)
        print(f"   ❌ Should have failed with wrong password")
        return False
    except Exception as e:
        print(f"   ✅ Correctly rejected wrong password: {type(e).__name__}")
        return True

# ============================================================================
# MODULE 3: IMAGE PROCESSING TESTS
# ============================================================================

def test_dwt_reconstruction():
    """Test DWT decomposition and reconstruction"""
    import cv2
    
    img = cv2.imread('test_lena.png', cv2.IMREAD_GRAYSCALE)
    bands = dwt_decompose(img)
    reconstructed = dwt_reconstruct(bands)
    
    psnr_value = psnr(img, reconstructed)
    success = psnr_value > 100  # Should be near-perfect
    
    print(f"   Original shape: {img.shape}")
    print(f"   Reconstructed shape: {reconstructed.shape}")
    print(f"   PSNR: {psnr_value:.2f} dB")
    print(f"   Quality: {'Excellent' if success else 'Poor'}")
    return success

def test_dwt_band_access():
    """Test access to DWT bands"""
    import cv2
    
    img = cv2.imread('test_lena.png', cv2.IMREAD_GRAYSCALE)
    bands = dwt_decompose(img)
    
    required_bands = ['HH1', 'HL1', 'LH1', 'HH2', 'HL2', 'LH2', 'LL2']
    success = all(band in bands for band in required_bands)
    
    print(f"   Available bands: {list(bands.keys())}")
    print(f"   All required bands present: {success}")
    
    for band_name in required_bands:
        if band_name in bands:
            print(f"   {band_name}: shape {bands[band_name].shape}")
    
    return success

# ============================================================================
# MODULE 4: COMPRESSION TESTS
# ============================================================================

def test_compression_basic():
    """Test basic Huffman compression"""
    message = b"AAAABBBCCD"
    
    tree, compressed = compress_huffman(message)
    decompressed = decompress_huffman(compressed, tree)
    
    ratio = len(compressed) / len(message) * 100
    success = decompressed == message
    
    print(f"   Original: {len(message)} bytes")
    print(f"   Compressed: {len(compressed)} bytes")
    print(f"   Compression ratio: {ratio:.1f}%")
    print(f"   Decompressed matches: {success}")
    return success

def test_compression_random():
    """Test compression with random data (worst case)"""
    import random
    message = bytes([random.randint(0, 255) for _ in range(1000)])
    
    tree, compressed = compress_huffman(message)
    decompressed = decompress_huffman(compressed, tree)
    
    ratio = len(compressed) / len(message) * 100
    success = decompressed == message
    
    print(f"   Original: {len(message)} bytes")
    print(f"   Compressed: {len(compressed)} bytes")
    print(f"   Compression ratio: {ratio:.1f}%")
    print(f"   Decompressed matches: {success}")
    return success

def test_payload_format():
    """Test payload creation and parsing"""
    message = b"Test message for payload"
    tree, compressed = compress_huffman(message)
    
    payload = create_payload(message, tree, compressed)
    msg_len, tree_extracted, compressed_extracted = parse_payload(payload)
    
    success = (msg_len == len(message) and 
               tree_extracted == tree and 
               compressed_extracted == compressed)
    
    print(f"   Message length: {msg_len}")
    print(f"   Tree size: {len(tree_extracted)} bytes")
    print(f"   Compressed size: {len(compressed_extracted)} bytes")
    print(f"   Payload parsing correct: {success}")
    return success

# ============================================================================
# MODULE 5: EMBEDDING TESTS
# ============================================================================

def test_embedding_basic():
    """Test basic message embedding and extraction"""
    message = "Hello, World!"
    password = "test123"
    cover_image = "test_lena.png"
    stego_image = "test_stego_basic.png"
    
    # Embed
    capacity = calculate_capacity(cover_image)
    embed_message(message, password, cover_image, stego_image)
    
    # Extract
    extracted = extract_message(password, stego_image)
    
    success = extracted == message
    print(f"   Original: '{message}'")
    print(f"   Extracted: '{extracted}'")
    print(f"   Capacity: {capacity} bytes")
    print(f"   Match: {success}")
    return success

def test_embedding_empty():
    """Test embedding empty message"""
    message = ""
    password = "test123"
    cover_image = "test_lena.png"
    stego_image = "test_stego_empty.png"
    
    embed_message(message, password, cover_image, stego_image)
    extracted = extract_message(password, stego_image)
    
    success = extracted == message
    print(f"   Empty message embedding: {success}")
    return success

def test_embedding_multiline():
    """Test embedding multi-line message"""
    message = """Line 1
Line 2
Line 3"""
    password = "multiline_test"
    cover_image = "test_lena.png"
    stego_image = "test_stego_multiline.png"
    
    embed_message(message, password, cover_image, stego_image)
    extracted = extract_message(password, stego_image)
    
    success = extracted == message
    print(f"   Original lines: {message.count(chr(10)) + 1}")
    print(f"   Extracted lines: {extracted.count(chr(10)) + 1}")
    print(f"   Match: {success}")
    return success

def test_embedding_special_chars():
    """Test embedding special characters"""
    message = "Special: !@#$%^&*()_+-=[]{}|;':\",./<>?"
    password = "special_test"
    cover_image = "test_lena.png"
    stego_image = "test_stego_special.png"
    
    embed_message(message, password, cover_image, stego_image)
    extracted = extract_message(password, stego_image)
    
    success = extracted == message
    print(f"   Original: '{message}'")
    print(f"   Extracted: '{extracted}'")
    print(f"   Match: {success}")
    return success

def test_embedding_json():
    """Test embedding JSON data"""
    message = '{"name": "Test", "value": 123, "active": true}'
    password = "json_test"
    cover_image = "test_lena.png"
    stego_image = "test_stego_json.png"
    
    embed_message(message, password, cover_image, stego_image)
    extracted = extract_message(password, stego_image)
    
    success = extracted == message
    print(f"   JSON valid: {success}")
    if success:
        import json
        parsed = json.loads(extracted)
        print(f"   Parsed: {parsed}")
    return success

def test_embedding_numbers():
    """Test embedding numeric data"""
    message = "123456789012345678901234567890"
    password = "numbers_test"
    cover_image = "test_lena.png"
    stego_image = "test_stego_numbers.png"
    
    embed_message(message, password, cover_image, stego_image)
    extracted = extract_message(password, stego_image)
    
    success = extracted == message
    print(f"   Number string length: {len(message)}")
    print(f"   Match: {success}")
    return success

def test_embedding_different_images():
    """Test embedding in different cover images"""
    message = "Testing different images"
    password = "image_test"
    
    images = ["test_lena.png", "test_peppers.png"]
    results = []
    
    for img in images:
        if not os.path.exists(img):
            print(f"   ⚠️  Skipping {img} (not found)")
            continue
            
        stego = f"test_stego_{os.path.basename(img)}"
        embed_message(message, password, img, stego)
        extracted = extract_message(password, stego)
        
        match = extracted == message
        results.append(match)
        print(f"   {img}: {'✓' if match else '✗'}")
    
    return all(results) if results else False

def test_embedding_psnr():
    """Test PSNR of stego image"""
    import cv2
    
    message = "Quality test message"
    password = "psnr_test"
    cover_image = "test_lena.png"
    stego_image = "test_stego_psnr.png"
    
    embed_message(message, password, cover_image, stego_image)
    
    cover = cv2.imread(cover_image, cv2.IMREAD_GRAYSCALE)
    stego = cv2.imread(stego_image, cv2.IMREAD_GRAYSCALE)
    
    psnr_value = psnr(cover, stego)
    success = psnr_value > 50  # Should be > 50 dB
    
    print(f"   PSNR: {psnr_value:.2f} dB")
    print(f"   Quality: {'Excellent (>50dB)' if success else 'Poor (<50dB)'}")
    return success

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_integration_full_pipeline():
    """Test complete pipeline: encrypt → compress → embed → extract → decompress → decrypt"""
    original_message = "Full pipeline integration test!"
    password = "pipeline_test_123"
    cover_image = "test_lena.png"
    stego_image = "test_stego_pipeline.png"
    
    print(f"   Original message: '{original_message}'")
    
    # Full pipeline embed
    embed_message(original_message, password, cover_image, stego_image)
    print(f"   ✓ Embedded successfully")
    
    # Full pipeline extract
    extracted_message = extract_message(password, stego_image)
    print(f"   ✓ Extracted: '{extracted_message}'")
    
    success = extracted_message == original_message
    print(f"   Pipeline integrity: {success}")
    return success

def test_integration_wrong_password_extract():
    """Test extraction with wrong password"""
    message = "Secret message"
    correct_password = "correct_pass"
    wrong_password = "wrong_pass"
    cover_image = "test_lena.png"
    stego_image = "test_stego_wrong_pass.png"
    
    embed_message(message, correct_password, cover_image, stego_image)
    
    try:
        extracted = extract_message(wrong_password, stego_image)
        # If it extracts something but it's garbage, that's expected
        match = extracted == message
        print(f"   Extracted with wrong password: '{extracted[:50]}...'")
        print(f"   Matches original: {match}")
        return not match  # Should NOT match
    except Exception as e:
        print(f"   ✓ Correctly failed: {type(e).__name__}")
        return True

# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_edge_single_char():
    """Test embedding single character"""
    message = "X"
    password = "single_char"
    cover_image = "test_lena.png"
    stego_image = "test_stego_single.png"
    
    embed_message(message, password, cover_image, stego_image)
    extracted = extract_message(password, stego_image)
    
    success = extracted == message
    print(f"   Single char '{message}': {success}")
    return success

def test_edge_repeated_chars():
    """Test embedding repeated characters (best compression)"""
    message = "A" * 100
    password = "repeated_test"
    cover_image = "test_lena.png"
    stego_image = "test_stego_repeated.png"
    
    embed_message(message, password, cover_image, stego_image)
    extracted = extract_message(password, stego_image)
    
    success = extracted == message
    print(f"   100 repeated 'A': {success}")
    return success

# ============================================================================
# RUN ALL TESTS
# ============================================================================

print("\n" + "="*80)
print("MODULE 1: ENCRYPTION TESTS")
print("="*80)
run_test("Basic Encryption/Decryption", test_encryption_basic)
run_test("Empty Message Encryption", test_encryption_empty)
run_test("Large Message (1MB) Encryption", test_encryption_large)
run_test("Unicode Characters Encryption", test_encryption_unicode)
run_test("Wrong Password Rejection", test_encryption_wrong_password)

print("\n" + "="*80)
print("MODULE 3: IMAGE PROCESSING TESTS")
print("="*80)
run_test("DWT Decomposition/Reconstruction", test_dwt_reconstruction)
run_test("DWT Band Access", test_dwt_band_access)

print("\n" + "="*80)
print("MODULE 4: COMPRESSION TESTS")
print("="*80)
run_test("Basic Huffman Compression", test_compression_basic)
run_test("Random Data Compression", test_compression_random)
run_test("Payload Format", test_payload_format)

print("\n" + "="*80)
print("MODULE 5: EMBEDDING TESTS")
print("="*80)
run_test("Basic Message Embedding", test_embedding_basic)
run_test("Empty Message Embedding", test_embedding_empty)
run_test("Multi-line Message", test_embedding_multiline)
run_test("Special Characters", test_embedding_special_chars)
run_test("JSON Data Embedding", test_embedding_json)
run_test("Numeric Data", test_embedding_numbers)
run_test("Different Cover Images", test_embedding_different_images)
run_test("PSNR Quality Check", test_embedding_psnr)

print("\n" + "="*80)
print("INTEGRATION TESTS")
print("="*80)
run_test("Full Pipeline Test", test_integration_full_pipeline)
run_test("Wrong Password Extraction", test_integration_wrong_password_extract)

print("\n" + "="*80)
print("EDGE CASE TESTS")
print("="*80)
run_test("Single Character", test_edge_single_char)
run_test("Repeated Characters", test_edge_repeated_chars)

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "="*80)
print("📊 TEST SUMMARY")
print("="*80)
print(f"Total Tests: {test_results['total']}")
print(f"✅ Passed: {test_results['passed']}")
print(f"❌ Failed: {test_results['failed']}")
print(f"Success Rate: {test_results['passed']/test_results['total']*100:.1f}%")
print("="*80)

if test_results['failed'] == 0:
    print("🎉 ALL TESTS PASSED! System is fully functional.")
else:
    print(f"⚠️  {test_results['failed']} test(s) failed. Review output above.")

print("\n✅ Testing complete!")
