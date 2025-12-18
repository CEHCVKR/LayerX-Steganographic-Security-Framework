"""
Test Adaptive Q Factor Implementation
Verify PSNR improvement with different payload sizes
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '05. Embedding and Extraction Module'))

from a5_embedding_extraction import embed, extract, psnr_images
import time

def test_payload(size, description):
    """Test a specific payload size"""
    print(f"\n{'='*70}")
    print(f"TEST: {description} ({size} bytes)")
    print(f"{'='*70}")
    
    # Create test message
    message = "X" * size
    payload = message.encode('utf-8')
    
    print(f"Payload size: {size} bytes")
    
    # Embed
    start = time.time()
    success = embed(payload, 'test_lena.png', 'adaptive_test.png', optimization='fixed')
    embed_time = time.time() - start
    
    if not success:
        print("❌ Embedding failed")
        return None
    
    # Calculate PSNR
    psnr = psnr_images('test_lena.png', 'adaptive_test.png')
    
    # Extract
    start = time.time()
    extracted = extract('adaptive_test.png', optimization='fixed')
    extract_time = time.time() - start
    
    # Verify
    success = (extracted == payload)
    
    print(f"\n📊 RESULTS:")
    print(f"  PSNR: {psnr:.2f} dB {'✅ PASS' if psnr >= 50 else '⚠️ BELOW 50'}")
    print(f"  Extraction: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"  Embed time: {embed_time*1000:.1f} ms")
    print(f"  Extract time: {extract_time*1000:.1f} ms")
    
    # Clean up
    if os.path.exists('adaptive_test.png'):
        os.remove('adaptive_test.png')
    
    return {'size': size, 'psnr': psnr, 'success': success}

def main():
    print("="*70)
    print("ADAPTIVE Q FACTOR - PERFORMANCE VERIFICATION")
    print("="*70)
    print("Testing automatic Q selection based on payload size\n")
    
    if not os.path.exists('test_lena.png'):
        print("❌ test_lena.png not found")
        return
    
    results = []
    
    # Test different payload sizes
    tests = [
        (500, "Small payload (Q=4.0)"),
        (1000, "1KB payload (Q=4.0)"),
        (2000, "2KB payload (Q=4.0)"),
        (3000, "3KB payload (Q=6.0)"),
        (4000, "4KB payload (Q=6.0)"),
        (5000, "5KB payload (Q=6.0)"),
        (5500, "5.5KB payload (Q=7.0) - Hybrid encryption size"),
        (6000, "6KB payload (Q=7.0) - Maximum for >50dB"),
    ]
    
    for size, desc in tests:
        result = test_payload(size, desc)
        if result:
            results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY - ADAPTIVE Q PERFORMANCE")
    print("="*70)
    
    if not results:
        print("❌ No successful tests")
        return
    
    print(f"\n{'Payload Size':>15} {'PSNR':>10} {'Status':>15}")
    print("-"*70)
    
    for r in results:
        status = "✅ PASS" if r['psnr'] >= 50 else "⚠️ BELOW 50"
        print(f"{r['size']:>13}B {r['psnr']:>9.2f}dB {status}")
    
    # Statistics
    meets_target = [r for r in results if r['psnr'] >= 50]
    
    print(f"\n📊 Statistics:")
    print(f"  Total tests: {len(results)}")
    print(f"  Successful: {len([r for r in results if r['success']])}")
    print(f"  PSNR >=50dB: {len(meets_target)}/{len(results)} ({100*len(meets_target)/len(results):.1f}%)")
    
    if meets_target:
        avg_psnr = sum(r['psnr'] for r in meets_target) / len(meets_target)
        min_psnr = min(r['psnr'] for r in meets_target)
        max_psnr = max(r['psnr'] for r in meets_target)
        
        print(f"\n✅ PSNR Performance:")
        print(f"  Average: {avg_psnr:.2f} dB")
        print(f"  Range: {min_psnr:.2f} - {max_psnr:.2f} dB")
        print(f"  All meet target (>50dB): {'✅ YES' if len(meets_target) == len(results) else '⚠️ PARTIAL'}")
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    
    if len(meets_target) == len(results):
        print("✅ All payload sizes achieve PSNR >50dB with adaptive Q")
        print("✅ System ready for production use")
    elif meets_target:
        print(f"✅ {len(meets_target)}/{len(results)} payloads achieve PSNR >50dB")
        print("⚠️  Consider increasing Q for larger payloads")
    else:
        print("❌ Adaptive Q needs further tuning")
    
    print("="*70)

if __name__ == "__main__":
    main()
