"""
PSNR Optimization Tests - Different Scenarios & Payload Sizes
Goal: Achieve PSNR >50 dB even with larger payloads
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '03. Image Processing Module'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '05. Embedding and Extraction Module'))

import cv2
import numpy as np
from a3_image_processing import read_image, dwt_decompose, dwt_reconstruct
from a5_embedding_extraction import embed_message, extract_message
import time

def calculate_psnr(original, stego):
    """Calculate PSNR between two images"""
    mse = np.mean((original.astype(float) - stego.astype(float))**2)
    if mse == 0:
        return float('inf')
    psnr = 10 * np.log10(255**2 / mse)
    return psnr

def test_scenario(image_path, payload_size, q_factor, coeff_percentage, threshold, bands, scenario_name):
    """Test a specific configuration"""
    print(f"\n{'='*70}")
    print(f"SCENARIO: {scenario_name}")
    print(f"{'='*70}")
    print(f"Payload size: {payload_size} bytes")
    print(f"Q factor: {q_factor}")
    print(f"Coefficient usage: {coeff_percentage}%")
    print(f"Threshold: {threshold}")
    print(f"Bands: {len(bands)}")
    
    try:
        # Load image
        image = read_image(image_path)
        if image is None:
            print("❌ Failed to load image")
            return None
        
        # Create test payload
        test_message = "X" * payload_size
        
        # Apply DWT
        coeffs = dwt_decompose(image, levels=2)
        
        # Backup original Q and threshold from module
        from a5_embedding_extraction import Q, THRESHOLD
        original_q = Q
        original_threshold = THRESHOLD
        
        # Temporarily modify parameters
        import a5_embedding_extraction as embed_module
        embed_module.Q = q_factor
        embed_module.THRESHOLD = threshold
        
        # Calculate capacity
        total_coeffs = 0
        for band_name in bands:
            if band_name == 'LL2':
                band = coeffs[1][0]
            elif band_name == 'LH1':
                band = coeffs[0][1][0]
            elif band_name == 'HL1':
                band = coeffs[0][1][1]
            elif band_name == 'HH1':
                band = coeffs[0][1][2]
            elif band_name == 'LH2':
                band = coeffs[1][1][0]
            elif band_name == 'HL2':
                band = coeffs[1][1][1]
            elif band_name == 'HH2':
                band = coeffs[1][1][2]
            else:
                continue
            
            # Count coefficients above threshold
            usable = np.sum(np.abs(band) >= threshold)
            total_coeffs += int(usable * (coeff_percentage / 100.0))
        
        capacity_bytes = (total_coeffs * 8) // 8
        
        print(f"Available capacity: {capacity_bytes} bytes")
        
        if payload_size > capacity_bytes:
            print(f"❌ Payload too large for capacity")
            # Restore original values
            embed_module.Q = original_q
            embed_module.THRESHOLD = original_threshold
            return None
        
        # Embed message
        start_time = time.time()
        stego_coeffs = embed_message(test_message, coeffs)
        embed_time = time.time() - start_time
        
        # Reconstruct image
        stego_image = dwt_reconstruct(stego_coeffs)
        stego_image = np.clip(stego_image, 0, 255).astype(np.uint8)
        
        # Calculate PSNR
        psnr = calculate_psnr(image, stego_image)
        
        # Extract and verify
        start_time = time.time()
        extracted = extract_message(stego_coeffs, len(test_message))
        extract_time = time.time() - start_time
        
        success = (extracted == test_message)
        
        # Restore original values
        embed_module.Q = original_q
        embed_module.THRESHOLD = original_threshold
        
        print(f"\n📊 RESULTS:")
        print(f"  PSNR: {psnr:.2f} dB {'✅ PASS' if psnr >= 50 else '⚠️ BELOW TARGET'}")
        print(f"  Capacity used: {payload_size}/{capacity_bytes} bytes ({100*payload_size/capacity_bytes:.1f}%)")
        print(f"  Extraction: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print(f"  Embed time: {embed_time*1000:.2f} ms")
        print(f"  Extract time: {extract_time*1000:.2f} ms")
        
        return {
            'scenario': scenario_name,
            'payload_size': payload_size,
            'q_factor': q_factor,
            'coeff_percentage': coeff_percentage,
            'threshold': threshold,
            'bands': len(bands),
            'psnr': psnr,
            'capacity_bytes': capacity_bytes,
            'success': success,
            'embed_time': embed_time,
            'extract_time': extract_time
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    image_path = 'test_lena.png'
    
    if not os.path.exists(image_path):
        print(f"❌ Test image not found: {image_path}")
        return
    
    print("="*70)
    print("PSNR OPTIMIZATION - COMPREHENSIVE TESTING")
    print("="*70)
    print(f"Test image: {image_path}")
    print(f"Goal: PSNR ≥50 dB with various payload sizes")
    
    # Define band configurations
    bands_7 = ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']
    bands_6 = ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2']
    bands_3 = ['LH1', 'HL1', 'HH1']
    
    results = []
    
    # TEST SET 1: Small payloads (100-1000 bytes) - Should achieve PSNR >50
    print("\n" + "="*70)
    print("TEST SET 1: SMALL PAYLOADS (100-1000 bytes)")
    print("="*70)
    
    result = test_scenario(image_path, 100, 4.0, 38, 8, bands_7, "Small payload - Current settings")
    if result: results.append(result)
    
    result = test_scenario(image_path, 500, 4.0, 38, 8, bands_7, "Small-medium payload - Current settings")
    if result: results.append(result)
    
    result = test_scenario(image_path, 1000, 4.0, 38, 8, bands_7, "Medium payload - Current settings")
    if result: results.append(result)
    
    # TEST SET 2: Medium payloads (2000-4000 bytes) - Optimize for PSNR
    print("\n" + "="*70)
    print("TEST SET 2: MEDIUM PAYLOADS (2000-4000 bytes)")
    print("="*70)
    
    result = test_scenario(image_path, 2000, 4.0, 38, 8, bands_7, "2KB - Current Q=4.0")
    if result: results.append(result)
    
    result = test_scenario(image_path, 2000, 5.0, 38, 8, bands_7, "2KB - Higher Q=5.0")
    if result: results.append(result)
    
    result = test_scenario(image_path, 2000, 6.0, 38, 8, bands_7, "2KB - Highest Q=6.0")
    if result: results.append(result)
    
    result = test_scenario(image_path, 4000, 5.0, 38, 8, bands_7, "4KB - Q=5.0")
    if result: results.append(result)
    
    result = test_scenario(image_path, 4000, 6.0, 38, 8, bands_7, "4KB - Q=6.0")
    if result: results.append(result)
    
    # TEST SET 3: Large payloads (5000-8000 bytes) - Maximum capacity
    print("\n" + "="*70)
    print("TEST SET 3: LARGE PAYLOADS (5000-8000 bytes)")
    print("="*70)
    
    result = test_scenario(image_path, 5000, 4.0, 38, 8, bands_7, "5KB - Q=4.0")
    if result: results.append(result)
    
    result = test_scenario(image_path, 5000, 5.0, 38, 8, bands_7, "5KB - Q=5.0")
    if result: results.append(result)
    
    result = test_scenario(image_path, 5000, 6.0, 38, 8, bands_7, "5KB - Q=6.0")
    if result: results.append(result)
    
    result = test_scenario(image_path, 5000, 7.0, 38, 8, bands_7, "5KB - Q=7.0")
    if result: results.append(result)
    
    result = test_scenario(image_path, 8000, 6.0, 38, 8, bands_7, "8KB - Q=6.0")
    if result: results.append(result)
    
    result = test_scenario(image_path, 8000, 7.0, 38, 8, bands_7, "8KB - Q=7.0")
    if result: results.append(result)
    
    # TEST SET 4: Reduced bands for better PSNR
    print("\n" + "="*70)
    print("TEST SET 4: FEWER BANDS (Better PSNR, Lower Capacity)")
    print("="*70)
    
    result = test_scenario(image_path, 3000, 5.0, 38, 8, bands_6, "3KB - 6 bands, Q=5.0")
    if result: results.append(result)
    
    result = test_scenario(image_path, 3000, 6.0, 38, 8, bands_6, "3KB - 6 bands, Q=6.0")
    if result: results.append(result)
    
    result = test_scenario(image_path, 2000, 5.0, 38, 10, bands_6, "2KB - 6 bands, threshold=10")
    if result: results.append(result)
    
    result = test_scenario(image_path, 1000, 6.0, 30, 10, bands_3, "1KB - 3 bands only")
    if result: results.append(result)
    
    # TEST SET 5: Lower coefficient usage for better PSNR
    print("\n" + "="*70)
    print("TEST SET 5: LOWER COEFFICIENT USAGE (Better PSNR)")
    print("="*70)
    
    result = test_scenario(image_path, 3000, 5.0, 30, 8, bands_7, "3KB - 30% coeffs")
    if result: results.append(result)
    
    result = test_scenario(image_path, 5000, 6.0, 30, 8, bands_7, "5KB - 30% coeffs")
    if result: results.append(result)
    
    result = test_scenario(image_path, 3000, 6.0, 25, 10, bands_7, "3KB - 25% coeffs, thresh=10")
    if result: results.append(result)
    
    # SUMMARY
    print("\n" + "="*70)
    print("FINAL SUMMARY - ALL SCENARIOS")
    print("="*70)
    
    # Filter successful results
    successful = [r for r in results if r and r['success']]
    
    if not successful:
        print("❌ No successful scenarios")
        return
    
    # Sort by PSNR descending
    successful.sort(key=lambda x: x['psnr'], reverse=True)
    
    print(f"\n{'Scenario':<40} {'Payload':>8} {'PSNR':>8} {'Q':>5} {'Bands':>6}")
    print("-"*70)
    
    for r in successful:
        status = "✅" if r['psnr'] >= 50 else "⚠️"
        print(f"{status} {r['scenario']:<38} {r['payload_size']:>6}B {r['psnr']:>7.2f} {r['q_factor']:>5.1f} {r['bands']:>6}")
    
    # Find best configurations
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    
    # Best for small payloads (<2KB)
    small_payload = [r for r in successful if r['payload_size'] < 2000 and r['psnr'] >= 50]
    if small_payload:
        best_small = max(small_payload, key=lambda x: x['payload_size'])
        print(f"\n✅ SMALL PAYLOADS (<2KB):")
        print(f"   Configuration: Q={best_small['q_factor']}, {best_small['coeff_percentage']}% coeffs, {best_small['bands']} bands")
        print(f"   Max payload: {best_small['payload_size']} bytes")
        print(f"   PSNR: {best_small['psnr']:.2f} dB")
    
    # Best for medium payloads (2-5KB)
    medium_payload = [r for r in successful if 2000 <= r['payload_size'] < 5000 and r['psnr'] >= 50]
    if medium_payload:
        best_medium = max(medium_payload, key=lambda x: x['payload_size'])
        print(f"\n✅ MEDIUM PAYLOADS (2-5KB):")
        print(f"   Configuration: Q={best_medium['q_factor']}, {best_medium['coeff_percentage']}% coeffs, {best_medium['bands']} bands")
        print(f"   Max payload: {best_medium['payload_size']} bytes")
        print(f"   PSNR: {best_medium['psnr']:.2f} dB")
    
    # Best for large payloads (>=5KB)
    large_payload = [r for r in successful if r['payload_size'] >= 5000 and r['psnr'] >= 50]
    if large_payload:
        best_large = max(large_payload, key=lambda x: x['payload_size'])
        print(f"\n✅ LARGE PAYLOADS (≥5KB):")
        print(f"   Configuration: Q={best_large['q_factor']}, {best_large['coeff_percentage']}% coeffs, {best_large['bands']} bands")
        print(f"   Max payload: {best_large['payload_size']} bytes")
        print(f"   PSNR: {best_large['psnr']:.2f} dB")
    
    # Overall best PSNR
    best_psnr = max(successful, key=lambda x: x['psnr'])
    print(f"\n🏆 HIGHEST PSNR ACHIEVED:")
    print(f"   Scenario: {best_psnr['scenario']}")
    print(f"   PSNR: {best_psnr['psnr']:.2f} dB")
    print(f"   Payload: {best_psnr['payload_size']} bytes")
    print(f"   Configuration: Q={best_psnr['q_factor']}, {best_psnr['bands']} bands")
    
    # Count how many meet target
    meets_target = len([r for r in successful if r['psnr'] >= 50])
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"   Scenarios tested: {len(results)}")
    print(f"   Successful extractions: {len(successful)}")
    print(f"   Meeting PSNR ≥50 dB: {meets_target}/{len(successful)}")
    print(f"   Success rate: {100*meets_target/len(successful):.1f}%")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
