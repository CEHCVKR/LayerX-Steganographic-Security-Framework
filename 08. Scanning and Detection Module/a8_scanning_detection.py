"""
Module 8: Scanning and Detection
Author: Member A
Description: Steganalysis detection and security scanning for steganographic content
Dependencies: numpy, opencv-python, scipy, scikit-learn

Features:
- Statistical analysis (Chi-square, RS analysis)
- Histogram analysis
- DCT coefficient distribution analysis
- LSB analysis
- Anomaly detection
- Security scoring
"""

import numpy as np
import cv2
from scipy import stats
from scipy.fft import dct, idct
import sys
import os
from typing import Dict, Tuple, List

# Import previous modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "03. Image Processing Module"))
from a3_image_processing import *


def chi_square_test(image: np.ndarray, block_size: int = 256) -> float:
    """
    Perform Chi-square test for LSB steganography detection
    
    Args:
        image: Input image
        block_size: Block size for analysis
        
    Returns:
        Chi-square statistic (lower = more likely stego)
    """
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    h, w = image.shape
    chi_values = []
    
    for i in range(0, h - block_size, block_size // 2):
        for j in range(0, w - block_size, block_size // 2):
            block = image[i:i+block_size, j:j+block_size]
            
            # Count pixel pairs
            pairs = np.zeros(128, dtype=int)
            for k in range(128):
                pairs[k] = np.sum((block == 2*k) | (block == 2*k + 1))
            
            # Calculate chi-square
            expected = pairs.sum() / 128
            if expected > 0:
                chi = np.sum((pairs - expected) ** 2 / expected)
                chi_values.append(chi)
    
    return np.mean(chi_values) if chi_values else 0.0


def rs_analysis(image: np.ndarray) -> Dict[str, float]:
    """
    Regular-Singular (RS) analysis for steganography detection
    
    Args:
        image: Input image
        
    Returns:
        Dictionary with R/S ratios and estimated message length
    """
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def mask_group(pixels, mask):
        """Apply mask and calculate discrimination function"""
        masked = pixels.copy()
        for i, m in enumerate(mask):
            if m == 1:
                if i < len(masked) - 1:
                    masked[i] = min(255, max(0, 2*masked[i] - masked[i+1]))
        return np.abs(np.diff(masked.astype(int))).sum()
    
    # Sample blocks
    block_size = 8
    h, w = image.shape
    
    R_plus, R_minus, S_plus, S_minus = 0, 0, 0, 0
    total_blocks = 0
    
    mask = [1, 0, 1, 0, 1, 0, 1, 0]
    
    for i in range(0, h - block_size, block_size):
        for j in range(0, w - block_size, block_size):
            block = image[i:i+block_size, j:j+block_size].flatten()
            
            # Original discrimination
            f_original = np.abs(np.diff(block.astype(int))).sum()
            
            # Apply positive mask
            f_plus = mask_group(block, mask)
            
            # Apply negative mask
            f_minus = mask_group(block, [1-m for m in mask])
            
            # Classify
            if f_plus > f_original:
                R_plus += 1
            elif f_plus < f_original:
                S_plus += 1
                
            if f_minus > f_original:
                R_minus += 1
            elif f_minus < f_original:
                S_minus += 1
            
            total_blocks += 1
    
    # Calculate ratios
    if total_blocks > 0:
        r_plus_ratio = R_plus / total_blocks
        s_plus_ratio = S_plus / total_blocks
        r_minus_ratio = R_minus / total_blocks
        s_minus_ratio = S_minus / total_blocks
        
        # Estimate message length (simplified)
        estimated_length = 0.0
        if r_plus_ratio > s_plus_ratio:
            estimated_length = 2 * (r_plus_ratio - s_plus_ratio) / (r_plus_ratio + s_plus_ratio)
    else:
        r_plus_ratio = s_plus_ratio = r_minus_ratio = s_minus_ratio = 0.0
        estimated_length = 0.0
    
    return {
        'R_plus': r_plus_ratio,
        'S_plus': s_plus_ratio,
        'R_minus': r_minus_ratio,
        'S_minus': s_minus_ratio,
        'estimated_length': estimated_length,
        'detection_score': abs(r_plus_ratio - s_plus_ratio)
    }


def histogram_analysis(image: np.ndarray) -> Dict[str, float]:
    """
    Analyze histogram for steganography indicators
    
    Args:
        image: Input image
        
    Returns:
        Dictionary with histogram metrics
    """
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    hist = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten()
    
    # Calculate metrics
    entropy = -np.sum((hist / hist.sum()) * np.log2((hist / hist.sum()) + 1e-10))
    
    # Pair analysis (LSB embedding indicator)
    pair_diffs = []
    for i in range(0, 256, 2):
        if i+1 < 256:
            pair_diffs.append(abs(hist[i] - hist[i+1]))
    
    avg_pair_diff = np.mean(pair_diffs)
    max_pair_diff = np.max(pair_diffs)
    
    # Smoothness
    smoothness = np.mean(np.abs(np.diff(hist)))
    
    return {
        'entropy': entropy,
        'avg_pair_diff': avg_pair_diff,
        'max_pair_diff': max_pair_diff,
        'smoothness': smoothness,
        'uniformity': np.std(hist)
    }


def dct_analysis(image: np.ndarray) -> Dict[str, float]:
    """
    Analyze DCT coefficients for anomalies
    
    Args:
        image: Input image
        
    Returns:
        Dictionary with DCT metrics
    """
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply DCT on 8x8 blocks
    h, w = image.shape
    block_size = 8
    
    coeff_stats = []
    
    for i in range(0, h - block_size, block_size):
        for j in range(0, w - block_size, block_size):
            block = image[i:i+block_size, j:j+block_size].astype(float)
            dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
            
            # Analyze middle-frequency coefficients (typical embedding zone)
            mid_freq = dct_block[2:6, 2:6]
            coeff_stats.append({
                'mean': np.mean(mid_freq),
                'std': np.std(mid_freq),
                'max': np.max(np.abs(mid_freq))
            })
    
    # Aggregate statistics
    means = [s['mean'] for s in coeff_stats]
    stds = [s['std'] for s in coeff_stats]
    
    return {
        'avg_coeff_mean': np.mean(means),
        'avg_coeff_std': np.mean(stds),
        'coeff_variance': np.var(means),
        'block_inconsistency': np.std(stds)
    }


def lsb_analysis(image: np.ndarray) -> Dict[str, float]:
    """
    Analyze LSB plane for randomness
    
    Args:
        image: Input image
        
    Returns:
        Dictionary with LSB metrics
    """
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Extract LSB plane
    lsb_plane = image & 1
    
    # Calculate randomness
    total_pixels = lsb_plane.size
    ones = np.sum(lsb_plane)
    zeros = total_pixels - ones
    
    # Expected for random: ~50% each
    randomness_score = 1 - abs(0.5 - (ones / total_pixels)) * 2
    
    # Adjacent bit flips (indicator of embedding)
    flips_h = np.sum(np.diff(lsb_plane, axis=1) != 0)
    flips_v = np.sum(np.diff(lsb_plane, axis=0) != 0)
    
    expected_flips = total_pixels * 0.5
    flip_ratio = (flips_h + flips_v) / expected_flips
    
    # Autocorrelation
    autocorr = np.correlate(lsb_plane.flatten(), lsb_plane.flatten(), mode='same')[lsb_plane.size // 2]
    
    return {
        'ones_ratio': ones / total_pixels,
        'randomness_score': randomness_score,
        'flip_ratio': flip_ratio,
        'autocorrelation': float(autocorr) / total_pixels
    }


def detect_steganography(image_path: str) -> Dict[str, any]:
    """
    Comprehensive steganography detection
    
    Args:
        image_path: Path to image file
        
    Returns:
        Dictionary with detection results and scores
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")
    
    print(f"Analyzing: {image_path}")
    print(f"Image size: {image.shape}")
    
    # Run all tests
    chi_square = chi_square_test(image)
    rs_result = rs_analysis(image)
    hist_result = histogram_analysis(image)
    dct_result = dct_analysis(image)
    lsb_result = lsb_analysis(image)
    
    # Calculate overall detection score (0-100, higher = more suspicious)
    detection_score = 0.0
    
    # Chi-square contribution (lower is more suspicious)
    if chi_square < 100:
        detection_score += 30
    elif chi_square < 200:
        detection_score += 15
    
    # RS analysis contribution
    detection_score += rs_result['detection_score'] * 20
    
    # Histogram contribution
    if hist_result['avg_pair_diff'] < 50:
        detection_score += 15
    
    # LSB randomness contribution
    if 0.45 < lsb_result['ones_ratio'] < 0.55:
        detection_score += 20  # High randomness suspicious
    
    # DCT contribution
    if dct_result['block_inconsistency'] > 5:
        detection_score += 15
    
    detection_score = min(100, detection_score)
    
    # Classification
    if detection_score > 70:
        classification = "HIGH - Likely contains hidden data"
    elif detection_score > 40:
        classification = "MEDIUM - Possibly contains hidden data"
    else:
        classification = "LOW - Unlikely to contain hidden data"
    
    return {
        'detection_score': detection_score,
        'classification': classification,
        'chi_square': chi_square,
        'rs_analysis': rs_result,
        'histogram': hist_result,
        'dct_analysis': dct_result,
        'lsb_analysis': lsb_result
    }


def scan_directory(directory: str) -> List[Dict]:
    """
    Scan directory for images and analyze each
    
    Args:
        directory: Path to directory
        
    Returns:
        List of detection results
    """
    results = []
    
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            filepath = os.path.join(directory, filename)
            try:
                result = detect_steganography(filepath)
                result['filename'] = filename
                results.append(result)
            except Exception as e:
                print(f"Error analyzing {filename}: {str(e)}")
    
    return results


def compare_images(original_path: str, stego_path: str) -> Dict[str, float]:
    """
    Compare original and stego images for differences
    
    Args:
        original_path: Path to original image
        stego_path: Path to stego image
        
    Returns:
        Dictionary with comparison metrics
    """
    orig = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
    stego = cv2.imread(stego_path, cv2.IMREAD_GRAYSCALE)
    
    if orig is None or stego is None:
        raise ValueError("Cannot read images")
    
    if orig.shape != stego.shape:
        raise ValueError("Images must have same dimensions")
    
    # Calculate differences
    diff = np.abs(orig.astype(int) - stego.astype(int))
    
    # Metrics
    max_diff = np.max(diff)
    avg_diff = np.mean(diff)
    changed_pixels = np.sum(diff > 0)
    total_pixels = orig.size
    
    # PSNR
    mse = np.mean((orig.astype(float) - stego.astype(float)) ** 2)
    psnr = 10 * np.log10(255**2 / mse) if mse > 0 else float('inf')
    
    # Structural similarity
    mean_orig = np.mean(orig)
    mean_stego = np.mean(stego)
    var_orig = np.var(orig)
    var_stego = np.var(stego)
    covar = np.mean((orig - mean_orig) * (stego - mean_stego))
    
    return {
        'max_diff': int(max_diff),
        'avg_diff': float(avg_diff),
        'changed_pixels': int(changed_pixels),
        'change_ratio': float(changed_pixels / total_pixels),
        'psnr': float(psnr),
        'correlation': float(covar / (np.sqrt(var_orig * var_stego) + 1e-10))
    }


def test_scanning_module():
    """Test the scanning and detection module"""
    print("="*70)
    print("MODULE 8: SCANNING AND DETECTION TEST")
    print("="*70)
    
    # Test with test image
    test_image = 'test_lena.png'
    
    if os.path.exists(test_image):
        print(f"\n1. Testing steganography detection on {test_image}...")
        result = detect_steganography(test_image)
        
        print(f"\n   Detection Score: {result['detection_score']:.2f}/100")
        print(f"   Classification: {result['classification']}")
        print(f"   Chi-square: {result['chi_square']:.2f}")
        print(f"   RS Detection: {result['rs_analysis']['detection_score']:.4f}")
        print(f"   LSB Randomness: {result['lsb_analysis']['randomness_score']:.4f}")
        print(f"   Histogram Entropy: {result['histogram']['entropy']:.4f}")
        
        print("\n   ✓ Detection analysis complete")
    else:
        print(f"\n⚠️  Test image not found: {test_image}")
    
    # Test comparison if stego image exists
    stego_image = 'final_improved.png'
    if os.path.exists(test_image) and os.path.exists(stego_image):
        print(f"\n2. Testing image comparison...")
        comp = compare_images(test_image, stego_image)
        
        print(f"\n   PSNR: {comp['psnr']:.2f} dB")
        print(f"   Changed pixels: {comp['changed_pixels']} ({comp['change_ratio']*100:.2f}%)")
        print(f"   Average difference: {comp['avg_diff']:.2f}")
        print(f"   Max difference: {comp['max_diff']}")
        
        print("\n   ✓ Image comparison complete")
    
    print("\n" + "="*70)
    print("✅ Scanning and detection module test completed!")
    print("="*70)


if __name__ == "__main__":
    test_scanning_module()
