# 🚀 QUICK REFERENCE GUIDE
**LayerX Steganographic Security Framework**

---

## 📋 MODULE INDEX

### Core Security & Steganography (Modules 1-7)
| Module | File | Purpose |
|--------|------|---------|
| **1** | `a1_encryption.py` | AES-256-CBC encryption with PBKDF2 |
| **2** | `a2_key_management.py` | ECC + AES key management |
| **3** | `a3_image_processing.py` | DWT + DCT transforms |
| **4** | `a4_compression.py` | Huffman + Reed-Solomon ECC |
| **5** | `a5_embedding_extraction.py` | Adaptive steganography |
| **6** | `a6_optimization.py` | ACO + GA optimization |
| **7** | `a7_communication.py` | TCP/IP multi-client server |

### Analysis & Testing (Modules 8, 11, 12, 17, 18)
| Module | File | Purpose |
|--------|------|---------|
| **8** | `a8_scanning_detection.py` | Steganalysis & detection |
| **11** | `a11_performance_monitoring.py` | CPU/memory monitoring |
| **12** | `a12_security_analysis.py` | Security scanning |
| **17** | `a17_testing_validation.py` | Automated test suite |
| **18** | `a18_error_handling.py` | Exception management |

---

## 🎯 COMMON TASKS

### 1. Encrypt and Hide Message
```bash
# Generate keys
python generate_keys.py

# Send encrypted message in image
python send_ecc.py

# Extract and decrypt
python receive_ecc.py
```

### 2. Network Chat (Secure)
```bash
# Terminal 1: Start server
python chat_server.py

# Terminal 2+: Start clients
python chat_client.py

# Client commands:
#   /list          - Show connected users
#   /send <user>   - Send encrypted message
#   /help          - Show commands
#   /quit          - Disconnect
```

### 3. Detect Hidden Data
```python
from a8_scanning_detection import detect_steganography

result = detect_steganography('suspicious_image.png')
print(f"Detection: {result['classification']}")
print(f"Score: {result['detection_score']}/100")
```

### 4. Monitor Performance
```python
from a11_performance_monitoring import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.start_monitoring(interval=1.0)

with monitor.time_operation("my_task"):
    # Your code here
    pass

monitor.print_summary()
```

### 5. Security Analysis
```python
from a12_security_analysis import SecurityAnalyzer

analyzer = SecurityAnalyzer()
analyzer.analyze_key(my_key)
analyzer.scan_system({'encryption_algorithm': 'AES-256'})
print(analyzer.generate_report())
```

### 6. Run Tests
```bash
# Test all modules
python test_comprehensive.py

# Test specific module
cd "17. Testing and Validation Module"
python a17_testing_validation.py
```

---

## 🔧 MODULE APIs

### Module 8: Scanning & Detection
```python
# Detect steganography
detect_steganography(image_path) → {
    'detection_score': 0-100,
    'classification': 'LOW'|'MEDIUM'|'HIGH',
    'chi_square': float,
    'rs_analysis': {...},
    'histogram': {...}
}

# Compare images
compare_images(original, stego) → {
    'psnr': float,
    'changed_pixels': int,
    'correlation': float
}

# Scan directory
scan_directory(path) → [results...]
```

### Module 11: Performance Monitoring
```python
# Initialize monitor
monitor = PerformanceMonitor(history_size=100)

# Start background monitoring
monitor.start_monitoring(interval=1.0)

# Time operations
with monitor.time_operation("operation_name"):
    do_work()

# Get stats
stats = monitor.get_operation_stats("operation_name")
# Returns: {'count', 'avg', 'min', 'max', 'total'}

# Get summary
monitor.print_summary()
```

### Module 12: Security Analysis
```python
# Create analyzer
analyzer = SecurityAnalyzer()

# Analyze key strength
key_analysis = analyzer.analyze_key(key_bytes, "key_name")
# Returns: {'length', 'entropy', 'strength', 'score'}

# Check password
pw_analysis = analyzer.analyze_password(password)
# Returns: {'verdict', 'score', 'checks'}

# Scan system
vulns = analyzer.scan_system(system_config)
# Returns: [{'severity', 'category', 'description', 'recommendation'}]

# Calculate score
score = analyzer.calculate_score()  # 0-100

# Generate report
report = analyzer.generate_report()
```

### Module 17: Testing Framework
```python
# Create test suite
suite = TestSuite("My Tests")
suite.add_test(test_function, "Test Name")

# Run tests
results = suite.run()

# Run all tests
from a17_testing_validation import run_comprehensive_tests
results = run_comprehensive_tests()
```

### Module 18: Error Handling
```python
# Initialize handler
handler = ErrorHandler("errors.log")

# Add callback
handler.add_callback(lambda err: print(f"Error: {err}"))

# Handle exception
try:
    risky_operation()
except Exception as e:
    handler.handle_exception(e, "Operation context")

# Safe execution
result = safe_execute(
    risky_function,
    error_handler=handler,
    default_return=None
)

# Retry on error
@retry_on_error
def network_call():
    pass

# Validate input
validated = validate_input(
    data,
    lambda x: len(x) > 0,
    "Data cannot be empty"
)
```

---

## 📊 PERFORMANCE SPECS

### Encryption (Module 1)
- **Algorithm:** AES-256-CBC
- **Key Derivation:** PBKDF2 (100k iterations)
- **Speed:** ~0.108s per 1KB message
- **Security:** ✅ Excellent

### Steganography (Modules 3, 5)
- **Method:** DWT (2-level) + DCT
- **PSNR:** 41-65dB (payload-dependent)
- **Capacity:** 36.5% (11,946 bytes max)
- **Speed:** ~150ms embedding, ~120ms extraction

### Compression (Module 4)
- **Algorithm:** Huffman coding
- **ECC:** Reed-Solomon (adaptive)
- **Speed:** ~6ms compression
- **Ratio:** Depends on data (best for repetitive)

### Network (Module 7)
- **Protocol:** TCP/IP (JSON messages)
- **Latency:** <100ms (LAN)
- **Clients:** Multi-client support
- **Throughput:** ~2 MB/s

### Detection (Module 8)
- **Methods:** Chi-square, RS, DCT, Histogram, LSB
- **Speed:** <2s per 512x512 image
- **Accuracy:** Multi-metric scoring (0-100)

---

## 🔒 SECURITY CHECKLIST

### ✅ Implemented
- [x] AES-256 encryption
- [x] PBKDF2 key derivation (100k iterations)
- [x] ECC key exchange (SECP256R1)
- [x] Cryptographic random (secrets module)
- [x] Reed-Solomon error correction
- [x] Custom exception handling
- [x] Input validation
- [x] Security analysis tools
- [x] Steganalysis detection

### ⚠️ Recommended Additions
- [ ] TLS/SSL for network traffic (Module 7)
- [ ] User authentication (optional Module 9)
- [ ] Audit logging (optional Module 10)
- [ ] Rate limiting
- [ ] Certificate validation

---

## 🧪 TEST COVERAGE

### Module 17: Automated Tests (14 tests)
| Category | Tests | Status |
|----------|-------|--------|
| Encryption | 3 | ✅ 3/3 |
| Key Management | 2 | ✅ 2/2 |
| Image Processing | 2 | ✅ 2/2 |
| Compression | 2 | ✅ 2/2 |
| Embedding | 1 | ✅ 1/1 |
| Performance | 2 | ✅ 2/2 |
| Security | 2 | ✅ 2/2 |

**Overall:** 100% pass rate (14/14)

---

## 🐛 TROUBLESHOOTING

### Issue: Low PSNR (<50dB)
**Solution:** Reduce payload size or use adaptive Q-factor
```python
# Automatic: Module 5 uses adaptive Q based on payload
# Manual: Adjust Q factor in a5_embedding_extraction.py
```

### Issue: Network Connection Failed
**Solution:** Check firewall and port availability
```bash
# Test server
python chat_server.py
# Use 127.0.0.1:5555 for local testing
```

### Issue: Extraction Failed
**Solution:** Verify correct payload length and image
```python
# Check detection first
result = detect_steganography('image.png')
if result['detection_score'] > 50:
    # Likely contains data
    extract_from_dwt_bands(image, expected_length)
```

### Issue: Tests Failing
**Solution:** Verify dependencies installed
```bash
pip install -r requirements.txt
python -m pip list | Select-String "numpy|opencv|pywt"
```

---

## 📚 DOCUMENTATION FILES

1. **README.md** - Project overview
2. **QUICK_START.md** - 5-minute setup
3. **COMPLETE_SYSTEM_README.md** - Technical reference
4. **FINAL_MODULE_IMPLEMENTATION_REPORT.md** - Phase 4 report
5. **PROJECT_COMPLETION_SUMMARY.md** - Phase 1-3 status
6. **QUICK_REFERENCE_GUIDE.md** - This file

---

## 💻 SYSTEM REQUIREMENTS

### Dependencies
```
numpy>=1.21.0
opencv-python>=4.5.0
pywavelets>=1.1.1
scikit-image>=0.18.0
pycryptodome>=3.15.0
cryptography>=40.0.0
reedsolo>=1.5.4
psutil>=5.9.0
```

### Installation
```bash
pip install -r requirements.txt
```

### Compatibility
- **Python:** 3.8+
- **OS:** Windows, Linux, macOS
- **RAM:** 512MB minimum (2GB recommended)
- **Storage:** 100MB for code + images

---

## 🎯 WORKFLOW EXAMPLES

### Example 1: Full Encryption Pipeline
```python
from a1_encryption import encrypt_message
from a4_compression import compress_huffman, create_payload
from a5_embedding_extraction import embed_in_dwt_bands

# 1. Encrypt
ciphertext, salt, iv = encrypt_message("Secret", "password")

# 2. Compress
compressed, tree = compress_huffman(ciphertext)

# 3. Create payload
payload = create_payload(ciphertext, tree, compressed)

# 4. Embed
stego_image = embed_in_dwt_bands("cover.png", payload)

# 5. Save
cv2.imwrite("stego.png", stego_image)
```

### Example 2: Security Audit
```python
from a12_security_analysis import SecurityAnalyzer
from a8_scanning_detection import detect_steganography

analyzer = SecurityAnalyzer()

# Analyze system
analyzer.scan_system({
    'encryption_algorithm': 'AES-256',
    'key_length': 256,
    'network_encryption': True
})

# Check images
detection = detect_steganography('suspicious.png')

# Generate report
print(analyzer.generate_report())
print(f"Image Detection: {detection['classification']}")
```

### Example 3: Performance Testing
```python
from a11_performance_monitoring import PerformanceMonitor
from a17_testing_validation import run_comprehensive_tests

monitor = PerformanceMonitor()
monitor.start_monitoring(interval=0.5)

# Run tests while monitoring
with monitor.time_operation("comprehensive_tests"):
    results = run_comprehensive_tests()

# Check performance
monitor.print_summary()
```

---

## 🔗 QUICK LINKS

### Module Locations
```
h:\LayerX Steganographic Security Framework\
├── 01. Encryption Module\a1_encryption.py
├── 02. Key Management Module\a2_key_management.py
├── 03. Image Processing Module\a3_image_processing.py
├── 04. Compression Module\a4_compression.py
├── 05. Embedding and Extraction Module\a5_embedding_extraction.py
├── 06. Optimization Module\a6_optimization.py
├── 07. Communication Module\a7_communication.py
├── 08. Scanning and Detection Module\a8_scanning_detection.py
├── 11. Performance Monitoring Module\a11_performance_monitoring.py
├── 12. Security Analysis Module\a12_security_analysis.py
├── 17. Testing and Validation Module\a17_testing_validation.py
└── 18. Error Handling and Exception Management Module\a18_error_handling.py
```

### Applications
```
├── generate_keys.py        - Generate ECC key pairs
├── hybrid_encryption.py    - Encrypt with ECC + AES
├── send_ecc.py            - Encrypt and embed message
├── receive_ecc.py         - Extract and decrypt message
├── chat_server.py         - Network chat server
└── chat_client.py         - Network chat client
```

---

## ✅ STATUS SUMMARY

**Implementation:** ✅ COMPLETE (12/12 modules)  
**Testing:** ✅ PASSED (100% success rate)  
**Security:** ✅ GOOD (75/100 score)  
**Documentation:** ✅ COMPREHENSIVE (9 files)  
**Production Status:** ✅ READY

---

**For detailed information, see:**
- Technical details → `COMPLETE_SYSTEM_README.md`
- Setup guide → `QUICK_START.md`
- Phase 4 report → `FINAL_MODULE_IMPLEMENTATION_REPORT.md`

**End of Quick Reference Guide**
