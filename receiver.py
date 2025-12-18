"""
LayerX Steganographic Security Framework - RECEIVER
Hybrid Mode: Security + Quality + Speed

Usage:
    python receiver.py <stego_image> [password]
    
Example:
    python receiver.py stego.png mypassword123
"""

import sys
import os

# Add module paths
sys.path.append('01. Encryption Module')
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')
sys.path.append('06. Optimization Module')

from a1_encryption import decrypt_message
from a4_compression import decompress_huffman, parse_payload
from a5_embedding_extraction import extract


def receive_message(stego_path: str, password: str, optimization: str = 'hybrid') -> str:
    """
    Extract secret message from stego image.
    
    Args:
        stego_path: Path to stego image
        password: Decryption password
        optimization: 'hybrid' (auto-detect), 'chaos', 'fixed', 'aco'
        
    Returns:
        Decrypted message or empty string if failed
    """
    try:
        print(f"[1/5] Reading stego image...")
        
        # Step 1: Auto-detect optimization method if hybrid
        if optimization == 'hybrid':
            # Try methods in order: fixed (most reliable), chaos, aco
            methods = ['fixed', 'chaos', 'aco']
            print(f"[2/5] Auto-detecting optimization method...")
            
            extracted = None
            used_method = None
            
            for method in methods:
                try:
                    print(f"   Trying {method.upper()}...")
                    extracted = extract(stego_path, optimization=method)
                    if extracted and len(extracted) > 0:
                        # Validate by attempting to parse
                        msg_len, tree_ext, compressed_ext = parse_payload(extracted)
                        if msg_len > 0:
                            used_method = method
                            print(f"   ✓ Detected: {method.upper()} mode")
                            break
                except:
                    continue
            
            if not used_method:
                print(f"❌ Error: Could not detect optimization method")
                print(f"   Try specifying method manually: LAYERX_MODE=chaos/fixed/aco")
                return ""
            
            optimization = used_method
        else:
            # Step 2: Extract payload using specified method
            mode_desc = {
                'chaos': 'CHAOS mode',
                'aco': 'ACO mode',
                'fixed': 'FIXED mode'
            }
            print(f"[2/5] Extracting payload ({mode_desc.get(optimization, optimization)})...")
            extracted = extract(stego_path, optimization=optimization)
        
        if not extracted:
            print(f"❌ Error: Extraction failed")
            return ""
        
        # Step 3: Parse payload (extracts salt, IV, and encrypted data)
        print(f"[3/5] Parsing payload...")
        msg_len, tree_ext, compressed_ext = parse_payload(extracted)
        
        # Step 4: Decompress to get ciphertext with salt/IV
        print(f"[4/5] Decompressing data...")
        ciphertext_with_header = decompress_huffman(compressed_ext, tree_ext)
        
        # Salt and IV are prepended by encrypt_message, extract them
        salt = ciphertext_with_header[:16]
        iv = ciphertext_with_header[16:32]
        actual_ciphertext = ciphertext_with_header[32:]
        
        # Step 5: Decrypt
        print(f"[5/5] Decrypting message...")
        message = decrypt_message(actual_ciphertext, password, salt, iv)
        
        print(f"\n✅ SUCCESS!")
        print(f"\n📊 Statistics:")
        print(f"   Payload size: {len(extracted)} bytes")
        print(f"   Compressed size: {len(compressed_ext)} bytes")
        print(f"   Message length: {len(message)} characters")
        print(f"   Optimization: {optimization.upper()}")
        
        return message
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return ""


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n❌ Error: Not enough arguments")
        print("\nRequired arguments:")
        print("  1. Stego image path (e.g., stego.png)")
        print("  2. Password (optional, default: 'password123')")
        print("\nOptional: Set LAYERX_MODE environment variable:")
        print("  LAYERX_MODE=hybrid  (default: auto-detect method)")
        print("  LAYERX_MODE=chaos   (if embedded with chaos)")
        print("  LAYERX_MODE=fixed   (if embedded with fixed)")
        print("  LAYERX_MODE=aco     (if embedded with aco)")
        sys.exit(1)
    
    stego_path = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else "password123"
    optimization = os.environ.get('LAYERX_MODE', 'hybrid')
    
    # Validate files
    if not os.path.exists(stego_path):
        print(f"❌ Error: Stego image not found: {stego_path}")
        sys.exit(1)
    
    print("="*80)
    print("LayerX Steganographic Security Framework - RECEIVER")
    print("="*80)
    
    message = receive_message(stego_path, password, optimization)
    
    if message:
        print("\n" + "="*80)
        print("📩 EXTRACTED MESSAGE:")
        print("="*80)
        print(message)
        print("="*80)
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print("❌ Failed to extract message")
        print("="*80)
        sys.exit(1)


if __name__ == '__main__':
    main()
