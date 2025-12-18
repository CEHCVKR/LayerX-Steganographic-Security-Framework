"""
Validation script: Check if implementation meets abstract requirements
"""
import cv2
import numpy as np
import os

print("="*80)
print("ABSTRACT REQUIREMENTS vs IMPLEMENTATION VALIDATION")
print("="*80)

# Test images
orig = cv2.imread('test_lena.png', 0)
steg = cv2.imread('metrics_test.png', 0)

if orig is None or steg is None:
    print("ERROR: Test images not found")
    exit(1)

# Calculate PSNR
mse = np.mean((orig.astype(float) - steg.astype(float))**2)
psnr = 10 * np.log10(255**2 / mse) if mse > 0 else float('inf')

# Calculate NPCR (Number of Pixel Change Rate)
diff = np.abs(orig.astype(int) - steg.astype(int))
npcr = (diff > 0).sum() / diff.size * 100

# Calculate UACI (Unified Average Changing Intensity)
uaci = diff.sum() / (255 * diff.size) * 100

# Calculate payload capacity
img_size = orig.size
payload_bytes = 5365  # From last test
capacity_percent = (payload_bytes * 8) / img_size * 100

print("\n1. IMPERCEPTIBILITY (PSNR)")
print(f"   Target: > 50 dB")
print(f"   Actual: {psnr:.2f} dB")
print(f"   Status: {'PASS' if psnr > 50 else 'FAIL'}")

print("\n2. PAYLOAD CAPACITY")
print(f"   Target: 30-50%")
print(f"   Actual: {capacity_percent:.2f}%")
print(f"   Payload: {payload_bytes} bytes in {img_size} pixels")
print(f"   Status: {'FAIL - Below target' if capacity_percent < 30 else 'PASS'}")

print("\n3. ROBUSTNESS (NPCR/UACI)")
print(f"   NPCR: {npcr:.2f}% (Higher = more robust)")
print(f"   UACI: {uaci:.4f}% (Balanced change)")
print(f"   Status: MEASURED")

print("\n4. IMPLEMENTED FEATURES")
features = {
    "AES-256 Encryption": "YES",
    "ECC (Elliptic Curve)": "NO - Missing",
    "Huffman Compression": "YES",
    "DWT Transform": "YES",
    "DCT Transform": "YES",
    "ACO Optimization": "YES",
    "Chaos Maps": "YES",
    "Network Communication": "NO - Only file-based",
    "Secure Chat/File Transfer": "NO - Only send/receive"
}

for feature, status in features.items():
    marker = "✓" if "YES" in status else "✗"
    print(f"   {marker} {feature}: {status}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"PSNR Target: {'ACHIEVED' if psnr > 50 else 'NOT ACHIEVED'}")
print(f"Payload Target: {'NOT ACHIEVED (only {:.1f}% vs 30-50%)'.format(capacity_percent)}")
print(f"Missing: ECC encryption, Network layer, Secure chat UI")
print("="*80)
