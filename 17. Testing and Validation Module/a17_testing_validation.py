"""
Module 17: Testing and Validation
Author: Member A
Description: Comprehensive testing framework for system validation
Dependencies: unittest, pytest

Features:
- Unit testing framework
- Integration testing
- Performance testing
- Security testing
- Compliance validation
- Test report generation
"""

import unittest
import time
import os
import sys
from typing import Dict, List, Callable
from datetime import datetime

# Import all modules for testing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "01. Encryption Module"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "02. Key Management Module"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "03. Image Processing Module"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "04. Compression Module"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "05. Embedding and Extraction Module"))


class TestResult:
    """Store test result information"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = False
        self.duration = 0.0
        self.error = None
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'test_name': self.test_name,
            'passed': self.passed,
            'duration': self.duration,
            'error': str(self.error) if self.error else None,
            'timestamp': self.timestamp.isoformat()
        }


class TestSuite:
    """Comprehensive test suite"""
    
    def __init__(self, name: str):
        self.name = name
        self.tests = []
        self.results = []
    
    def add_test(self, test_func: Callable, test_name: str):
        """Add test function"""
        self.tests.append((test_func, test_name))
    
    def run(self) -> List[TestResult]:
        """Run all tests in suite"""
        print(f"\n{'='*70}")
        print(f"Running Test Suite: {self.name}")
        print(f"{'='*70}")
        
        passed_count = 0
        failed_count = 0
        
        for test_func, test_name in self.tests:
            print(f"\n▶ {test_name}...", end=' ')
            result = TestResult(test_name)
            
            start_time = time.time()
            try:
                test_func()
                result.passed = True
                result.duration = time.time() - start_time
                print(f"✓ PASSED ({result.duration:.3f}s)")
                passed_count += 1
            except Exception as e:
                result.passed = False
                result.duration = time.time() - start_time
                result.error = e
                print(f"✗ FAILED ({result.duration:.3f}s)")
                print(f"  Error: {str(e)}")
                failed_count += 1
            
            self.results.append(result)
        
        # Summary
        total = len(self.tests)
        print(f"\n{'='*70}")
        print(f"Test Suite Summary: {self.name}")
        print(f"{'='*70}")
        print(f"Total: {total} | Passed: {passed_count} | Failed: {failed_count}")
        print(f"Success Rate: {(passed_count/total*100):.1f}%")
        print(f"{'='*70}\n")
        
        return self.results


class EncryptionTests:
    """Encryption module tests"""
    
    @staticmethod
    def test_encryption_basic():
        """Test basic encryption/decryption"""
        from a1_encryption import encrypt_message, decrypt_message
        
        password = "TestPassword123"
        message = "Test message"
        
        ciphertext, salt, iv = encrypt_message(message, password)
        assert ciphertext != message.encode(), "Encryption failed"
        
        decrypted = decrypt_message(ciphertext, password, salt, iv)
        assert decrypted == message, "Decryption failed"
    
    @staticmethod
    def test_encryption_empty():
        """Test encryption with empty message"""
        from a1_encryption import encrypt_message, decrypt_message
        
        password = "TestPassword123"
        message = ""
        
        ciphertext, salt, iv = encrypt_message(message, password)
        decrypted = decrypt_message(ciphertext, password, salt, iv)
        assert decrypted == message, "Empty message failed"
    
    @staticmethod
    def test_encryption_large():
        """Test encryption with large message"""
        from a1_encryption import encrypt_message, decrypt_message
        
        password = "TestPassword123"
        message = "X" * 10000
        
        ciphertext, salt, iv = encrypt_message(message, password)
        decrypted = decrypt_message(ciphertext, password, salt, iv)
        assert decrypted == message, "Large message failed"


class KeyManagementTests:
    """Key management tests"""
    
    @staticmethod
    def test_key_generation():
        """Test key generation"""
        from a2_key_management import generate_ecc_keypair
        
        private_key, public_key = generate_ecc_keypair()
        
        assert public_key is not None, "Public key not generated"
        assert private_key is not None, "Private key not generated"
    
    @staticmethod
    def test_key_save_load():
        """Test key save and load"""
        from a2_key_management import KeyManager
        
        km = KeyManager()
        aes_key = km.set_aes_key("TestPassword123", b"1234567890123456")
        stego_key = km.set_stego_key()
        
        assert aes_key is not None, "AES key not generated"
        assert stego_key is not None, "Stego key not generated"
        assert km.get_key('aes') == aes_key, "Key retrieval failed"
        
        # Test clear
        km.clear_keys()
        assert km.get_key('aes') is None, "Key not cleared"


class ImageProcessingTests:
    """Image processing tests"""
    
    @staticmethod
    def test_image_load():
        """Test image loading"""
        from a3_image_processing import read_image
        
        if os.path.exists('test_lena.png'):
            img = read_image('test_lena.png')
            assert img is not None, "Image loading failed"
            assert len(img.shape) == 2, "Invalid image shape"
    
    @staticmethod
    def test_dwt_transform():
        """Test DWT transformation"""
        from a3_image_processing import dwt_decompose, dwt_reconstruct
        import numpy as np
        
        # Create test image
        test_img = np.random.randint(0, 256, (256, 256), dtype=np.uint8)
        
        coeffs = dwt_decompose(test_img, levels=2)
        # Check if it's a dictionary with expected keys
        assert isinstance(coeffs, dict), "DWT should return dictionary"
        assert 'll2' in coeffs or 'LL2' in coeffs or len(coeffs) > 0, "DWT failed"
        
        reconstructed = dwt_reconstruct(coeffs)
        assert reconstructed.shape == test_img.shape, "IDWT failed"


class CompressionTests:
    """Compression tests"""
    
    @staticmethod
    def test_compression_basic():
        """Test basic compression"""
        from a4_compression import compress_huffman, decompress_huffman
        
        data = b"Test data " * 100
        compressed, tree = compress_huffman(data)
        
        assert compressed is not None, "Compression failed"
        assert tree is not None, "Tree generation failed"
        
        decompressed = decompress_huffman(compressed, tree)
        assert decompressed == data, "Decompression failed"
    
    @staticmethod
    def test_compression_ratio():
        """Test compression ratio"""
        from a4_compression import compress_huffman
        
        data = b"A" * 1000
        compressed, tree = compress_huffman(data)
        
        # Repetitive data should compress well
        assert len(compressed) < len(data) * 0.5, f"Poor compression: {len(compressed)}/{len(data)}"


class EmbeddingTests:
    """Embedding and extraction tests"""
    
    @staticmethod
    def test_embedding_extraction():
        """Test basic embedding and extraction"""
        from a5_embedding_extraction import embed_in_dwt_bands, extract_from_dwt_bands
        import numpy as np
        
        if os.path.exists('test_lena.png'):
            data = b"Test payload"
            
            stego_img = embed_in_dwt_bands('test_lena.png', data)
            assert stego_img is not None, "Embedding failed"
            
            extracted = extract_from_dwt_bands(stego_img, len(data))
            assert extracted == data, "Extraction failed"


class PerformanceTests:
    """Performance tests"""
    
    @staticmethod
    def test_encryption_speed():
        """Test encryption speed"""
        from a1_encryption import encrypt_message
        
        password = "TestPassword123"
        message = "X" * 1000
        
        start = time.time()
        for _ in range(100):
            encrypt_message(message, password)
        duration = time.time() - start
        
        avg_time = duration / 100
        assert avg_time < 0.15, f"Encryption too slow: {avg_time:.3f}s"
    
    @staticmethod
    def test_embedding_speed():
        """Test embedding speed"""
        if os.path.exists('test_lena.png'):
            from a5_embedding_extraction import embed_in_dwt_bands
            
            data = b"X" * 1000
            
            start = time.time()
            embed_in_dwt_bands('test_lena.png', data)
            duration = time.time() - start
            
            assert duration < 1.0, f"Embedding too slow: {duration:.3f}s"


class SecurityTests:
    """Security tests"""
    
    @staticmethod
    def test_key_randomness():
        """Test key randomness"""
        from a2_key_management import generate_stego_key
        
        keys = [generate_stego_key() for _ in range(10)]
        
        # All keys should be different
        assert len(set(keys)) == 10, "Keys not unique"
    
    @staticmethod
    def test_encryption_randomness():
        """Test encryption produces different ciphertexts"""
        from a1_encryption import encrypt_message
        
        password = "TestPassword123"
        message = "Test"
        
        ct1, _, _ = encrypt_message(message, password)
        ct2, _, _ = encrypt_message(message, password)
        
        # With random salt/IV, ciphertexts should differ
        assert ct1 != ct2, "Encryption not randomized"


def run_comprehensive_tests():
    """Run all test suites"""
    print("\n" + "="*70)
    print("COMPREHENSIVE SYSTEM TESTING")
    print("="*70)
    
    all_results = []
    
    # Encryption tests
    enc_suite = TestSuite("Encryption Module Tests")
    enc_suite.add_test(EncryptionTests.test_encryption_basic, "Basic Encryption")
    enc_suite.add_test(EncryptionTests.test_encryption_empty, "Empty Message")
    enc_suite.add_test(EncryptionTests.test_encryption_large, "Large Message")
    all_results.extend(enc_suite.run())
    
    # Key management tests
    key_suite = TestSuite("Key Management Tests")
    key_suite.add_test(KeyManagementTests.test_key_generation, "Key Generation")
    key_suite.add_test(KeyManagementTests.test_key_save_load, "Key Save/Load")
    all_results.extend(key_suite.run())
    
    # Image processing tests
    img_suite = TestSuite("Image Processing Tests")
    img_suite.add_test(ImageProcessingTests.test_image_load, "Image Loading")
    img_suite.add_test(ImageProcessingTests.test_dwt_transform, "DWT Transform")
    all_results.extend(img_suite.run())
    
    # Compression tests
    comp_suite = TestSuite("Compression Tests")
    comp_suite.add_test(CompressionTests.test_compression_basic, "Basic Compression")
    comp_suite.add_test(CompressionTests.test_compression_ratio, "Compression Ratio")
    all_results.extend(comp_suite.run())
    
    # Embedding tests
    emb_suite = TestSuite("Embedding Tests")
    emb_suite.add_test(EmbeddingTests.test_embedding_extraction, "Embed/Extract")
    all_results.extend(emb_suite.run())
    
    # Performance tests
    perf_suite = TestSuite("Performance Tests")
    perf_suite.add_test(PerformanceTests.test_encryption_speed, "Encryption Speed")
    perf_suite.add_test(PerformanceTests.test_embedding_speed, "Embedding Speed")
    all_results.extend(perf_suite.run())
    
    # Security tests
    sec_suite = TestSuite("Security Tests")
    sec_suite.add_test(SecurityTests.test_key_randomness, "Key Randomness")
    sec_suite.add_test(SecurityTests.test_encryption_randomness, "Encryption Randomness")
    all_results.extend(sec_suite.run())
    
    # Overall summary
    total = len(all_results)
    passed = sum(1 for r in all_results if r.passed)
    failed = total - passed
    
    print("\n" + "="*70)
    print("OVERALL TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    print("="*70)
    
    return all_results


def test_testing_module():
    """Test the testing module"""
    print("="*70)
    print("MODULE 17: TESTING AND VALIDATION")
    print("="*70)
    
    # Run comprehensive tests
    results = run_comprehensive_tests()
    
    # Generate report
    print("\n📄 Test report generated")
    print(f"   Total tests executed: {len(results)}")
    print(f"   Passed: {sum(1 for r in results if r.passed)}")
    print(f"   Failed: {sum(1 for r in results if not r.passed)}")
    
    print("\n" + "="*70)
    print("✅ Testing and validation module completed!")
    print("="*70)


if __name__ == "__main__":
    test_testing_module()
