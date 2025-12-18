"""
PSNR Optimization Tests - Various Payload Sizes
Tests different Q factors and payloads to achieve PSNR >50 dB
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '03. Image Processing Module'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '05. Embedding and Extraction Module'))

from a5_embedding_extraction import embed, extract, psnr_images
import cv2
import numpy as np
import time

def test_with_q_factor(payload_size, q_factor, test_name):
    """Test embedding with specific Q factor"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    print(f"Payload: {payload_size} bytes, Q factor: {q_factor}")
    
    try:
        # Modify Q factor temporarily
        import a5_embedding_extraction as embed_module
        original_q = embed_module.Q
        embed_module.Q = q_factor
        
        # Create test message
        message = "X" * payload_size
        payload = message.encode('utf-8')
        
        # Embed
        start = time.time()
        success = embed(payload, 'test_lena.png', 'temp_test.png', optimization='aco')
        embed_time = time.time() - start
        
        if not success:
            print("❌ Embedding failed")
            embed_module.Q = original_q
            return None
        
        # Calculate PSNR
        psnr = psnr_images('test_lena.png', 'temp_test.png')
        
        # Extract
        start = time.time()
        extracted = extract('temp_test.png', optimization='aco')
        extract_time = time.time() - start
        
        # Verify
        success = (extracted == payload)
        
        # Clean up
        if os.path.exists('temp_test.png'):
            os.remove('temp_test.png')
        
        # Restore Q
        embed_module.Q = original_q
        
        print(f"\n📊 RESULTS:")
        print(f"  PSNR: {psnr:.2f} dB {'✅ PASS' if psnr >= 50 else '⚠️ BELOW 50'}")
        print(f"  Extraction: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print(f"  Embed time: {embed_time*1000:.1f} ms")
        print(f"  Extract time: {extract_time*1000:.1f} ms")
        
        return {
            'test_name': test_name,
            'payload_size': payload_size,
            'q_factor': q_factor,
            'psnr': psnr,
            'success': success,
            'embed_time': embed_time,
            'extract_time': extract_time
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        # Restore Q
        try:
            embed_module.Q = original_q
        except:
            pass
        return None

def main():
    print("="*70)
    print("PSNR OPTIMIZATION - PAYLOAD SIZE & Q FACTOR TESTS")
    print("="*70)
    print("Goal: Achieve PSNR ≥50 dB with various payload sizes")
    print("Method: Test different Q factors (4.0 to 8.0)")
    
    if not os.path.exists('test_lena.png'):
        print("❌ test_lena.png not found")
        return
    
    results = []
    
    # TEST SET 1: Small payloads (500-1500 bytes)
    print("\n" + "="*70)
    print("TEST SET 1: SMALL PAYLOADS (500-1500 bytes)")
    print("="*70)
    
    result = test_with_q_factor(500, 4.0, "500B - Q=4.0 (Current)")
    if result: results.append(result)
    
    result = test_with_q_factor(1000, 4.0, "1KB - Q=4.0 (Current)")
    if result: results.append(result)
    
    result = test_with_q_factor(1000, 5.0, "1KB - Q=5.0")
    if result: results.append(result)
    
    result = test_with_q_factor(1500, 5.0, "1.5KB - Q=5.0")
    if result: results.append(result)
    
    # TEST SET 2: Medium payloads (2000-4000 bytes)
    print("\n" + "="*70)
    print("TEST SET 2: MEDIUM PAYLOADS (2-4 KB)")
    print("="*70)
    
    result = test_with_q_factor(2000, 4.0, "2KB - Q=4.0 (Current)")
    if result: results.append(result)
    
    result = test_with_q_factor(2000, 5.0, "2KB - Q=5.0")
    if result: results.append(result)
    
    result = test_with_q_factor(2000, 6.0, "2KB - Q=6.0")
    if result: results.append(result)
    
    result = test_with_q_factor(3000, 5.0, "3KB - Q=5.0")
    if result: results.append(result)
    
    result = test_with_q_factor(3000, 6.0, "3KB - Q=6.0")
    if result: results.append(result)
    
    result = test_with_q_factor(4000, 6.0, "4KB - Q=6.0")
    if result: results.append(result)
    
    # TEST SET 3: Large payloads (5000-8000 bytes)
    print("\n" + "="*70)
    print("TEST SET 3: LARGE PAYLOADS (5-8 KB)")
    print("="*70)
    
    result = test_with_q_factor(5000, 5.0, "5KB - Q=5.0")
    if result: results.append(result)
    
    result = test_with_q_factor(5000, 6.0, "5KB - Q=6.0")
    if result: results.append(result)
    
    result = test_with_q_factor(5000, 7.0, "5KB - Q=7.0")
    if result: results.append(result)
    
    result = test_with_q_factor(6000, 6.0, "6KB - Q=6.0")
    if result: results.append(result)
    
    result = test_with_q_factor(6000, 7.0, "6KB - Q=7.0")
    if result: results.append(result)
    
    result = test_with_q_factor(8000, 7.0, "8KB - Q=7.0")
    if result: results.append(result)
    
    result = test_with_q_factor(8000, 8.0, "8KB - Q=8.0")
    if result: results.append(result)
    
    # TEST SET 4: Very high Q for maximum PSNR
    print("\n" + "="*70)
    print("TEST SET 4: ULTRA HIGH Q (Maximum PSNR)")
    print("="*70)
    
    result = test_with_q_factor(1000, 8.0, "1KB - Q=8.0 (Ultra)")
    if result: results.append(result)
    
    result = test_with_q_factor(2000, 8.0, "2KB - Q=8.0 (Ultra)")
    if result: results.append(result)
    
    result = test_with_q_factor(3000, 8.0, "3KB - Q=8.0 (Ultra)")
    if result: results.append(result)
    
    result = test_with_q_factor(4000, 8.0, "4KB - Q=8.0 (Ultra)")
    if result: results.append(result)
    
    # SUMMARY
    print("\n" + "="*70)
    print("COMPREHENSIVE SUMMARY")
    print("="*70)
    
    successful = [r for r in results if r and r['success']]
    
    if not successful:
        print("❌ No successful tests")
        return
    
    # Sort by PSNR
    successful.sort(key=lambda x: x['psnr'], reverse=True)
    
    print(f"\n{'Test Name':<35} {'Payload':>8} {'Q':>5} {'PSNR':>8} {'Status':>7}")
    print("-"*70)
    
    for r in successful:
        status = "✅ PASS" if r['psnr'] >= 50 else "⚠️ BELOW"
        print(f"{r['test_name']:<35} {r['payload_size']:>6}B {r['q_factor']:>5.1f} {r['psnr']:>7.2f} {status}")
    
    # Statistics
    meets_target = [r for r in successful if r['psnr'] >= 50]
    below_target = [r for r in successful if r['psnr'] < 50]
    
    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)
    
    print(f"\n📊 Overall Statistics:")
    print(f"  Total tests: {len(results)}")
    print(f"  Successful extractions: {len(successful)}")
    print(f"  Meeting PSNR ≥50 dB: {len(meets_target)}")
    print(f"  Below target: {len(below_target)}")
    print(f"  Success rate: {100*len(meets_target)/len(successful):.1f}%")
    
    if meets_target:
        print(f"\n🏆 Best Results (PSNR ≥50 dB):")
        
        # Highest PSNR
        best_psnr = max(meets_target, key=lambda x: x['psnr'])
        print(f"\n  Highest PSNR:")
        print(f"    {best_psnr['test_name']}")
        print(f"    PSNR: {best_psnr['psnr']:.2f} dB, Q={best_psnr['q_factor']}")
        
        # Largest payload with PSNR ≥50
        best_capacity = max(meets_target, key=lambda x: x['payload_size'])
        print(f"\n  Largest Payload (while maintaining PSNR ≥50):")
        print(f"    {best_capacity['test_name']}")
        print(f"    Payload: {best_capacity['payload_size']} bytes")
        print(f"    PSNR: {best_capacity['psnr']:.2f} dB, Q={best_capacity['q_factor']}")
        
        # Recommended Q factors for different sizes
        print(f"\n💡 Recommended Configurations:")
        
        small = [r for r in meets_target if r['payload_size'] <= 2000]
        if small:
            best_small = max(small, key=lambda x: (x['payload_size'], x['psnr']))
            print(f"\n  For payloads ≤2KB: Q={best_small['q_factor']}")
            print(f"    Can achieve {best_small['payload_size']}B at {best_small['psnr']:.2f} dB")
        
        medium = [r for r in meets_target if 2000 < r['payload_size'] <= 5000]
        if medium:
            best_medium = max(medium, key=lambda x: (x['payload_size'], x['psnr']))
            print(f"\n  For payloads 2-5KB: Q={best_medium['q_factor']}")
            print(f"    Can achieve {best_medium['payload_size']}B at {best_medium['psnr']:.2f} dB")
        
        large = [r for r in meets_target if r['payload_size'] > 5000]
        if large:
            best_large = max(large, key=lambda x: (x['payload_size'], x['psnr']))
            print(f"\n  For payloads >5KB: Q={best_large['q_factor']}")
            print(f"    Can achieve {best_large['payload_size']}B at {best_large['psnr']:.2f} dB")
    
    if below_target:
        print(f"\n⚠️  Below Target (PSNR <50 dB):")
        for r in below_target[:5]:  # Show top 5
            print(f"    {r['test_name']}: {r['psnr']:.2f} dB (need Q≥{r['q_factor']+1})")
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    
    if meets_target:
        print(f"✅ SUCCESS: Can achieve PSNR ≥50 dB with payloads up to {best_capacity['payload_size']} bytes")
        print(f"   Optimal Q factor range: {min([r['q_factor'] for r in meets_target]):.1f} - {max([r['q_factor'] for r in meets_target]):.1f}")
    else:
        print("⚠️  Need to increase Q factor or reduce payload size to meet PSNR target")
    
    print("="*70)

if __name__ == "__main__":
    main()
