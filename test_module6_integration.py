"""
Test Module 6 Integration - Compare Optimization Methods
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
import cv2

print("="*80)
print("Module 6 Integration Test - Optimization Comparison")
print("="*80)

# Test message
message = "Hello World! Testing optimization methods."
password = "test123"

# Encrypt and compress
ciphertext, salt, iv = encrypt_message(message, password)
compressed, tree = compress_huffman(ciphertext)
payload = create_payload(ciphertext, tree, compressed)

print(f"\nTest Message: '{message}'")
print(f"Payload size: {len(payload)} bytes ({len(payload)*8} bits)")

# Test capacity
test_img = read_image('test_lena.png')
capacity = get_capacity(test_img.shape[:2], 'dwt')
print(f"Image capacity: {capacity} bytes")

results = {}

# Test 1: Fixed (Default) Method
print("\n" + "="*80)
print("[Method 1] FIXED - Sequential Positional Selection")
print("="*80)
try:
    start = time.time()
    embed(payload, 'test_lena.png', 'test_opt_fixed.png', optimization='fixed')
    embed_time = time.time() - start
    
    start = time.time()
    extracted = extract('test_opt_fixed.png')
    extract_time = time.time() - start
    
    msg_len, tree_ext, compressed_ext = parse_payload(extracted)
    ciphertext_ext = decompress_huffman(compressed_ext, tree_ext)
    decrypted = decrypt_message(ciphertext_ext, password, salt, iv)
    
    # Calculate PSNR
    cover = cv2.imread('test_lena.png', cv2.IMREAD_GRAYSCALE)
    stego = cv2.imread('test_opt_fixed.png', cv2.IMREAD_GRAYSCALE)
    psnr_val = psnr(cover, stego)
    
    success = (decrypted == message)
    results['fixed'] = {
        'success': success,
        'psnr': psnr_val,
        'embed_time': embed_time,
        'extract_time': extract_time
    }
    
    print(f"{'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"PSNR: {psnr_val:.2f} dB")
    print(f"Embedding time: {embed_time:.3f}s")
    print(f"Extraction time: {extract_time:.3f}s")
    
except Exception as e:
    print(f"❌ FAILED - {e}")
    results['fixed'] = {'success': False, 'error': str(e)}

# Test 2: Chaos Method
print("\n" + "="*80)
print("[Method 2] CHAOS - Logistic Map Selection (Steganalysis-Resistant)")
print("="*80)
try:
    start = time.time()
    embed(payload, 'test_lena.png', 'test_opt_chaos.png', optimization='chaos')
    embed_time = time.time() - start
    
    start = time.time()
    extracted = extract('test_opt_chaos.png', optimization='chaos')
    extract_time = time.time() - start
    
    msg_len, tree_ext, compressed_ext = parse_payload(extracted)
    ciphertext_ext = decompress_huffman(compressed_ext, tree_ext)
    decrypted = decrypt_message(ciphertext_ext, password, salt, iv)
    
    # Calculate PSNR
    cover = cv2.imread('test_lena.png', cv2.IMREAD_GRAYSCALE)
    stego = cv2.imread('test_opt_chaos.png', cv2.IMREAD_GRAYSCALE)
    psnr_val = psnr(cover, stego)
    
    success = (decrypted == message)
    results['chaos'] = {
        'success': success,
        'psnr': psnr_val,
        'embed_time': embed_time,
        'extract_time': extract_time
    }
    
    print(f"{'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"PSNR: {psnr_val:.2f} dB")
    print(f"Embedding time: {embed_time:.3f}s")
    print(f"Extraction time: {extract_time:.3f}s")
    
except Exception as e:
    print(f"❌ FAILED - {e}")
    import traceback
    traceback.print_exc()
    results['chaos'] = {'success': False, 'error': str(e)}

# Test 3: ACO Method
print("\n" + "="*80)
print("[Method 3] ACO - Robustness-Optimized Selection")
print("="*80)
try:
    start = time.time()
    embed(payload, 'test_lena.png', 'test_opt_aco.png', optimization='aco')
    embed_time = time.time() - start
    
    start = time.time()
    extracted = extract('test_opt_aco.png', optimization='aco')
    extract_time = time.time() - start
    
    msg_len, tree_ext, compressed_ext = parse_payload(extracted)
    ciphertext_ext = decompress_huffman(compressed_ext, tree_ext)
    decrypted = decrypt_message(ciphertext_ext, password, salt, iv)
    
    # Calculate PSNR
    cover = cv2.imread('test_lena.png', cv2.IMREAD_GRAYSCALE)
    stego = cv2.imread('test_opt_aco.png', cv2.IMREAD_GRAYSCALE)
    psnr_val = psnr(cover, stego)
    
    success = (decrypted == message)
    results['aco'] = {
        'success': success,
        'psnr': psnr_val,
        'embed_time': embed_time,
        'extract_time': extract_time
    }
    
    print(f"{'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"PSNR: {psnr_val:.2f} dB")
    print(f"Embedding time: {embed_time:.3f}s")
    print(f"Extraction time: {extract_time:.3f}s")
    
except Exception as e:
    print(f"❌ FAILED - {e}")
    import traceback
    traceback.print_exc()
    results['aco'] = {'success': False, 'error': str(e)}

# Summary Comparison
print("\n" + "="*80)
print("COMPARISON SUMMARY")
print("="*80)
print(f"{'Method':<15} {'Status':<15} {'PSNR (dB)':<15} {'Embed (s)':<15} {'Extract (s)':<15}")
print("-"*80)

for method in ['fixed', 'chaos', 'aco']:
    if method not in results:
        continue
    
    r = results[method]
    status = '✅ SUCCESS' if r.get('success') else '❌ FAILED'
    psnr_str = f"{r.get('psnr', 0):.2f}" if 'psnr' in r else 'N/A'
    embed_str = f"{r.get('embed_time', 0):.3f}" if 'embed_time' in r else 'N/A'
    extract_str = f"{r.get('extract_time', 0):.3f}" if 'extract_time' in r else 'N/A'
    
    print(f"{method.upper():<15} {status:<15} {psnr_str:<15} {embed_str:<15} {extract_str:<15}")

print("\n" + "="*80)
print("Analysis:")
print("="*80)
print("✅ FIXED: Simple, deterministic, baseline performance")
print("✅ CHAOS: Steganalysis-resistant, pseudo-random coefficient selection")
print("✅ ACO: Robustness-optimized, selects most stable coefficients")
print("\nRecommendation: Use 'chaos' for security, 'aco' for quality, 'fixed' for speed")
print("="*80)
