"""
ECC Key Pair Generator
Generates public/private key pairs for hybrid AES-ECC encryption
"""
import sys
sys.path.append('02. Key Management Module')

from a2_key_management import (
    generate_ecc_keypair,
    serialize_public_key,
    serialize_private_key
)
import os

def generate_keys(name: str, password: str = None):
    """Generate and save ECC key pair"""
    
    print("="*80)
    print("ECC KEY PAIR GENERATOR (SECP256R1)")
    print("="*80)
    
    # Generate key pair
    print(f"\n1. Generating key pair for '{name}'...")
    private_key, public_key = generate_ecc_keypair()
    print(f"   ✓ Generated SECP256R1 (P-256) key pair")
    
    # Serialize keys
    print(f"\n2. Serializing keys...")
    public_pem = serialize_public_key(public_key)
    private_pem = serialize_private_key(private_key, password)
    
    # Save keys
    pub_filename = f"{name}_public.pem"
    priv_filename = f"{name}_private.pem"
    
    with open(pub_filename, 'wb') as f:
        f.write(public_pem)
    print(f"   ✓ Saved public key: {pub_filename}")
    
    with open(priv_filename, 'wb') as f:
        f.write(private_pem)
    print(f"   ✓ Saved private key: {priv_filename}")
    if password:
        print(f"   ✓ Private key encrypted with password")
    
    print(f"\n3. Key sizes:")
    print(f"   Public key:  {len(public_pem)} bytes")
    print(f"   Private key: {len(private_pem)} bytes")
    
    print(f"\n✅ SUCCESS! Keys generated for '{name}'")
    print(f"\n📋 Usage:")
    print(f"   Send:    python send_ecc.py cover.png stego.png 'message' {pub_filename}")
    print(f"   Receive: python receive_ecc.py stego.png {priv_filename} <salt> <iv>")
    print("="*80)
    
    return pub_filename, priv_filename


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_keys.py <name> [password]")
        print("\nExample:")
        print("  python generate_keys.py alice")
        print("  python generate_keys.py bob mypassword")
        sys.exit(1)
    
    name = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else None
    
    generate_keys(name, password)
