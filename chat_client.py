"""
Secure Chat Client
Interactive chat client with hybrid AES-ECC encryption and steganography
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '02. Key Management Module'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '07. Communication Module'))

from a7_communication import CommunicationClient
from a2_key_management import generate_ecc_keypair, serialize_public_key
import threading
import time

class SecureChatClient:
    """Interactive secure chat client"""
    
    def __init__(self, username, private_key, public_key_pem):
        self.username = username
        self.private_key = private_key
        self.public_key_pem = public_key_pem
        self.client = CommunicationClient(username, public_key_pem)
        self.running = False
        
    def connect(self, host, port=5555):
        """Connect to server"""
        if self.client.connect(host, port):
            self.running = True
            
            # Setup callbacks
            self.client.on_message_received = self.on_message
            self.client.on_client_joined = self.on_client_joined
            self.client.on_client_left = self.on_client_left
            self.client.on_disconnected = self.on_disconnected
            
            return True
        return False
    
    def on_message(self, sender, data):
        """Handle incoming message"""
        print(f"\n💬 Message from {sender}:")
        print(f"   Metadata: {data.get('metadata', {})}")
        print(f"   [Image received - use receive_ecc.py to decrypt]")
        print("> ", end='', flush=True)
    
    def on_client_joined(self, username, public_key):
        """Handle client joined"""
        print(f"\n✓ {username} joined the chat")
        print("> ", end='', flush=True)
    
    def on_client_left(self, username):
        """Handle client left"""
        print(f"\n✗ {username} left the chat")
        print("> ", end='', flush=True)
    
    def on_disconnected(self):
        """Handle disconnection"""
        print("\n❌ Disconnected from server")
        self.running = False
    
    def run(self):
        """Run interactive chat"""
        print("\n" + "="*70)
        print("SECURE CHAT - COMMANDS")
        print("="*70)
        print("/list       - Show online users")
        print("/send       - Send encrypted message")
        print("/help       - Show this help")
        print("/quit       - Exit chat")
        print("="*70)
        
        try:
            while self.running:
                try:
                    command = input("\n> ").strip()
                    
                    if not command:
                        continue
                    
                    if command == '/quit':
                        break
                    elif command == '/list':
                        self.show_users()
                    elif command == '/send':
                        self.send_message()
                    elif command == '/help':
                        self.show_help()
                    else:
                        print("Unknown command. Type /help for commands.")
                
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
        
        finally:
            self.client.disconnect()
            print("\n✓ Goodbye!")
    
    def show_users(self):
        """Show online users"""
        clients = self.client.get_clients()
        print(f"\n📋 Online Users ({len(clients)}):")
        for username in clients.keys():
            print(f"   - {username}")
    
    def send_message(self):
        """Send encrypted message"""
        print("\n📤 Send Encrypted Message")
        print("   Note: Use send_ecc.py to create encrypted stego image first")
        print("   Then provide the path to send it")
        
        recipient = input("   Recipient (username or 'broadcast'): ").strip()
        if not recipient:
            return
        
        image_path = input("   Stego image path: ").strip()
        if not os.path.exists(image_path):
            print(f"   ❌ File not found: {image_path}")
            return
        
        # Get metadata (salt, iv)
        salt = input("   Salt (hex): ").strip()
        iv = input("   IV (hex): ").strip()
        
        metadata = {
            'salt': salt,
            'iv': iv,
            'encryption': 'AES-ECC-Hybrid'
        }
        
        # Send message
        if self.client.send_message(recipient, image_path, metadata):
            print("   ✅ Message sent!")
        else:
            print("   ❌ Failed to send")
    
    def show_help(self):
        """Show help"""
        print("\n" + "="*70)
        print("COMMAND HELP")
        print("="*70)
        print("/list   - Show all online users")
        print("/send   - Send encrypted steganographic message")
        print("         (requires pre-encrypted stego image)")
        print("/help   - Show this help message")
        print("/quit   - Exit the chat application")
        print("\nWorkflow:")
        print("1. Use 'python send_ecc.py' to create encrypted stego image")
        print("2. Use '/send' to transmit the image through chat")
        print("3. Recipient uses 'python receive_ecc.py' to decrypt")
        print("="*70)


def main():
    print("="*70)
    print("SECURE STEGANOGRAPHIC CHAT CLIENT")
    print("="*70)
    print("\nAES-ECC Hybrid Encryption + DWT-DCT Steganography\n")
    
    # Get username
    username = input("Enter your username: ").strip()
    if not username:
        print("❌ Username required")
        return
    
    # Load or generate keys
    private_key_file = f"{username}_private.pem"
    public_key_file = f"{username}_public.pem"
    
    if os.path.exists(private_key_file) and os.path.exists(public_key_file):
        print(f"✓ Found existing keys: {private_key_file}")
        
        # Load keys
        with open(public_key_file, 'r') as f:
            public_key_pem = f.read()
        
        # For simplicity, we don't load private key here
        # User will need it separately for decryption
        private_key = None
        
    else:
        print("⚠️  No keys found. Generating new ECC keypair...")
        private_key, public_key = generate_ecc_keypair()
        public_key_pem = serialize_public_key(public_key)
        
        # Save keys
        from a2_key_management import serialize_private_key
        private_pem = serialize_private_key(private_key)
        
        with open(private_key_file, 'w') as f:
            f.write(private_pem)
        with open(public_key_file, 'w') as f:
            f.write(public_key_pem)
        
        print(f"✓ Keys saved: {private_key_file}, {public_key_file}")
    
    # Get server info
    host = input("\nServer IP address: ").strip()
    if not host:
        print("❌ Server IP required")
        return
    
    port_input = input("Server port (default: 5555): ").strip()
    port = int(port_input) if port_input else 5555
    
    # Create and connect client
    client = SecureChatClient(username, private_key, public_key_pem)
    
    if client.connect(host, port):
        print("\n✅ Connected successfully!")
        client.run()
    else:
        print("\n❌ Failed to connect to server")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
