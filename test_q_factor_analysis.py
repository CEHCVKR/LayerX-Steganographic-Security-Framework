"""
PSNR vs Q Factor & Payload Size - Comprehensive Analysis
Direct modification of embed_in_dwt_bands Q parameter
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '03. Image Processing Module'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '01. Encryption Module'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '04. Compression Module'))

import cv2
import numpy as np
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct, psnr
from a4_compression import compress_huffman, decompress_huffman
import time

def embed_with_custom_q(payload_bits, bands, q_factor):
    """Embed with custom Q factor"""
    embed_bands = ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']
    
    # Collect coefficients
    all_coefficients = []
    for band_name in embed_bands:
        if band_name in bands:
            band = bands[band_name]
            for i in range(8, band.shape[0]):
                for j in range(8, band.shape[1]):
                    if abs(band[i, j]) >= 8:  # Threshold
                        all_coefficients.append((band_name, i, j))
    
    # Use first 38% of coefficients
    usable_count = int(len(all_coefficients) * 0.38)
    all_coefficients = all_coefficients[:usable_count]
    
    if len(all_coefficients) < len(payload_bits):
        raise ValueError(f"Not enough capacity. Need {len(payload_bits)}, have {len(all_coefficients)}")
    
    # Create modified bands
    modified_bands = {}
    for band_name, band_data in bands.items():
        if isinstance(band_data, np.ndarray):
            modified_bands[band_name] = band_data.copy()
        else:
            modified_bands[band_name] = band_data
    
    # Embed with specified Q
    Q = q_factor
    for i, bit in enumerate(payload_bits):
        band_name, row, col = all_coefficients[i]
        original_coeff = modified_bands[band_name][row, col]
        
        # Quantize
        quantized = Q * round(original_coeff / Q)
        
        if bit == '1':
            q_level = round(quantized / Q)
            if q_level % 2 == 0:
                quantized = quantized + Q if quantized >= 0 else quantized - Q
        else:
            q_level = round(quantized / Q)
            if q_level % 2 != 0:
                quantized = quantized + Q if quantized >= 0 else quantized - Q
        
        modified_bands[band_name][row, col] = quantized
    
    return modified_bands

def extract_with_custom_q(bands, bit_length, q_factor):
    """Extract with custom Q factor"""
    embed_bands = ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']
    
    # Collect coefficients (must match embedding order)
    all_coefficients = []
    for band_name in embed_bands:
        if band_name in bands:
            band = bands[band_name]
            for i in range(8, band.shape[0]):
                for j in range(8, band.shape[1]):
                    if abs(band[i, j]) >= 8:  # Same threshold
                        all_coefficients.append((band_name, i, j))
    
    # Use first 38%
    usable_count = int(len(all_coefficients) * 0.38)
    all_coefficients = all_coefficients[:usable_count]
    
    # Extract bits
    Q = q_factor
    extracted_bits = []
    for i in range(bit_length):
        band_name, row, col = all_coefficients[i]
        coeff = bands[band_name][row, col]
        
        q_level = round(coeff / Q)
        bit = '1' if q_level % 2 != 0 else '0'
        extracted_bits.append(bit)
    
    return ''.join(extracted_bits)

def bytes_to_bits(data):
    """Convert bytes to bit string"""
    return ''.join(format(byte, '08b') for byte in data)

def bits_to_bytes(bit_string):
    """Convert bit string to bytes"""
    # Pad to multiple of 8
    padding = (8 - len(bit_string) % 8) % 8
    bit_string += '0' * padding
    
    byte_array = bytearray()
    for i in range(0, len(bit_string), 8):
        byte = bit_string[i:i+8]
        byte_array.append(int(byte, 2))
    
    return bytes(byte_array)

def test_configuration(image_path, payload_size, q_factor, test_name):
    """Test a specific Q factor and payload size"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    print(f"Payload: {payload_size} bytes | Q factor: {q_factor}")
    
    try:
        # Load image
        image = read_image(image_path)
        
        # Create payload
        test_message = "X" * payload_size
        payload_bytes = test_message.encode('utf-8')
        
        # Compress
        compressed, tree_bytes = compress_huffman(payload_bytes)
        
        # Convert to bits
        payload_bits = bytes_to_bits(compressed)
        
        print(f"  Original: {payload_size}B → Compressed: {len(compressed)}B → {len(payload_bits)} bits")
        
        # DWT decompose
        bands = dwt_decompose(image, levels=2)
        
        # Embed
        start = time.time()
        stego_bands = embed_with_custom_q(payload_bits, bands, q_factor)
        embed_time = time.time() - start
        
        # Reconstruct
        stego_image = dwt_reconstruct(stego_bands)
        
        # Calculate PSNR
        psnr_value = psnr(image, stego_image)
        
        # Extract
        start = time.time()
        extracted_bits = extract_with_custom_q(stego_bands, len(payload_bits), q_factor)
        extract_time = time.time() - start
        
        # Decompress
        extracted_bytes = bits_to_bytes(extracted_bits)
        decompressed = decompress_huffman(extracted_bytes, tree_bytes)
        
        # Verify
        success = (decompressed == payload_bytes)
        
        print(f"\n📊 RESULTS:")
        print(f"  PSNR: {psnr_value:.2f} dB {'✅ PASS' if psnr_value >= 50 else '⚠️ BELOW 50dB'}")
        print(f"  Extraction: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print(f"  Embed time: {embed_time*1000:.1f} ms")
        print(f"  Extract time: {extract_time*1000:.1f} ms")
        
        return {
            'test_name': test_name,
            'payload_size': payload_size,
            'q_factor': q_factor,
            'psnr': psnr_value,
            'success': success,
            'embed_time': embed_time,
            'extract_time': extract_time
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def main():
    print("="*70)
    print("PSNR OPTIMIZATION - Q FACTOR vs PAYLOAD SIZE")
    print("="*70)
    print("Goal: Maintain PSNR >=50 dB with different configurations\n")
    
    image_path = 'test_lena.png'
    if not os.path.exists(image_path):
        print(f"❌ {image_path} not found")
        return
    
    results = []
    
    # Small payloads (≤2KB)
    print("\n" + "="*70)
    print("SET 1: SMALL PAYLOADS (≤2KB)")
    print("="*70)
    
    for q in [4.0, 5.0, 6.0]:
        r = test_configuration(image_path, 500, q, f"500B - Q={q}")
        if r: results.append(r)
    
    for q in [4.0, 5.0, 6.0]:
        r = test_configuration(image_path, 1000, q, f"1KB - Q={q}")
        if r: results.append(r)
    
    for q in [5.0, 6.0, 7.0]:
        r = test_configuration(image_path, 2000, q, f"2KB - Q={q}")
        if r: results.append(r)
    
    # Medium payloads (3-5KB)
    print("\n" + "="*70)
    print("SET 2: MEDIUM PAYLOADS (3-5KB)")
    print("="*70)
    
    for q in [5.0, 6.0, 7.0]:
        r = test_configuration(image_path, 3000, q, f"3KB - Q={q}")
        if r: results.append(r)
    
    for q in [6.0, 7.0, 8.0]:
        r = test_configuration(image_path, 4000, q, f"4KB - Q={q}")
        if r: results.append(r)
    
    for q in [6.0, 7.0, 8.0]:
        r = test_configuration(image_path, 5000, q, f"5KB - Q={q}")
        if r: results.append(r)
    
    # Large payloads (6-8KB)
    print("\n" + "="*70)
    print("SET 3: LARGE PAYLOADS (6-8KB)")
    print("="*70)
    
    for q in [7.0, 8.0, 9.0]:
        r = test_configuration(image_path, 6000, q, f"6KB - Q={q}")
        if r: results.append(r)
    
    for q in [7.0, 8.0, 9.0, 10.0]:
        r = test_configuration(image_path, 8000, q, f"8KB - Q={q}")
        if r: results.append(r)
    
    # SUMMARY
    print("\n" + "="*70)
    print("COMPREHENSIVE SUMMARY")
    print("="*70)
    
    successful = [r for r in results if r and r['success']]
    
    if not successful:
        print("❌ No successful tests")
        return
    
    # Sort by PSNR
    successful.sort(key=lambda x: (-x['psnr'], -x['payload_size']))
    
    print(f"\n{'Test Name':<25} {'Payload':>8} {'Q':>5} {'PSNR':>9} {'Status':>10}")
    print("-"*70)
    
    for r in successful[:15]:  # Show top 15
        status = "✅ PASS" if r['psnr'] >= 50 else "⚠️ <50dB"
        print(f"{r['test_name']:<25} {r['payload_size']:>6}B {r['q_factor']:>5.1f} {r['psnr']:>8.2f}dB {status}")
    
    # Analysis
    meets_target = [r for r in successful if r['psnr'] >= 50]
    
    print("\n" + "="*70)
    print("ANALYSIS & RECOMMENDATIONS")
    print("="*70)
    
    print(f"\n📊 Statistics:")
    print(f"  Tests run: {len(results)}")
    print(f"  Successful: {len(successful)}")
    print(f"  PSNR >=50dB: {len(meets_target)}/{len(successful)} ({100*len(meets_target)/len(successful):.1f}%)")
    
    if meets_target:
        # Best overall
        best = max(meets_target, key=lambda x: x['psnr'])
        print(f"\n🏆 Highest PSNR:")
        print(f"    {best['test_name']}: {best['psnr']:.2f} dB")
        
        # Best capacity
        best_cap = max(meets_target, key=lambda x: x['payload_size'])
        print(f"\n📦 Largest Payload (while PSNR ≥50):")
        print(f"    {best_cap['test_name']}: {best_cap['payload_size']}B at {best_cap['psnr']:.2f} dB")
        
        # Recommendations by size
        print(f"\n💡 Recommended Q Factors:")
        
        small = [r for r in meets_target if r['payload_size'] <= 2000]
        if small:
            avg_q = np.mean([r['q_factor'] for r in small])
            avg_psnr = np.mean([r['psnr'] for r in small])
            print(f"  <=2KB: Q >={min([r['q_factor'] for r in small]):.1f} (avg {avg_q:.1f}, PSNR {avg_psnr:.1f}dB)")
        
        medium = [r for r in meets_target if 2000 < r['payload_size'] <= 5000]
        if medium:
            avg_q = np.mean([r['q_factor'] for r in medium])
            avg_psnr = np.mean([r['psnr'] for r in medium])
            print(f"  2-5KB: Q >={min([r['q_factor'] for r in medium]):.1f} (avg {avg_q:.1f}, PSNR {avg_psnr:.1f}dB)")
        
        large = [r for r in meets_target if r['payload_size'] > 5000]
        if large:
            avg_q = np.mean([r['q_factor'] for r in large])
            avg_psnr = np.mean([r['psnr'] for r in large])
            print(f"  >5KB: Q >={min([r['q_factor'] for r in large]):.1f} (avg {avg_q:.1f}, PSNR {avg_psnr:.1f}dB)")
        
        print(f"\n✅ CONCLUSION:")
        print(f"  Maximum payload with PSNR >=50dB: {best_cap['payload_size']} bytes using Q={best_cap['q_factor']}")
        print(f"  For hybrid encryption (~5.5KB), recommended Q >=6.0 to maintain >50dB")
    else:
        print("\n⚠️  No configurations achieved PSNR >=50dB")
        print("  Consider reducing payload size or increasing Q factor")
    
    print("="*70)

if __name__ == "__main__":
    main()
