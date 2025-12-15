"""
LayerX Steganographic Security Framework - Full Pipeline Test
Author: Member A
Description: End-to-end test of the complete steganography pipeline

Pipeline Flow:
1. Encrypt message with password → (ciphertext, salt, iv)
2. Compress ciphertext → (compressed, tree)  
3. Create payload → [msg_len][tree][compressed]
4. Embed payload in cover image → stego image
5. Extract payload from stego image
6. Decompress → original ciphertext
7. Decrypt → original message

Target: Perfect recovery + PSNR >40dB + <500ms total time
"""

import os
import sys
import time
import traceback
from typing import List, Dict

# Add all module paths
module_paths = [
    "01. Encryption Module",
    "02. Key Management Module", 
    "03. Image Processing Module",
    "04. Compression Module",
    "05. Embedding and Extraction Module"
]

for module_path in module_paths:
    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), module_path)
    if full_path not in sys.path:
        sys.path.append(full_path)

# Import all modules
from a1_encryption import encrypt_message, decrypt_message
from a2_key_management import KeyManager
from a3_image_processing import create_test_images, get_capacity
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import embed, extract, psnr_images


def time_operation(func, *args, **kwargs):
    """Time a function execution and return result and duration in ms"""
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000
    return result, duration_ms


def test_pipeline():
    """Run complete pipeline test"""
    print("🚀 === LayerX Steganographic Security Framework ===")
    print("    Full Pipeline Test - Member A Implementation")
    print("=" * 60)
    
    # Test configuration
    test_cases = [
        ("Secret test", "Basic test"),
        ("", "Empty message"),
        ("Hello World!", "Short message"),
        ("This is a longer test message with multiple words and punctuation!", "Medium message"),
        ("A" * 100, "100 char repeat"),
        ("JSON: {\"key\": \"value\", \"array\": [1,2,3], \"nested\": {\"a\": \"b\"}}", "JSON data"),
        ("Multi\nLine\nMessage\nWith\nBreaks", "Multi-line"),
        ("Special chars: àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ", "Unicode"),
        ("Binary-like: \x00\x01\x02\x03\xFF\xFE\xFD\xFC", "Binary data"),
        ("X" * 500, "Large message (500 chars)")
    ]
    
    password = "test_password_123"
    
    # Setup test images
    test_images = ["test_lena.png", "test_peppers.png"]
    
    print("🖼️  Setting up test images...")
    if not any(os.path.exists(img) for img in test_images):
        create_test_images()
        print("✅ Created test images")
    else:
        print("✅ Test images already exist")
    
    # Find available images
    available_images = [img for img in test_images if os.path.exists(img)]
    if not available_images:
        print("❌ No test images available!")
        return False
    
    print(f"🖼️  Using images: {', '.join(available_images)}")
    
    # Results storage
    results = []
    total_tests = len(test_cases) * len(available_images)
    current_test = 0
    
    print(f"\n🧪 Running {total_tests} pipeline tests...")
    print("-" * 60)
    
    for cover_image in available_images:
        print(f"\n📸 Testing with {cover_image}:")
        
        # Check image capacity
        from a3_image_processing import read_image
        image = read_image(cover_image)
        max_capacity = get_capacity(image.shape, 'dwt')
        print(f"   Embedding capacity: {max_capacity} bytes")
        
        for message, description in test_cases:
            current_test += 1
            print(f"\n   Test {current_test:2d}/{total_tests}: {description}")
            print(f"      Message: '{message[:50]}{'...' if len(message) > 50 else ''}'")
            
            try:
                # === FORWARD PIPELINE ===
                total_start = time.perf_counter()
                
                # Step 1: Encryption
                (ciphertext, salt, iv), encrypt_time = time_operation(
                    encrypt_message, message, password
                )
                
                # Step 2: Compression  
                (compressed, tree), compress_time = time_operation(
                    compress_huffman, ciphertext
                )
                
                # Step 3: Create payload
                payload, payload_time = time_operation(
                    create_payload, ciphertext, tree, compressed
                )
                
                # Check if payload fits
                if len(payload) > max_capacity:
                    print(f"      ⚠️  SKIPPED: Payload too large ({len(payload)} > {max_capacity} bytes)")
                    continue
                
                # Step 4: Embedding
                stego_path = f"temp_stego_{current_test}.png"
                embed_success, embed_time = time_operation(
                    embed, payload, cover_image, stego_path
                )
                
                if not embed_success:
                    print(f"      ❌ Embedding failed!")
                    continue
                
                # === REVERSE PIPELINE ===
                
                # Step 5: Extraction
                extracted_payload, extract_time = time_operation(
                    extract, stego_path
                )
                
                # Step 6: Parse payload
                (msg_len, tree_extracted, compressed_extracted), parse_time = time_operation(
                    parse_payload, extracted_payload
                )
                
                # Step 7: Decompression
                ciphertext_extracted, decompress_time = time_operation(
                    decompress_huffman, compressed_extracted, tree_extracted
                )
                
                # Step 8: Decryption
                message_extracted, decrypt_time = time_operation(
                    decrypt_message, ciphertext_extracted, password, salt, iv
                )
                
                total_end = time.perf_counter()
                total_time = (total_end - total_start) * 1000
                
                # === VERIFICATION ===
                
                # Check round-trip accuracy
                if message_extracted != message:
                    print(f"      ❌ Round-trip FAILED!")
                    print(f"         Original: {len(message)} chars")
                    print(f"         Extracted: {len(message_extracted)} chars")
                    continue
                
                # Calculate PSNR
                psnr_value = psnr_images(cover_image, stego_path)
                
                # Calculate compression ratio
                if len(ciphertext) > 0:
                    compression_ratio = len(compressed) / len(ciphertext) * 100
                else:
                    compression_ratio = 0
                
                # === RESULTS ===
                
                result = {
                    'test_id': current_test,
                    'image': cover_image,
                    'description': description,
                    'message_len': len(message),
                    'ciphertext_len': len(ciphertext),
                    'compressed_len': len(compressed),
                    'tree_len': len(tree),
                    'payload_len': len(payload),
                    'compression_ratio': compression_ratio,
                    'psnr': psnr_value,
                    'times': {
                        'encrypt': encrypt_time,
                        'compress': compress_time,
                        'payload': payload_time,
                        'embed': embed_time,
                        'extract': extract_time,
                        'parse': parse_time,
                        'decompress': decompress_time,
                        'decrypt': decrypt_time,
                        'total': total_time
                    },
                    'success': True
                }
                
                results.append(result)
                
                # Print results
                print(f"      ✅ SUCCESS!")
                print(f"         Round-trip: Perfect match")
                print(f"         PSNR: {psnr_value:.2f}dB {'✅' if psnr_value > 40 else '❌ (<40dB)'}")
                print(f"         Compression: {compression_ratio:.1f}% ratio")
                print(f"         Payload: {len(payload)} bytes")
                print(f"         Total time: {total_time:.1f}ms {'✅' if total_time < 500 else '⚠️ (>500ms)'}")
                print(f"         Breakdown: E={encrypt_time:.1f} C={compress_time:.1f} "
                      f"Em={embed_time:.1f} Ex={extract_time:.1f} D={decompress_time:.1f} De={decrypt_time:.1f}")
                
                # Cleanup
                if os.path.exists(stego_path):
                    os.remove(stego_path)
                    
            except Exception as e:
                print(f"      ❌ ERROR: {str(e)}")
                traceback.print_exc()
                continue
    
    # === FINAL SUMMARY ===
    
    print("\n" + "=" * 60)
    print("📊 PIPELINE TEST SUMMARY")
    print("=" * 60)
    
    if not results:
        print("❌ No successful tests!")
        return False
    
    successful_tests = len(results)
    avg_psnr = sum(r['psnr'] for r in results) / len(results)
    min_psnr = min(r['psnr'] for r in results)
    max_psnr = max(r['psnr'] for r in results)
    
    avg_total_time = sum(r['times']['total'] for r in results) / len(results)
    max_total_time = max(r['times']['total'] for r in results)
    
    avg_compression = sum(r['compression_ratio'] for r in results) / len(results)
    
    print(f"✅ Successful tests: {successful_tests}/{total_tests}")
    print(f"📈 PSNR Statistics:")
    print(f"   Average: {avg_psnr:.2f}dB")
    print(f"   Range: {min_psnr:.2f}dB - {max_psnr:.2f}dB")
    print(f"   Target >40dB: {'✅ PASSED' if min_psnr > 40 else '❌ FAILED'}")
    
    print(f"⏱️  Performance:")
    print(f"   Average total time: {avg_total_time:.1f}ms")
    print(f"   Maximum time: {max_total_time:.1f}ms") 
    print(f"   Target <500ms: {'✅ PASSED' if max_total_time < 500 else '❌ FAILED'}")
    
    print(f"🗜️  Compression:")
    print(f"   Average ratio: {avg_compression:.1f}%")
    
    # Performance breakdown
    print(f"\n⏱️  Average Time Breakdown:")
    avg_times = {}
    for step in ['encrypt', 'compress', 'embed', 'extract', 'decompress', 'decrypt']:
        avg_times[step] = sum(r['times'][step] for r in results) / len(results)
        print(f"   {step.capitalize():12s}: {avg_times[step]:6.1f}ms")
    
    # Test quality assessment
    quality_passed = min_psnr > 40
    performance_passed = max_total_time < 500
    functionality_passed = successful_tests == total_tests
    
    overall_passed = quality_passed and performance_passed and functionality_passed
    
    print(f"\n🎯 OVERALL ASSESSMENT:")
    print(f"   Functionality: {'✅ PASSED' if functionality_passed else '❌ FAILED'}")
    print(f"   Quality (PSNR): {'✅ PASSED' if quality_passed else '❌ FAILED'}")  
    print(f"   Performance: {'✅ PASSED' if performance_passed else '❌ FAILED'}")
    print(f"   OVERALL: {'🎉 READY FOR MEMBER B!' if overall_passed else '⚠️ NEEDS FIXES'}")
    
    if overall_passed:
        print("\n🔧 Member B can now build optimization and security on this foundation!")
        print("📤 Share this output with team daily as requested.")
    
    return overall_passed


if __name__ == "__main__":
    success = test_pipeline()
    exit(0 if success else 1)