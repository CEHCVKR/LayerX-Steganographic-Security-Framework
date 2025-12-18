"""
Module 3: Image Processing
Author: Member A  
Description: DWT (2 levels) + DCT on LL band for frequency domain steganography
Dependencies: numpy, opencv-python, pywavelets, scikit-image

Functions:
- read_image(path: str) → numpy.ndarray (grayscale uint8)
- dwt_decompose(image: ndarray, levels: int) → dict (DWT coefficients)
- dct_on_ll(ll_band: ndarray) → ndarray (DCT of LL band)
- idct_on_ll(ll_dct: ndarray) → ndarray (Inverse DCT)
- dwt_reconstruct(bands: dict) → ndarray (Reconstructed image)
- psnr(original: ndarray, reconstructed: ndarray) → float (Peak SNR in dB)
"""

import numpy as np
import cv2
import pywt
from scipy.fft import dct, idct
from skimage.metrics import peak_signal_noise_ratio
import os
from typing import Dict, Tuple


def read_image(path: str) -> np.ndarray:
    """
    Read image and convert to grayscale.
    
    Args:
        path (str): Path to image file
        
    Returns:
        numpy.ndarray: Grayscale image as uint8 array
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found: {path}")
    
    # Read image
    image = cv2.imread(path)
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    return image.astype(np.uint8)


def dwt_decompose(image: np.ndarray, levels: int = 2) -> Dict[str, np.ndarray]:
    """
    Perform 2-level DWT decomposition using Daubechies wavelet.
    
    Args:
        image (numpy.ndarray): Input grayscale image
        levels (int): Number of decomposition levels (default: 2)
        
    Returns:
        dict: DWT coefficients and original structure for reconstruction
    """
    # Convert to float64 for processing
    img_float = image.astype(np.float64)
    
    # First level decomposition
    coeffs1 = pywt.dwt2(img_float, 'db4')
    LL1, (LH1, HL1, HH1) = coeffs1
    
    # Second level decomposition on LL1
    coeffs2 = pywt.dwt2(LL1, 'db4')
    LL2, (LH2, HL2, HH2) = coeffs2
    
    # Return individual bands and structure for reconstruction
    return {
        'LL2': LL2,
        'LH2': LH2, 
        'HL2': HL2,
        'HH2': HH2,
        'LH1': LH1,
        'HL1': HL1, 
        'HH1': HH1,
        'original_shape': image.shape,
        'LL1_shape': LL1.shape
    }


def dct_on_ll(ll_band: np.ndarray) -> np.ndarray:
    """
    Apply 2D DCT to LL band for frequency domain analysis.
    
    Args:
        ll_band (numpy.ndarray): LL band from DWT decomposition
        
    Returns:
        numpy.ndarray: DCT coefficients matrix
    """
    return dct(dct(ll_band, axis=0, norm='ortho'), axis=1, norm='ortho')


def idct_on_ll(ll_dct: np.ndarray) -> np.ndarray:
    """
    Apply inverse 2D DCT to reconstruct LL band.
    
    Args:
        ll_dct (numpy.ndarray): DCT coefficients matrix
        
    Returns:
        numpy.ndarray: Reconstructed LL band
    """
    return idct(idct(ll_dct, axis=1, norm='ortho'), axis=0, norm='ortho')


def dwt_reconstruct(bands: Dict[str, np.ndarray]) -> np.ndarray:
    """
    Reconstruct image from DWT bands using inverse DWT.
    
    Args:
        bands (dict): DWT coefficient bands
        
    Returns:
        numpy.ndarray: Reconstructed image as uint8
    """
    # Reconstruct level 2
    coeffs2 = (bands['LL2'], (bands['LH2'], bands['HL2'], bands['HH2']))
    LL1_reconstructed = pywt.idwt2(coeffs2, 'db4')
    
    # Ensure LL1 matches the original shape if we have it
    if 'LL1_shape' in bands:
        target_shape = bands['LL1_shape']
        # Trim or pad to match original LL1 shape
        current_shape = LL1_reconstructed.shape
        
        if current_shape != target_shape:
            # Create output array with target shape
            LL1_adjusted = np.zeros(target_shape)
            
            # Copy data, trimming if larger, padding if smaller
            min_rows = min(current_shape[0], target_shape[0])
            min_cols = min(current_shape[1], target_shape[1])
            LL1_adjusted[:min_rows, :min_cols] = LL1_reconstructed[:min_rows, :min_cols]
            LL1_reconstructed = LL1_adjusted
    
    # Reconstruct level 1
    coeffs1 = (LL1_reconstructed, (bands['LH1'], bands['HL1'], bands['HH1']))
    image_reconstructed = pywt.idwt2(coeffs1, 'db4')
    
    # Trim to original image size if we have it
    if 'original_shape' in bands:
        target_shape = bands['original_shape']
        current_shape = image_reconstructed.shape
        
        if current_shape != target_shape:
            min_rows = min(current_shape[0], target_shape[0])
            min_cols = min(current_shape[1], target_shape[1])
            image_reconstructed = image_reconstructed[:min_rows, :min_cols]
    
    # Convert back to uint8, clipping to valid range
    return np.clip(np.round(image_reconstructed), 0, 255).astype(np.uint8)


def psnr(original: np.ndarray, reconstructed: np.ndarray) -> float:
    """
    Calculate Peak Signal-to-Noise Ratio between original and reconstructed images.
    
    Args:
        original (numpy.ndarray): Original image
        reconstructed (numpy.ndarray): Reconstructed image
        
    Returns:
        float: PSNR value in decibels
    """
    # Ensure same shape
    if original.shape != reconstructed.shape:
        raise ValueError("Images must have same shape for PSNR calculation")
    
    return float(peak_signal_noise_ratio(original, reconstructed, data_range=255))


def get_capacity(image_shape: Tuple[int, int], domain: str = 'dwt') -> int:
    """
    Calculate embedding capacity for given image dimensions.
    
    Args:
        image_shape (tuple): (height, width) of image
        domain (str): Transform domain ('dwt' or 'spatial')
        
    Returns:
        int: Maximum embedding capacity in bytes
    """
    height, width = image_shape
    
    if domain == 'dwt':
        # Multi-band capacity (7 bands total): LH1, HL1, LH2, HL2, HH1, HH2, LL2
        # Each DWT level reduces size by factor of 4
        level1_size = (height // 2) * (width // 2) * 3  # HH1, HL1, LH1  
        level2_size = (height // 4) * (width // 4) * 3  # HH2, HL2, LH2
        level2_ll = (height // 4) * (width // 4) * 1  # LL2 (low-freq details)
        
        total_coeffs = level1_size + level2_size + level2_ll
        
        # Aggressive utilization for 30-50% capacity (abstract requirement)
        # Use 38% of coefficients with threshold >= 8 for good balance
        usable_coeffs = int(total_coeffs * 0.38)
        return usable_coeffs // 8  # Convert bits to bytes
    
    elif domain == 'spatial':
        # LSB embedding capacity
        total_pixels = height * width
        return total_pixels // 8  # 1 bit per pixel -> bytes
    
    else:
        raise ValueError("Domain must be 'dwt' or 'spatial'")


def create_test_images():
    """Create simple test images if none available"""
    print("Creating test images...")
    
    # Create Lena-like pattern (checkerboard with gradients)
    lena = np.zeros((512, 512), dtype=np.uint8)
    for i in range(512):
        for j in range(512):
            # Checkerboard base pattern
            check = 128 + 64 * (((i//32) + (j//32)) % 2)
            # Add gradients
            grad_i = int(127 * i / 511)
            grad_j = int(127 * j / 511)
            lena[i, j] = np.clip((check + grad_i + grad_j) // 3, 0, 255)
    
    cv2.imwrite('test_lena.png', lena)
    
    # Create peppers-like pattern (circles and noise)
    peppers = np.random.randint(100, 156, (512, 512), dtype=np.uint8)
    center = (256, 256)
    for i in range(512):
        for j in range(512):
            dist = np.sqrt((i - center[0])**2 + (j - center[1])**2)
            if dist < 100:
                peppers[i, j] = min(255, peppers[i, j] + 100)
            elif dist < 200:
                peppers[i, j] = max(0, peppers[i, j] - 50)
    
    cv2.imwrite('test_peppers.png', peppers)
    print("✅ Created test_lena.png and test_peppers.png")


def test_image_processing_module():
    """Test function to verify image processing works correctly"""
    print("=== Module 3: Image Processing Tests ===")
    
    # Create test images if they don't exist
    test_images = ['test_lena.png', 'test_peppers.png']
    for img_path in test_images:
        if not os.path.exists(img_path):
            create_test_images()
            break
    
    for img_path in test_images:
        if not os.path.exists(img_path):
            continue
            
        print(f"\nTesting with {img_path}:")
        
        try:
            # Test 1: Image reading
            image = read_image(img_path)
            print(f"✅ Image loaded: shape {image.shape}, dtype {image.dtype}")
            
            # Test 2: DWT decomposition
            bands = dwt_decompose(image, levels=2)
            expected_bands = ['LL2', 'LH2', 'HL2', 'HH2', 'LH1', 'HL1', 'HH1']
            assert all(band in bands for band in expected_bands), "Missing DWT bands"
            print(f"✅ DWT decomposition: {len(bands)} bands")
            
            # Print band sizes for debugging
            for band_name, band_data in bands.items():
                if isinstance(band_data, np.ndarray):
                    print(f"   {band_name}: {band_data.shape}")
                else:
                    print(f"   {band_name}: {type(band_data)} (metadata)")
            
            # Test 3: DCT on LL band  
            ll_dct = dct_on_ll(bands['LL2'])
            ll_reconstructed = idct_on_ll(ll_dct)
            
            # Check DCT round-trip error
            dct_error = np.mean(np.abs(bands['LL2'] - ll_reconstructed))
            assert dct_error < 1e-10, f"DCT round-trip error too high: {dct_error}"
            print(f"✅ DCT round-trip: error {dct_error:.2e}")
            
            # Test 4: DWT reconstruction
            reconstructed = dwt_reconstruct(bands)
            
            # Calculate reconstruction quality
            psnr_value = psnr(image, reconstructed)
            pixel_diff = np.mean(np.abs(image.astype(float) - reconstructed.astype(float)))
            
            print(f"✅ DWT reconstruction: PSNR={psnr_value:.2f}dB, avg_error={pixel_diff:.3f}")
            
            # Verify target quality (>40dB PSNR, <1 pixel average error)
            assert psnr_value > 40.0, f"PSNR too low: {psnr_value:.2f}dB (target: >40dB)"
            assert pixel_diff < 1.0, f"Pixel error too high: {pixel_diff:.3f} (target: <1.0)"
            
            # Test 5: Capacity calculation
            capacity_dwt = get_capacity(image.shape, 'dwt') 
            capacity_spatial = get_capacity(image.shape, 'spatial')
            
            print(f"✅ Capacity: DWT={capacity_dwt} bytes, Spatial={capacity_spatial} bytes")
            
            # Verify reasonable capacity
            total_pixels = image.shape[0] * image.shape[1]
            assert capacity_dwt > 1000, f"DWT capacity too low: {capacity_dwt}"
            assert capacity_spatial == total_pixels // 8, "Spatial capacity calculation error"
            
        except Exception as e:
            print(f"❌ Test failed for {img_path}: {str(e)}")
            return False
    
    print("\n✅ All image processing tests PASSED! Module 3 ready.")
    return True


if __name__ == "__main__":
    test_image_processing_module()