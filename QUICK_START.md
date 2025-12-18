# Quick Start Guide - Secure Steganographic Chat

## 🚀 5-Minute Setup

### Prerequisites
```bash
pip install numpy opencv-python pywt scikit-image pycryptodome cryptography reedsolo
```

---

## Scenario 1: Simple Encrypted Message (No Network)

**Step 1: Generate keys for both parties**
```bash
python generate_keys.py alice
python generate_keys.py bob
```

**Step 2: Alice sends encrypted message to Bob**
```bash
python send_ecc.py test_lena.png secret.png "Hello Bob!" bob_public.pem
```
Output shows Salt and IV - **save these!**

**Step 3: Bob decrypts the message**
```bash
python receive_ecc.py secret.png bob_private.pem <salt> <iv>
```

✅ **Done!** Bob sees "Hello Bob!"

---

## Scenario 2: LAN Chat Application

### Terminal 1: Start Server (192.168.1.100)
```bash
python chat_server.py
```
- Server IP: `0.0.0.0`
- Port: `5555` (or custom)

**Server starts and waits for connections...**

### Terminal 2: Alice Joins (any machine in LAN)
```bash
python chat_client.py
```
- Username: `alice`
- Server IP: `192.168.1.100`
- Port: `5555`

**Alice sees: "Connected successfully!"**

### Terminal 3: Bob Joins (any machine in LAN)
```bash
python chat_client.py
```
- Username: `bob`
- Server IP: `192.168.1.100`
- Port: `5555`

**Both see: "bob joined the chat"**

### Terminal 2: Alice Creates Encrypted Message
```bash
# Outside chat, create stego image first
python send_ecc.py test_lena.png msg_for_bob.png "Secret plan at 3pm" bob_public.pem

# Note the Salt and IV shown
# Salt: abc123def456...
# IV: 789ghi012jkl...
```

### Terminal 2: Alice Sends in Chat
```
> /send
Recipient: bob
Stego image path: msg_for_bob.png
Salt: abc123def456...
IV: 789ghi012jkl...
```

**Server shows:** "alice → bob: Message sent"

### Terminal 3: Bob Receives and Decrypts
**Bob sees notification:** "Message from alice"

```bash
# Bob saves the image (transmitted through network)
# Then decrypts outside chat:

python receive_ecc.py received_image.png bob_private.pem abc123def456... 789ghi012jkl...
```

**Bob sees:** "Secret plan at 3pm" ✅

---

## Chat Commands

| Command | Description |
|---------|-------------|
| `/list` | Show online users |
| `/send` | Send encrypted message (need stego image) |
| `/help` | Show help |
| `/quit` | Exit chat |

---

## Complete Workflow Example

### Setup Phase (Once per user)
```bash
# Generate your keys
python generate_keys.py alice
# Creates: alice_private.pem (secret), alice_public.pem (share)

# Share your public key with others
# Copy bob_public.pem from Bob
```

### Communication Phase (Repeatable)

**1. Create Encrypted Stego Image:**
```bash
python send_ecc.py cover.png stego.png "Your message here" bob_public.pem
# Save the Salt and IV shown
```

**2. Send through Network:**
- Option A: Use chat application (`/send` command)
- Option B: Email, USB, cloud storage (image looks normal!)

**3. Recipient Decrypts:**
```bash
python receive_ecc.py stego.png bob_private.pem <salt> <iv>
# Message appears on screen
```

---

## Performance Summary

| Payload Size | PSNR | Embedding Time | Status |
|--------------|------|----------------|--------|
| <1 KB | 60-65 dB | ~130 ms | ✅ Excellent |
| 1-3 KB | 56-58 dB | ~150 ms | ✅ Very Good |
| 3-5 KB | 52-54 dB | ~180 ms | ✅ Good |
| 5KB+ (encrypted) | 41-50 dB | ~200 ms | ✅ Target |

**Capacity:** 11,946 bytes maximum (36.5% of image)  
**Extraction Success:** 100%  
**Security:** AES-256 + ECC (SECP256R1)

---

## Troubleshooting

### "Connection refused"
- Check server is running
- Verify IP address (use `ipconfig` on Windows, `ifconfig` on Linux)
- Check firewall allows port 5555

### "Username already taken"
- Choose different username
- Wait for previous user to disconnect

### "File not found"
- Use absolute paths or navigate to correct directory
- Check file name spelling

### "Extraction failed"
- Verify Salt and IV are exact copies (no spaces)
- Ensure correct private key used
- Check image wasn't compressed/modified during transfer

### Low PSNR
- Normal for large payloads (5KB+)
- Still excellent visual quality
- 41-42 dB is imperceptible to human eye

---

## Tips & Best Practices

✅ **Always use fresh keys** for different recipients  
✅ **Keep private keys secure** (never share!)  
✅ **Save Salt/IV** - needed for decryption  
✅ **Use uncompressed images** (PNG not JPG)  
✅ **Test locally first** before remote use  
✅ **Backup your keys** in secure location  

---

## System Architecture

```
Message → AES-256 (session key) → Encrypted
                ↓
        Session Key → ECC → Encrypted Key (125 bytes)
                ↓
        Combined → Huffman → Compressed
                ↓
        Bits → DWT-DCT → Stego Image (PSNR ~50dB)
                ↓
        Network → TCP/IP → Recipient
                ↓
        Extract → Decompress → Decrypt → Message ✅
```

---

## Need Help?

Check documentation:
- [COMPLETE_SYSTEM_README.md](COMPLETE_SYSTEM_README.md) - Full system docs
- [PSNR_TEST_RESULTS.md](PSNR_TEST_RESULTS.md) - Performance analysis
- [PSNR_IMPROVEMENT_RESULTS.md](PSNR_IMPROVEMENT_RESULTS.md) - Optimization results

Run tests:
```bash
python test_ecc_compliance.py      # Verify all features working
python test_performance.py          # Check PSNR and capacity
python test_adaptive_q.py          # Test Q factor optimization
```

---

## Ready to Use! 🎉

Your secure steganographic communication system is **production-ready**:
- ✅ All core modules implemented
- ✅ Network layer working
- ✅ Performance targets met
- ✅ Security fully implemented
- ✅ Chat application functional

Start with **Scenario 1** for simple testing, then move to **Scenario 2** for full LAN chat!
