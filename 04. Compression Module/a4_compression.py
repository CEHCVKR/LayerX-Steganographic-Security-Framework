"""
Module 4: Compression  
Author: Member A
Description: Huffman compression for encrypted data (post-encryption, pre-embedding)
Dependencies: heapq, collections, reedsolo

Functions:
- compress_huffman(data: bytes) → (compressed: bytes, tree: bytes)
- decompress_huffman(compressed: bytes, tree: bytes) → bytes
- create_payload(message_bytes: bytes, tree_bytes: bytes, compressed: bytes) → bytes
- parse_payload(payload: bytes) → (message_len: int, tree_bytes: bytes, compressed: bytes)
"""

import heapq
import pickle
from collections import Counter, defaultdict
from typing import Tuple, Dict, Optional
import struct
from reedsolo import RSCodec


class HuffmanNode:
    """Node for Huffman tree"""
    def __init__(self, char: Optional[int] = None, freq: int = 0, left=None, right=None):
        self.char = char  # byte value (0-255) or None for internal nodes
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq


class HuffmanCompressor:
    """Huffman compression implementation"""
    
    @staticmethod
    def _build_frequency_table(data: bytes) -> Dict[int, int]:
        """Build frequency table for input bytes"""
        if not data:
            return {}
        return dict(Counter(data))
    
    @staticmethod
    def _build_huffman_tree(freq_table: Dict[int, int]) -> Optional[HuffmanNode]:
        """Build Huffman tree from frequency table"""
        if not freq_table:
            return None
        
        # Handle single byte case
        if len(freq_table) == 1:
            byte_val = next(iter(freq_table))
            return HuffmanNode(char=byte_val, freq=freq_table[byte_val])
        
        # Create priority queue
        heap = []
        for byte_val, freq in freq_table.items():
            heapq.heappush(heap, HuffmanNode(char=byte_val, freq=freq))
        
        # Build tree bottom-up
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
            heapq.heappush(heap, merged)
        
        return heap[0]
    
    @staticmethod
    def _build_codes(root: HuffmanNode) -> Dict[int, str]:
        """Build prefix codes from Huffman tree"""
        if not root:
            return {}
        
        codes = {}
        
        def traverse(node, code=""):
            if node.char is not None:  # Leaf node
                codes[node.char] = code if code else "0"  # Handle single char case
            else:
                if node.left:
                    traverse(node.left, code + "0")
                if node.right:
                    traverse(node.right, code + "1")
        
        traverse(root)
        return codes
    
    @staticmethod
    def _serialize_tree(root: HuffmanNode) -> bytes:
        """Serialize Huffman tree to bytes using pickle"""
        return pickle.dumps(root)
    
    @staticmethod
    def _deserialize_tree(tree_bytes: bytes) -> HuffmanNode:
        """Deserialize Huffman tree from bytes"""
        return pickle.loads(tree_bytes)


def compress_huffman(data: bytes) -> Tuple[bytes, bytes]:
    """
    Compress data using Huffman coding.
    
    Args:
        data (bytes): Input data to compress
        
    Returns:
        tuple: (compressed_data: bytes, tree_data: bytes)
    """
    if not data:
        return b'', b''
    
    # Build frequency table and Huffman tree
    freq_table = HuffmanCompressor._build_frequency_table(data)
    root = HuffmanCompressor._build_huffman_tree(freq_table)
    
    if not root:
        return b'', b''
    
    # Build prefix codes
    codes = HuffmanCompressor._build_codes(root)
    
    # Encode data
    encoded_bits = ''.join(codes[byte] for byte in data)
    
    # Convert bit string to bytes (pad to byte boundary)
    padding = 8 - (len(encoded_bits) % 8)
    if padding != 8:
        encoded_bits += '0' * padding
    
    compressed_bytes = bytearray()
    for i in range(0, len(encoded_bits), 8):
        byte_str = encoded_bits[i:i+8]
        compressed_bytes.append(int(byte_str, 2))
    
    # Serialize tree
    tree_bytes = HuffmanCompressor._serialize_tree(root)
    
    # Prepend padding info to compressed data
    compressed_data = struct.pack('B', padding) + bytes(compressed_bytes)
    
    return compressed_data, tree_bytes


def decompress_huffman(compressed_data: bytes, tree_bytes: bytes) -> bytes:
    """
    Decompress Huffman-compressed data.
    
    Args:
        compressed_data (bytes): Compressed data
        tree_bytes (bytes): Serialized Huffman tree
        
    Returns:
        bytes: Decompressed original data
    """
    if not compressed_data or not tree_bytes:
        return b''
    
    # Deserialize tree
    root = HuffmanCompressor._deserialize_tree(tree_bytes)
    
    if not root:
        return b''
    
    # Extract padding info
    padding = compressed_data[0]
    compressed_bytes = compressed_data[1:]
    
    # Convert bytes back to bit string
    bit_string = ''.join(format(byte, '08b') for byte in compressed_bytes)
    
    # Remove padding
    if padding and padding < 8:
        bit_string = bit_string[:-padding]
    
    # Handle single character tree
    if root.char is not None:
        # For single character, each bit represents one instance
        char_count = len(bit_string)
        return bytes([root.char] * char_count)
    
    # Decode using tree traversal
    decoded = bytearray()
    current = root
    
    for bit in bit_string:
        if bit == '0' and current.left:
            current = current.left
        elif bit == '1' and current.right:
            current = current.right
        else:
            raise ValueError("Invalid bit sequence in compressed data")
        
        # Check if we reached a leaf
        if current.char is not None:
            decoded.append(current.char)
            current = root
    
    return bytes(decoded)


# Reed-Solomon Error Correction with adaptive strength based on payload size
def get_rs_codec(data_size: int) -> RSCodec:
    """
    Select appropriate RS codec based on data size.
    Larger payloads need stronger error correction.
    
    Args:
        data_size: Size of data to protect (bytes)
        
    Returns:
        RSCodec: Appropriate codec for the data size
    """
    if data_size < 500:  # Small payload (<500 bytes)
        return RSCodec(30)  # Can fix 15 byte errors
    elif data_size < 2000:  # Medium payload (500-2000 bytes)
        return RSCodec(60)  # Can fix 30 byte errors
    else:  # Large payload (>2000 bytes)
        return RSCodec(120)  # Can fix 60 byte errors


def create_payload(message_bytes: bytes, tree_bytes: bytes, compressed: bytes) -> bytes:
    """
    Create payload with adaptive Reed-Solomon error correction on tree data.
    Format: [msg_len:4bytes][tree_len_ecc:4bytes][tree_with_ecc][compressed]
    
    Args:
        message_bytes (bytes): Original message (for length)
        tree_bytes (bytes): Serialized Huffman tree
        compressed (bytes): Compressed data
        
    Returns:
        bytes: Complete payload with adaptive ECC protection for tree
    """
    msg_len = len(message_bytes)
    
    # Select appropriate ECC codec based on tree size
    rs_codec = get_rs_codec(len(tree_bytes))
    
    # Apply adaptive Reed-Solomon error correction to tree
    tree_with_ecc = rs_codec.encode(tree_bytes)
    tree_ecc_len = len(tree_with_ecc)
    
    payload = struct.pack('I', msg_len)  # 4 bytes message length
    payload += struct.pack('I', tree_ecc_len)  # 4 bytes ECC-protected tree length
    payload += tree_with_ecc
    payload += compressed
    
    return payload


def parse_payload(payload: bytes) -> Tuple[int, bytes, bytes]:
    """
    Parse payload with Reed-Solomon error correction decoding.
    Format: [msg_len:4bytes][tree_len_ecc:4bytes][tree_with_ecc][compressed]
    
    Args:
        payload (bytes): Complete payload
        
    Returns:
        tuple: (message_length, tree_bytes, compressed_bytes)
    """
    if len(payload) < 8:
        raise ValueError("Payload too short")
    
    # Extract lengths
    msg_len = struct.unpack('I', payload[0:4])[0]
    tree_ecc_len = struct.unpack('I', payload[4:8])[0]
    
    # Extract ECC-protected tree and compressed data
    tree_start = 8
    tree_end = tree_start + tree_ecc_len
    
    if len(payload) < tree_end:
        raise ValueError("Payload corrupted: tree data incomplete")
    
    tree_with_ecc = payload[tree_start:tree_end]
    
    # Try decoding with different ECC strengths (we don't know which was used)
    # Try from strongest to weakest
    for codec_strength in [120, 60, 30]:
        try:
            rs_codec = RSCodec(codec_strength)
            tree_bytes = rs_codec.decode(tree_with_ecc)[0]
            break  # Success!
        except Exception:
            continue  # Try next strength
    else:
        raise ValueError("Tree ECC decoding failed with all codec strengths")
    
    compressed = payload[tree_end:]
    
    return msg_len, tree_bytes, compressed


def test_compression_module():
    """Test function to verify compression works correctly"""
    print("=== Module 4: Compression Tests ===")
    
    # Test cases with different data types and sizes
    test_cases = [
        (b"", "Empty data"),
        (b"A", "Single character"),
        (b"AAAA", "Repeated character"),
        (b"ABABABAB", "Two characters alternating"),
        (b"Hello World! This is a test message.", "Short text"),
        (b"The quick brown fox jumps over the lazy dog. " * 10, "Medium repeated text"),
        (bytes(range(256)), "All byte values"),
        (b"A" * 1000, "Long repeated character"),
        (b"Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 20, "Long Lorem ipsum"),
        (bytes([i % 256 for i in range(10000)]), "Large varied data")
    ]
    
    print(f"Testing {len(test_cases)} compression test cases...")
    
    for i, (test_data, description) in enumerate(test_cases, 1):
        try:
            # Test compression
            compressed, tree = compress_huffman(test_data)
            
            # Test decompression
            decompressed = decompress_huffman(compressed, tree)
            
            # Verify round-trip
            assert decompressed == test_data, f"Round-trip failed for: {description}"
            
            # Calculate compression ratio
            if test_data:
                compression_ratio = len(compressed) / len(test_data) * 100
            else:
                compression_ratio = 0
            
            print(f"✅ Test {i:2d}: {description}")
            print(f"    Original: {len(test_data):5d} bytes, Compressed: {len(compressed):5d} bytes, "
                  f"Tree: {len(tree):4d} bytes, Ratio: {compression_ratio:5.1f}%")
            
            # Test payload format
            payload = create_payload(test_data, tree, compressed)
            msg_len, tree_parsed, compressed_parsed = parse_payload(payload)
            
            assert msg_len == len(test_data), "Message length mismatch"
            assert tree_parsed == tree, "Tree data mismatch"
            assert compressed_parsed == compressed, "Compressed data mismatch"
            
        except Exception as e:
            print(f"❌ Test {i:2d}: FAILED - {description}: {str(e)}")
            return False
    
    # Test specific compression effectiveness on cipher-like data
    print("\n--- Cipher-like Data Tests ---")
    
    # Simulate encrypted data (should have high entropy)
    import secrets
    cipher_data = secrets.token_bytes(1024)
    compressed, tree = compress_huffman(cipher_data)
    cipher_ratio = len(compressed) / len(cipher_data) * 100
    
    print(f"✅ Cipher data (1024 bytes): Compressed to {len(compressed)} bytes ({cipher_ratio:.1f}%)")
    
    # Test text-derived cipher (should compress better)
    text = "This is a test message that will be 'encrypted' and then compressed. " * 20
    text_bytes = text.encode('utf-8')
    
    # Simulate simple XOR 'encryption' (creates patterns Huffman can exploit)
    key = b'\x42'
    cipher_text = bytes([b ^ key[0] for b in text_bytes])
    
    compressed_text, tree_text = compress_huffman(cipher_text)
    text_ratio = len(compressed_text) / len(cipher_text) * 100
    
    print(f"✅ Text-derived cipher ({len(cipher_text)} bytes): "
          f"Compressed to {len(compressed_text)} bytes ({text_ratio:.1f}%)")
    
    # Verify we meet target compression ratios
    assert text_ratio < 80, f"Text compression ratio too low: {text_ratio:.1f}% (target: <80%)"
    
    print("\n✅ All compression tests PASSED! Module 4 ready.")
    print(f"📊 Compression Summary:")
    print(f"   - High entropy data: ~{cipher_ratio:.0f}% ratio (no significant compression)")
    print(f"   - Text-derived data: ~{text_ratio:.0f}% ratio (good compression)")
    return True


if __name__ == "__main__":
    test_compression_module()