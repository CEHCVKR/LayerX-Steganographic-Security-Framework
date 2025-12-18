"""
Comprehensive Test Suite for send.py & receive.py
Tests various scenarios and edge cases
"""
import subprocess
import os
import sys

def run_command(cmd):
    """Run command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def extract_salt_iv(output):
    """Extract salt and IV from sender output"""
    lines = output.split('\n')
    salt = None
    iv = None
    for line in lines:
        if 'Salt:' in line:
            salt = line.split('Salt:')[1].strip()
        if 'IV:' in line:
            iv = line.split('IV:')[1].strip()
    return salt, iv

def test_case(name, message, password, cover='test_lena.png'):
    """Run a complete send/receive test"""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}")
    print(f"Message: '{message}' ({len(message)} chars)")
    print(f"Password: '{password}'")
    
    stego = f"test_{name.replace(' ', '_')}.png"
    
    # Send
    send_cmd = f'python send.py {cover} {stego} "{message}" {password}'
    code, out, err = run_command(send_cmd)
    
    if code != 0:
        print(f"❌ SEND FAILED")
        print(f"Error: {err}")
        return False
    
    print(f"✓ Send successful")
    
    # Extract salt/IV
    salt, iv = extract_salt_iv(out)
    if not salt or not iv:
        print(f"❌ Could not extract salt/IV")
        return False
    
    # Receive
    recv_cmd = f'python receive.py {stego} {password} {salt} {iv}'
    code, out, err = run_command(recv_cmd)
    
    if code != 0:
        print(f"❌ RECEIVE FAILED")
        print(f"Error: {err}")
        return False
    
    # Check if message matches
    if message in out:
        print(f"✓ Receive successful")
        print(f"✅ PASSED - Message: '{message}'")
        return True
    else:
        print(f"❌ FAILED - Message mismatch")
        print(f"Expected: '{message}'")
        print(f"Got: {out}")
        return False

# Run test suite
print("="*80)
print("COMPREHENSIVE TEST SUITE - send.py & receive.py")
print("="*80)

results = {}

# Test 1: Simple short message
results['Simple'] = test_case(
    "Simple",
    "Hello World!",
    "password123"
)

# Test 2: Single character
results['Single_char'] = test_case(
    "Single_char",
    "X",
    "pass"
)

# Test 3: Empty-like (space)
results['Space'] = test_case(
    "Space",
    " ",
    "test"
)

# Test 4: Numbers only
results['Numbers'] = test_case(
    "Numbers",
    "1234567890",
    "numeric"
)

# Test 5: Special characters
results['Special'] = test_case(
    "Special",
    "!@#$%^&*()_+-=[]{}|;:,.<>?",
    "special123"
)

# Test 6: Multi-word sentence
results['Sentence'] = test_case(
    "Sentence",
    "The quick brown fox jumps over the lazy dog",
    "longpass"
)

# Test 7: With quotes
results['Quotes'] = test_case(
    "Quotes",
    'She said "Hello"',
    "quoted"
)

# Test 8: Long password
results['Long_pass'] = test_case(
    "Long_pass",
    "Secret message",
    "ThisIsAVeryLongPasswordWith123Numbers!@#"
)

# Test 9: Unicode (if supported)
results['Unicode'] = test_case(
    "Unicode",
    "Hello 世界 🌍",
    "unicode"
)

# Test 10: Multi-line (newline)
results['Multiline'] = test_case(
    "Multiline",
    "Line1\nLine2\nLine3",
    "multipass"
)

# Test 11: Medium length message
results['Medium'] = test_case(
    "Medium",
    "This is a medium length message to test capacity handling.",
    "medium"
)

# Test 12: JSON-like structure
results['JSON'] = test_case(
    "JSON",
    '{"key": "value", "num": 123}',
    "jsonpass"
)

# Test 13: Same password different messages
results['Same_pass1'] = test_case(
    "Same_pass1",
    "Message A",
    "samepass"
)
results['Same_pass2'] = test_case(
    "Same_pass2",
    "Message B",
    "samepass"
)

# Test 14: Same message different passwords
results['Diff_pass1'] = test_case(
    "Diff_pass1",
    "Same message",
    "password1"
)
results['Diff_pass2'] = test_case(
    "Diff_pass2",
    "Same message",
    "password2"
)

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)

passed = sum(1 for v in results.values() if v)
total = len(results)
rate = (passed / total * 100) if total > 0 else 0

print(f"\nTotal Tests: {total}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {total - passed}")
print(f"Success Rate: {rate:.1f}%")

print("\nDetailed Results:")
for test, result in results.items():
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"  {status} - {test}")

print("\n" + "="*80)
if rate == 100:
    print("🎉 ALL TESTS PASSED!")
elif rate >= 80:
    print("⚠️  MOST TESTS PASSED")
else:
    print("❌ MULTIPLE FAILURES - NEEDS ATTENTION")
print("="*80)
