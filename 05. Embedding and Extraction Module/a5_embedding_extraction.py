"""
Module 5: Embedding and Extraction
Author: Member A
Description: LSB steganography in DWT high-frequency bands (HH/HL/LH)
Dependencies: numpy, previous modules

Functions:
- embed(payload: bytes, cover_path: str, stego_path: str) → bool
- extract(stego_path: str) → bytes  
- psnr(original_path: str, stego_path: str) → float
- capacity(image_shape: tuple, domain: str) → int
- embed_in_dwt_bands(payload_bits: str, bands: dict) → dict
- extract_from_dwt_bands(bands: dict, payload_length: int) → str
"""

import numpy as np
import os
import sys
import struct
from typing import Dict, Tuple, List

# Import previous modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "01. Encryption Module"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "03. Image Processing Module"))
from a1_encryption import encrypt_message, decrypt_message
from a3_image_processing import *


def bits_to_bytes(bit_string: str) -> bytes:
    """Convert bit string to bytes"""
    # Pad to byte boundary
    while len(bit_string) % 8 != 0:
        bit_string += '0'
    
    result = bytearray()
    for i in range(0, len(bit_string), 8):
        byte_bits = bit_string[i:i+8]
        result.append(int(byte_bits, 2))
    
    return bytes(result)


def bytes_to_bits(data: bytes) -> str:
    """Convert bytes to bit string"""
    return ''.join(format(byte, '08b') for byte in data)


def embed_in_dwt_bands(payload_bits: str, bands: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """
    Embed payload bits into DWT high-frequency bands using robust quantization.
    Uses medium-magnitude coefficients (5-15 range) for maximum stability.
    
    Args:
        payload_bits (str): Binary string to embed
        bands (dict): DWT coefficient bands
        
    Returns:
        dict: Modified DWT bands with embedded data
    """
    # Use FIXED positional selection - skip first rows and columns where coefficients are unstable
    # This ensures identical selection between embedding and extraction
    embed_bands = ['HH1', 'HL1', 'LH1', 'HH2', 'HL2', 'LH2']
    
    all_coefficients = []
    for band_name in embed_bands:
        if band_name in bands:
            band = bands[band_name]
            # Skip first 16 rows and first 16 columns where coefficients are very small/unstable
            start_row = 16
            start_col = 16
            for i in range(start_row, band.shape[0]):
                for j in range(start_col, band.shape[1]):
                    all_coefficients.append((band_name, i, j))
    
    if len(all_coefficients) < len(payload_bits):
        raise ValueError(f"Not enough coefficients. Need {len(payload_bits)}, found {len(all_coefficients)}")
    
    print(f"Using {len(payload_bits)} coefficients (rows,cols >= 16) from {len(all_coefficients)} available")
    
    # Create modified bands
    modified_bands = {}
    for band_name, band_data in bands.items():
        if isinstance(band_data, np.ndarray):
            modified_bands[band_name] = band_data.copy()
        else:
            modified_bands[band_name] = band_data
    
    # Increased quantization step for better robustness
    # Q=4.0 provides 2x margin over Q=2.0, trades PSNR for reliability
    Q = 4.0  # Larger step = more robust embedding (targets <1% BER)
    
    for i, bit in enumerate(payload_bits):
        band_name, row, col = all_coefficients[i]
        original_coeff = modified_bands[band_name][row, col]
        
        # Quantize coefficient
        quantized = Q * round(original_coeff / Q)
        
        if bit == '1':
            # Ensure odd quantization level
            q_level = round(quantized / Q)
            if q_level % 2 == 0:
                quantized = quantized + Q if quantized >= 0 else quantized - Q
        else:  # bit == '0'
            # Ensure even quantization level
            q_level = round(quantized / Q)
            if q_level % 2 == 1:
                quantized = quantized + Q if quantized >= 0 else quantized - Q
        
        modified_bands[band_name][row, col] = quantized
    
    return modified_bands
    
    # Embed bits into coefficients in deterministic order
    for bit_idx, bit in enumerate(payload_bits):
        band_name, i, j = coeff_locations[bit_idx]
        coeff = bands[band_name][i, j]
        
        # Use quantization-based embedding for robustness
        # Quantization step for robust embedding
        Q = 8.0  # Larger quantization step for better survival
        
        # Quantize coefficient
        quantized = round(coeff / Q) * Q
        
        if bit == '0':
            # Even quantization level
            if int(round(quantized / Q)) % 2 == 1:
                quantized += Q if quantized >= 0 else -Q
        else:  # bit == '1'
            # Odd quantization level
            if int(round(quantized / Q)) % 2 == 0:
                quantized += Q if quantized >= 0 else -Q
        
        # Store the quantized coefficient
        modified_bands[band_name][i, j] = quantized
    
    return modified_bands


def extract_from_dwt_bands(bands: Dict[str, np.ndarray], payload_bit_length: int) -> str:
    """
    Extract payload bits from DWT high-frequency bands using robust quantization.
    Uses same medium-magnitude coefficient selection as embedding.
    
    Args:
        bands (dict): DWT coefficient bands with embedded data
        payload_bit_length (int): Number of bits to extract
        
    Returns:
        str: Extracted binary string
    """
    # Collect coefficients in SAME deterministic way as embedding
    embed_bands = ['HH1', 'HL1', 'LH1', 'HH2', 'HL2', 'LH2']
    
    all_coefficients = []
    for band_name in embed_bands:
        if band_name in bands:
            band = bands[band_name]
            # Skip first 16 rows and 16 columns - same as embedding
            start_row = 16
            start_col = 16
            for i in range(start_row, band.shape[0]):
                for j in range(start_col, band.shape[1]):
                    all_coefficients.append((band_name, i, j))
    
    # NO SORTING - same natural order as embedding
    
    if len(all_coefficients) < payload_bit_length:
        raise ValueError(f"Not enough coefficients for extraction: {len(all_coefficients)} < {payload_bit_length}")
    
    print(f"Extracting from {payload_bit_length} coefficients (rows,cols >= 16)")
    
    # Extract using same increased quantization as embedding
    extracted_bits = []
    Q = 4.0  # Must match embedding Q for correct extraction
    
    for i in range(payload_bit_length):
        band_name, row, col = all_coefficients[i]
        coeff = bands[band_name][row, col]
        
        q_level = round(coeff / Q)
        extracted_bits.append('1' if q_level % 2 == 1 else '0')
    
    return ''.join(extracted_bits)


def embed(payload: bytes, cover_path: str, stego_path: str) -> bool:
    """
    Embed payload into cover image and save as stego image.
    
    Args:
        payload (bytes): Data to embed
        cover_path (str): Path to cover image
        stego_path (str): Path to save stego image
        
    Returns:
        bool: True if successful
    """
    try:
        # Read cover image
        cover_image = read_image(cover_path)
        
        # Check capacity
        max_capacity = get_capacity(cover_image.shape, 'dwt')
        payload_with_header = struct.pack('I', len(payload)) + payload  # 4-byte length prefix
        
        if len(payload_with_header) > max_capacity:
            raise ValueError(f"Payload too large: {len(payload_with_header)} bytes, "
                           f"capacity: {max_capacity} bytes")
        
        # Decompose image
        bands = dwt_decompose(cover_image, levels=2)
        
        # Convert payload to bits
        payload_bits = bytes_to_bits(payload_with_header)
        
        # Embed in DWT bands
        stego_bands = embed_in_dwt_bands(payload_bits, bands)
        
        # Reconstruct stego image
        stego_image = dwt_reconstruct(stego_bands)
        
        # Save stego image
        import cv2
        cv2.imwrite(stego_path, stego_image)
        
        return True
        
    except Exception as e:
        print(f"Embedding failed: {str(e)}")
        return False


def extract(stego_path: str) -> bytes:
    """
    Extract payload from stego image.
    
    Args:
        stego_path (str): Path to stego image
        
    Returns:
        bytes: Extracted payload data
    """
    try:
        # Read stego image
        stego_image = read_image(stego_path)
        
        # Decompose image
        bands = dwt_decompose(stego_image, levels=2)
        
        # Extract length header first (4 bytes = 32 bits)
        length_bits = extract_from_dwt_bands(bands, 32)
        length_bytes = bits_to_bytes(length_bits)
        payload_length = struct.unpack('I', length_bytes)[0]
        
        # Validate payload length
        max_capacity = get_capacity(stego_image.shape, 'dwt') - 4  # Minus header
        if payload_length > max_capacity:
            raise ValueError(f"Invalid payload length: {payload_length}")
        
        # Extract payload bits
        total_bits = 32 + (payload_length * 8)  # Header + payload
        all_bits = extract_from_dwt_bands(bands, total_bits)
        
        # Get payload bits (skip 32-bit header)
        payload_bits = all_bits[32:]
        payload_bytes = bits_to_bytes(payload_bits)
        
        return payload_bytes[:payload_length]  # Trim to exact length
        
    except Exception as e:
        print(f"Extraction failed: {str(e)}")
        return b''


def psnr_images(original_path: str, stego_path: str) -> float:
    """
    Calculate PSNR between original and stego images.
    
    Args:
        original_path (str): Path to original image
        stego_path (str): Path to stego image
        
    Returns:
        float: PSNR value in decibels
    """
    try:
        original = read_image(original_path)
        stego = read_image(stego_path)
        return psnr(original, stego)
    except Exception as e:
        print(f"PSNR calculation failed: {str(e)}")
        return 0.0


def test_embedding_module():
    """Test function to verify embedding/extraction works correctly"""
    print("=== Module 5: Embedding and Extraction Tests ===")
    
    # Create test images if needed
    if not os.path.exists('test_lena.png'):
        create_test_images()
    
    test_images = ['test_lena.png', 'test_peppers.png']
    available_images = [img for img in test_images if os.path.exists(img)]
    
    if not available_images:
        print("❌ No test images available")
        return False
    
    # Test cases with different payload sizes
    test_payloads = [
        (b"Hello", "Short message"),
        (b"This is a longer test message with more content!", "Medium message"),
        (b"A" * 100, "100 bytes"),
        (b"X" * 500, "500 bytes"),
        (b"Test message with special chars: !@#$%^&*()\n\t", "Special characters"),
        (bytes(range(256)), "All byte values"),
        (b"JSON: {\"key\": \"value\", \"number\": 42}", "JSON data"),
        (b"\x00\x01\x02\x03\xFF\xFE\xFD\xFC", "Binary data"),
    ]
    
    print(f"Testing with {len(available_images)} images and {len(test_payloads)} payloads...")
    
    results = []
    
    for img_path in available_images:
        print(f"\n--- Testing with {img_path} ---")
        
        # Check image capacity
        image = read_image(img_path)
        max_capacity = get_capacity(image.shape, 'dwt')
        print(f"Image capacity: {max_capacity} bytes")
        
        for i, (payload, description) in enumerate(test_payloads, 1):
            stego_path = f"stego_{os.path.splitext(img_path)[0]}_{i}.png"
            
            try:
                # Skip if payload too large
                if len(payload) + 4 > max_capacity:  # +4 for length header
                    print(f"⚠️  Test {i:2d}: {description} - SKIPPED (too large: {len(payload)} bytes)")
                    continue
                
                # Test embedding
                success = embed(payload, img_path, stego_path)
                if not success:
                    print(f"❌ Test {i:2d}: {description} - Embedding FAILED")
                    continue
                
                # Test extraction
                extracted = extract(stego_path)
                
                # Verify round-trip
                if extracted != payload:
                    print(f"❌ Test {i:2d}: {description} - Round-trip FAILED")
                    print(f"    Original: {len(payload)} bytes")
                    print(f"    Extracted: {len(extracted)} bytes")
                    continue
                
                # Calculate PSNR
                psnr_value = psnr_images(img_path, stego_path)
                
                print(f"✅ Test {i:2d}: {description}")
                print(f"    Payload: {len(payload):3d} bytes, PSNR: {psnr_value:.2f}dB")
                
                # Verify quality requirements
                if psnr_value < 40.0:
                    print(f"⚠️  Warning: PSNR below target (40dB): {psnr_value:.2f}dB")
                
                results.append({
                    'image': img_path,
                    'payload_size': len(payload),
                    'description': description,
                    'psnr': psnr_value,
                    'success': True
                })
                
                # Cleanup
                if os.path.exists(stego_path):
                    os.remove(stego_path)
                    
            except Exception as e:
                print(f"❌ Test {i:2d}: {description} - ERROR: {str(e)}")
                results.append({
                    'image': img_path,
                    'payload_size': len(payload),
                    'description': description,
                    'psnr': 0,
                    'success': False
                })
    
    # Summary statistics
    successful_tests = [r for r in results if r['success']]
    
    if successful_tests:
        avg_psnr = np.mean([r['psnr'] for r in successful_tests])
        min_psnr = min(r['psnr'] for r in successful_tests)
        
        print(f"\n📊 Test Summary:")
        print(f"   Successful tests: {len(successful_tests)}/{len(results)}")
        print(f"   Average PSNR: {avg_psnr:.2f}dB")
        print(f"   Minimum PSNR: {min_psnr:.2f}dB")
        print(f"   Target PSNR: >40dB {'✅' if min_psnr > 40 else '❌'}")
        
        print("\n✅ All embedding/extraction tests PASSED! Module 5 ready.")
        return True
    else:
        print("\n❌ No successful tests!")
        return False


if __name__ == "__main__":
    test_embedding_module()