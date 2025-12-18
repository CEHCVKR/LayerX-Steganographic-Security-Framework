"""
LayerX Steganographic Security Framework - SENDER
Hybrid Mode: Security + Quality + Speed

Usage:
    python sender.py <cover_image> <output_image> <message> [password]
    
Example:
    python sender.py cover.png stego.png "Secret message" mypassword123
"""

import sys
import os

# Add module paths
sys.path.append('01. Encryption Module')
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')
sys.path.append('06. Optimization Module')

from a1_encryption import encrypt_message
from a4_compression import compress_huffman, create_payload
from a5_embedding_extraction import embed
from a3_image_processing import get_capacity, read_image


def send_message(cover_path: str, stego_path: str, message: str, password: str, 
                 optimization: str = 'hybrid') -> bool:
    """
    Embed secret message into cover image.
    
    Args:
        cover_path: Path to cover image
        stego_path: Path to save stego image
        message: Secret message to hide
        password: Encryption password
        optimization: 'hybrid' (default), 'chaos', 'fixed', 'aco'
        
    Returns:
        True if successful
    """
    try:
        # Step 1: Encrypt message
        print(f"[1/4] Encrypting message ({len(message)} chars)...")
        ciphertext, salt, iv = encrypt_message(message, password)
        
        # Step 2: Compress encrypted data
        print(f"[2/4] Compressing data...")
        # Prepend salt and IV to ciphertext before compression
        ciphertext_with_header = salt + iv + ciphertext
        compressed, tree = compress_huffman(ciphertext_with_header)
        payload = create_payload(ciphertext_with_header, tree, compressed)
        
        # Check capacity
        cover = read_image(cover_path)
        capacity = get_capacity(cover.shape[:2], 'dwt')
        
        if len(payload) > capacity - 4:  # -4 for header
            print(f"❌ Error: Payload too large ({len(payload)} bytes)")
            print(f"   Image capacity: {capacity-4} bytes")
            print(f"   Try a larger image or shorter message")
            return False
        
        print(f"   Payload: {len(payload)} bytes / {capacity-4} bytes capacity")
        
        # Step 3: Select optimization mode
        if optimization == 'hybrid':
            # HYBRID MODE: Use FIXED for reliability (Chaos is experimental)
            # Fixed mode provides: Speed + Quality + Security (via AES-256)
            opt_mode = 'fixed'
            print(f"[3/4] Embedding (Hybrid mode: FIXED for reliability)...")
        else:
            opt_mode = optimization
            mode_desc = {
                'chaos': 'CHAOS - Steganalysis-resistant (experimental)',
                'aco': 'ACO - Quality-optimized (experimental)',
                'fixed': 'FIXED - High-speed + reliable'
            }
            print(f"[3/4] Embedding ({mode_desc.get(opt_mode, opt_mode)})...")
        
        # Step 4: Embed payload
        success = embed(payload, cover_path, stego_path, optimization=opt_mode)
        
        if success:
            print(f"[4/4] ✅ SUCCESS! Stego image saved: {stego_path}")
            print(f"\n📊 Statistics:")
            print(f"   Message length: {len(message)} characters")
            print(f"   Encrypted size: {len(ciphertext)} bytes")
            print(f"   Final payload: {len(payload)} bytes")
            print(f"   Optimization: {opt_mode.upper()}")
            return True
        else:
            print(f"[4/4] ❌ Embedding failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Command-line interface."""
    if len(sys.argv) < 4:
        print(__doc__)
        print("\n❌ Error: Not enough arguments")
        print("\nRequired arguments:")
        print("  1. Cover image path (e.g., cover.png)")
        print("  2. Output stego image path (e.g., stego.png)")
        print("  3. Secret message (in quotes if contains spaces)")
        print("  4. Password (optional, default: 'password123')")
        print("\nOptional: Set LAYERX_MODE environment variable:")
        print("  LAYERX_MODE=hybrid  (default: adaptive security+speed)")
        print("  LAYERX_MODE=chaos   (maximum security)")
        print("  LAYERX_MODE=fixed   (maximum speed)")
        print("  LAYERX_MODE=aco     (maximum quality)")
        sys.exit(1)
    
    cover_path = sys.argv[1]
    stego_path = sys.argv[2]
    message = sys.argv[3]
    password = sys.argv[4] if len(sys.argv) > 4 else "password123"
    optimization = os.environ.get('LAYERX_MODE', 'hybrid')
    
    # Validate files
    if not os.path.exists(cover_path):
        print(f"❌ Error: Cover image not found: {cover_path}")
        sys.exit(1)
    
    print("="*80)
    print("LayerX Steganographic Security Framework - SENDER")
    print("="*80)
    
    success = send_message(cover_path, stego_path, message, password, optimization)
    
    print("="*80)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
