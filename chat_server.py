"""
Secure Chat Server
Runs the communication server for LAN-based steganographic chat
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '07. Communication Module'))

from a7_communication import CommunicationServer
import signal

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nShutting down...")
    if server:
        server.stop()
    sys.exit(0)

if __name__ == "__main__":
    print("="*70)
    print("SECURE STEGANOGRAPHIC CHAT SERVER")
    print("="*70)
    print("\nAES-ECC Hybrid Encryption + DWT-DCT Steganography")
    print("Press Ctrl+C to stop\n")
    
    # Get configuration
    host = input("Server IP (default: 0.0.0.0 for all interfaces): ").strip()
    if not host:
        host = '0.0.0.0'
    
    port_input = input("Port (default: 5555): ").strip()
    port = int(port_input) if port_input else 5555
    
    # Create and start server
    server = CommunicationServer(host=host, port=port)
    
    # Setup callbacks
    def on_client_connected(username, address):
        print(f"📥 {username} joined from {address[0]}")
    
    def on_client_disconnected(username):
        print(f"📤 {username} left")
    
    def on_message_received(sender, recipient, data):
        if recipient == 'broadcast':
            print(f"💬 {sender} → ALL: Message sent")
        else:
            print(f"💬 {sender} → {recipient}: Message sent")
    
    server.on_client_connected = on_client_connected
    server.on_client_disconnected = on_client_disconnected
    server.on_message_received = on_message_received
    
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start server
    if server.start():
        print("\n✅ Server is running!")
        print(f"   Clients can connect to: {host}:{port}")
        print("\n" + "="*70)
        
        # Keep running
        try:
            while True:
                pass
        except KeyboardInterrupt:
            pass
    else:
        print("\n❌ Failed to start server")
        sys.exit(1)
