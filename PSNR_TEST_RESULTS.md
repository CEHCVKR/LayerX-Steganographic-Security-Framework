"""
PSNR Test Results & Recommendations

Based on comprehensive testing with different payload sizes and Q factors:

## Test Results Summary

**Tests Run:** 25 configurations
**Success Rate:** 100% (all extractions successful)
**PSNR >=50dB:** 18/25 configurations (72%)

## Key Findings

### 1. Highest PSNR Achieved
- **Configuration:** 500B payload with Q=4.0
- **PSNR:** 65.13 dB
- **Status:** Exceeds target by 15.13 dB ✅

### 2. Maximum Capacity with PSNR >=50dB
- **Configuration:** 6000 bytes (6KB) with Q=7.0
- **PSNR:** 50.29 dB
- **Status:** Meets target ✅

### 3. Recommended Q Factors by Payload Size

| Payload Range | Min Q | Avg Q | Avg PSNR | Status |
|--------------|-------|-------|----------|--------|
| <=2KB        | 4.0   | 5.3   | 60.2 dB  | ✅ Excellent |
| 2-5KB        | 5.0   | 6.5   | 52.9 dB  | ✅ Good |
| >5KB (up to 6KB) | 7.0 | 7.0 | 50.3 dB | ✅ Target Met |

## Detailed Performance Table

| Payload | Q Factor | PSNR (dB) | Status |
|---------|----------|-----------|--------|
| 500B    | 4.0      | 65.13     | ✅ Excellent |
| 500B    | 5.0      | 63.59     | ✅ Excellent |
| 1KB     | 4.0      | 62.17     | ✅ Excellent |
| 500B    | 6.0      | 62.09     | ✅ Excellent |
| 1KB     | 5.0      | 60.65     | ✅ Excellent |
| 1KB     | 6.0      | 59.02     | ✅ Excellent |
| 2KB     | 5.0      | 57.77     | ✅ Very Good |
| 2KB     | 6.0      | 56.06     | ✅ Very Good |
| 3KB     | 5.0      | 56.04     | ✅ Very Good |
| 2KB     | 7.0      | 55.11     | ✅ Good |
| 3KB     | 6.0      | 54.29     | ✅ Good |
| 3KB     | 7.0      | 53.37     | ✅ Good |
| 4KB     | 6.0      | 53.10     | ✅ Good |
| 5KB     | 6.0      | 52.15     | ✅ Good |
| 4KB     | 7.0      | 52.12     | ✅ Good |
| 5KB     | 7.0      | 51.06     | ✅ Target |
| 4KB     | 8.0      | 50.77     | ✅ Target |
| 6KB     | 7.0      | 50.29     | ✅ Target |
| 5KB     | 8.0      | 49.84     | ⚠️ Just Below |
| 6KB     | 8.0      | 49.09     | ⚠️ Below |
| 8KB     | 7.0      | 49.00     | ⚠️ Below |
| 6KB     | 9.0      | 47.90     | ⚠️ Below |
| 8KB     | 8.0      | 47.84     | ⚠️ Below |
| 8KB     | 9.0      | 46.69     | ⚠️ Below |
| 8KB     | 10.0     | 45.70     | ⚠️ Below |

## Implementation Recommendations

### For Hybrid Encryption (typical payload ~5.5KB)
- **Recommended Q:** 6.0 or 7.0
- **Expected PSNR:** 50-52 dB
- **Status:** Meets abstract requirement (>50dB) ✅

### Adaptive Q Selection Strategy
```python
def get_optimal_q(payload_size_bytes):
    \"\"\"Select Q factor based on payload size to maintain PSNR >50dB\"\"\"
    if payload_size_bytes <= 2000:
        return 4.0  # Avg PSNR: 60.2dB
    elif payload_size_bytes <= 5000:
        return 6.0  # Avg PSNR: 52.9dB
    elif payload_size_bytes <= 6000:
        return 7.0  # Avg PSNR: 50.3dB
    else:
        return 8.0  # For >6KB, may drop below 50dB
```

## Conclusion

✅ **Abstract Compliance Achieved:**
- PSNR >50 dB: Achievable for payloads up to 6KB
- Capacity 30-50%: Achieved with 7-band embedding (36.5%)
- Hybrid AES-ECC: Implemented and working (~5.5KB payload)

✅ **Optimal Configuration for Project:**
- Small messages (<2KB): Q=4.0 → PSNR ~62dB
- Medium messages (2-5KB): Q=6.0 → PSNR ~53dB
- Large messages (5-6KB): Q=7.0 → PSNR ~51dB

**Recommendation:** Implement adaptive Q selection based on payload size to maximize PSNR while maintaining capacity.
