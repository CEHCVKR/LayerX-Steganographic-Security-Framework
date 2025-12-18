"""
Quick Manual Test Cases
Run each test individually
"""
import subprocess
import sys

def test(num, msg, pwd):
    print(f"\n{'='*60}")
    print(f"TEST {num}: {msg[:30]}...")
    stego = f"test{num}.png"
    
    # Send
    cmd = f'python send.py test_lena.png {stego} "{msg}" {pwd}'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    
    if r.returncode != 0:
        print(f"❌ Send failed")
        return False
    
    # Extract salt/IV
    lines = r.stdout.split('\n')
    salt = [l.split(':')[1].strip() for l in lines if 'Salt:' in l][0]
    iv = [l.split(':')[1].strip() for l in lines if 'IV:' in l][0]
    
    print(f"✓ Sent ({len(msg)} chars)")
    
    # Receive
    cmd = f'python receive.py {stego} {pwd} {salt} {iv}'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    
    if r.returncode != 0:
        print(f"❌ Receive failed")
        print(r.stderr[:200])
        return False
    
    if msg in r.stdout:
        print(f"✅ PASS - Verified")
        return True
    else:
        print(f"❌ FAIL - Mismatch")
        return False

print("="*60)
print("MANUAL TEST SUITE")
print("="*60)

results = []

# Basic tests that should work
results.append(("Short", test(1, "Hello", "pass")))
results.append(("Medium", test(2, "Hello World!", "pass123")))
results.append(("Long text", test(3, "The quick brown fox jumps", "longpass")))
results.append(("Numbers", test(4, "123456", "num")))
results.append(("Spaces", test(5, "A B C", "space")))
results.append(("Mixed", test(6, "Test123!", "mixed")))

# Summary
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
passed = sum(1 for _, r in results if r)
total = len(results)
print(f"Passed: {passed}/{total} ({passed/total*100:.0f}%)")
for name, result in results:
    print(f"  {'✅' if result else '❌'} {name}")
