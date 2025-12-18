"""
Module 7: Network Communication Layer
Author: Member A
Description: TCP/IP socket communication for secure LAN-based steganographic chat
Dependencies: socket, threading, json, queue

Features:
- Server/Client architecture
- Multi-client support
- Automatic image exchange
- Message broadcasting
- Connection management
- Thread-safe operations
"""

import socket
import threading
import json
import time
import os
import sys
from typing import Dict, List, Callable, Optional
from queue import Queue, Empty
from datetime import datetime

# Import previous modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CommunicationServer:
    """
    Server for handling multiple client connections in LAN
    Manages message routing and client registry
    """
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5555):
        """
        Initialize communication server
        
        Args:
            host: Server IP address (0.0.0.0 for all interfaces)
            port: Server port number
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients: Dict[str, socket.socket] = {}  # username -> socket
        self.client_info: Dict[str, dict] = {}  # username -> {address, public_key}
        self.running = False
        self.lock = threading.Lock()
        
        # Callbacks for events
        self.on_client_connected: Optional[Callable] = None
        self.on_client_disconnected: Optional[Callable] = None
        self.on_message_received: Optional[Callable] = None
        
    def start(self):
        """Start the server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"✓ Server started on {self.host}:{self.port}")
            print(f"  Waiting for connections...")
            
            # Start accepting connections in separate thread
            accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            accept_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start server: {str(e)}")
            return False
    
    def _accept_connections(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"⚠️  Error accepting connection: {str(e)}")
    
    def _handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle individual client connection"""
        username = None
        
        try:
            # Receive initial handshake with username and public key
            data = self._receive_data(client_socket)
            if not data or data.get('type') != 'handshake':
                client_socket.close()
                return
            
            username = data.get('username')
            public_key = data.get('public_key')
            
            # Check if username already exists
            with self.lock:
                if username in self.clients:
                    self._send_data(client_socket, {
                        'type': 'error',
                        'message': 'Username already taken'
                    })
                    client_socket.close()
                    return
                
                # Register client
                self.clients[username] = client_socket
                self.client_info[username] = {
                    'address': address,
                    'public_key': public_key,
                    'connected_at': datetime.now().isoformat()
                }
            
            # Send success response with client list
            self._send_data(client_socket, {
                'type': 'handshake_ok',
                'message': f'Welcome {username}!',
                'clients': self._get_client_list()
            })
            
            print(f"✓ {username} connected from {address[0]}:{address[1]}")
            
            # Notify other clients
            self._broadcast({
                'type': 'client_joined',
                'username': username,
                'public_key': public_key
            }, exclude=username)
            
            # Callback
            if self.on_client_connected:
                self.on_client_connected(username, address)
            
            # Handle messages from this client
            while self.running:
                data = self._receive_data(client_socket)
                if not data:
                    break
                
                # Process message
                self._process_message(username, data)
            
        except Exception as e:
            print(f"⚠️  Error handling client {username}: {str(e)}")
        
        finally:
            # Clean up
            if username:
                with self.lock:
                    if username in self.clients:
                        del self.clients[username]
                    if username in self.client_info:
                        del self.client_info[username]
                
                print(f"✗ {username} disconnected")
                
                # Notify other clients
                self._broadcast({
                    'type': 'client_left',
                    'username': username
                })
                
                # Callback
                if self.on_client_disconnected:
                    self.on_client_disconnected(username)
            
            try:
                client_socket.close()
            except:
                pass
    
    def _process_message(self, sender: str, data: dict):
        """Process message from client"""
        msg_type = data.get('type')
        
        if msg_type == 'message':
            # Forward message to recipient
            recipient = data.get('recipient')
            
            # Add sender info
            data['sender'] = sender
            data['timestamp'] = datetime.now().isoformat()
            
            if recipient == 'broadcast':
                # Broadcast to all except sender
                self._broadcast(data, exclude=sender)
            elif recipient in self.clients:
                # Send to specific recipient
                self._send_to_client(recipient, data)
            else:
                # Recipient not found
                self._send_to_client(sender, {
                    'type': 'error',
                    'message': f'Recipient {recipient} not found'
                })
            
            # Callback
            if self.on_message_received:
                self.on_message_received(sender, recipient, data)
        
        elif msg_type == 'get_clients':
            # Send updated client list
            self._send_to_client(sender, {
                'type': 'client_list',
                'clients': self._get_client_list()
            })
        
        elif msg_type == 'request_public_key':
            # Send public key of requested user
            target = data.get('username')
            if target in self.client_info:
                self._send_to_client(sender, {
                    'type': 'public_key',
                    'username': target,
                    'public_key': self.client_info[target]['public_key']
                })
    
    def _broadcast(self, data: dict, exclude: Optional[str] = None):
        """Broadcast message to all clients"""
        with self.lock:
            for username, client_socket in self.clients.items():
                if username != exclude:
                    self._send_data(client_socket, data)
    
    def _send_to_client(self, username: str, data: dict):
        """Send data to specific client"""
        with self.lock:
            if username in self.clients:
                self._send_data(self.clients[username], data)
    
    def _get_client_list(self) -> List[dict]:
        """Get list of connected clients"""
        with self.lock:
            return [
                {
                    'username': username,
                    'public_key': info['public_key'],
                    'address': info['address'][0]
                }
                for username, info in self.client_info.items()
            ]
    
    def _send_data(self, sock: socket.socket, data: dict):
        """Send JSON data over socket"""
        try:
            json_data = json.dumps(data)
            message = json_data.encode('utf-8')
            
            # Send length first (4 bytes)
            length = len(message).to_bytes(4, byteorder='big')
            sock.sendall(length + message)
            
        except Exception as e:
            print(f"⚠️  Error sending data: {str(e)}")
    
    def _receive_data(self, sock: socket.socket) -> Optional[dict]:
        """Receive JSON data from socket"""
        try:
            # Receive length first (4 bytes)
            length_data = sock.recv(4)
            if not length_data:
                return None
            
            message_length = int.from_bytes(length_data, byteorder='big')
            
            # Receive message
            chunks = []
            received = 0
            while received < message_length:
                chunk = sock.recv(min(message_length - received, 4096))
                if not chunk:
                    return None
                chunks.append(chunk)
                received += len(chunk)
            
            message = b''.join(chunks)
            return json.loads(message.decode('utf-8'))
            
        except Exception as e:
            print(f"⚠️  Error receiving data: {str(e)}")
            return None
    
    def stop(self):
        """Stop the server"""
        print("\n⚠️  Shutting down server...")
        self.running = False
        
        # Close all client connections
        with self.lock:
            for username, client_socket in self.clients.items():
                try:
                    client_socket.close()
                except:
                    pass
            self.clients.clear()
            self.client_info.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("✓ Server stopped")


class CommunicationClient:
    """
    Client for connecting to communication server
    Handles sending and receiving encrypted steganographic messages
    """
    
    def __init__(self, username: str, public_key_pem: str):
        """
        Initialize communication client
        
        Args:
            username: Client username
            public_key_pem: Client's ECC public key (PEM format)
        """
        self.username = username
        self.public_key_pem = public_key_pem
        self.socket = None
        self.connected = False
        self.running = False
        
        # Message queues
        self.incoming_messages = Queue()
        
        # Callbacks
        self.on_message_received: Optional[Callable] = None
        self.on_client_joined: Optional[Callable] = None
        self.on_client_left: Optional[Callable] = None
        self.on_disconnected: Optional[Callable] = None
        
        # Client list
        self.clients: Dict[str, dict] = {}
    
    def connect(self, host: str, port: int = 5555) -> bool:
        """
        Connect to server
        
        Args:
            host: Server IP address
            port: Server port
            
        Returns:
            bool: True if connected successfully
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            
            # Send handshake
            self._send_data({
                'type': 'handshake',
                'username': self.username,
                'public_key': self.public_key_pem
            })
            
            # Wait for response
            response = self._receive_data()
            if not response or response.get('type') != 'handshake_ok':
                error_msg = response.get('message', 'Connection failed') if response else 'No response'
                print(f"❌ Connection failed: {error_msg}")
                self.socket.close()
                return False
            
            self.connected = True
            self.running = True
            
            # Update client list
            self.clients = {
                client['username']: client
                for client in response.get('clients', [])
            }
            
            print(f"✓ Connected to {host}:{port} as {self.username}")
            print(f"  Online users: {', '.join(self.clients.keys())}")
            
            # Start receiving thread
            receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            receive_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return False
    
    def _receive_loop(self):
        """Continuously receive messages from server"""
        while self.running and self.connected:
            try:
                data = self._receive_data()
                if not data:
                    break
                
                # Process received data
                self._process_received_data(data)
                
            except Exception as e:
                if self.running:
                    print(f"⚠️  Error receiving: {str(e)}")
                break
        
        # Disconnected
        self.connected = False
        if self.on_disconnected:
            self.on_disconnected()
    
    def _process_received_data(self, data: dict):
        """Process data received from server"""
        msg_type = data.get('type')
        
        if msg_type == 'message':
            # Incoming message
            sender = data.get('sender')
            self.incoming_messages.put(data)
            
            if self.on_message_received:
                self.on_message_received(sender, data)
        
        elif msg_type == 'client_joined':
            # New client joined
            username = data.get('username')
            public_key = data.get('public_key')
            
            self.clients[username] = {
                'username': username,
                'public_key': public_key
            }
            
            print(f"\n✓ {username} joined the chat")
            
            if self.on_client_joined:
                self.on_client_joined(username, public_key)
        
        elif msg_type == 'client_left':
            # Client left
            username = data.get('username')
            
            if username in self.clients:
                del self.clients[username]
            
            print(f"\n✗ {username} left the chat")
            
            if self.on_client_left:
                self.on_client_left(username)
        
        elif msg_type == 'client_list':
            # Updated client list
            self.clients = {
                client['username']: client
                for client in data.get('clients', [])
            }
        
        elif msg_type == 'error':
            print(f"\n❌ Error: {data.get('message')}")
    
    def send_message(self, recipient: str, image_path: str, metadata: dict = None):
        """
        Send steganographic message
        
        Args:
            recipient: Recipient username ('broadcast' for all)
            image_path: Path to stego image file
            metadata: Additional metadata (salt, iv, etc.)
        """
        if not self.connected:
            print("❌ Not connected to server")
            return False
        
        try:
            # Read image file
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Send message
            self._send_data({
                'type': 'message',
                'recipient': recipient,
                'image_size': len(image_data),
                'metadata': metadata or {}
            })
            
            # Send image data in chunks
            self._send_image_data(image_data)
            
            return True
            
        except Exception as e:
            print(f"❌ Error sending message: {str(e)}")
            return False
    
    def get_message(self, timeout: float = None) -> Optional[dict]:
        """
        Get next incoming message from queue
        
        Args:
            timeout: Maximum time to wait (None = non-blocking)
            
        Returns:
            Message dict or None
        """
        try:
            return self.incoming_messages.get(timeout=timeout)
        except Empty:
            return None
    
    def get_clients(self) -> Dict[str, dict]:
        """Get list of connected clients"""
        return self.clients.copy()
    
    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        print("✓ Disconnected")
    
    def _send_data(self, data: dict):
        """Send JSON data over socket"""
        try:
            json_data = json.dumps(data)
            message = json_data.encode('utf-8')
            
            length = len(message).to_bytes(4, byteorder='big')
            self.socket.sendall(length + message)
            
        except Exception as e:
            print(f"⚠️  Error sending data: {str(e)}")
            raise
    
    def _send_image_data(self, image_data: bytes):
        """Send image data in chunks"""
        chunk_size = 4096
        for i in range(0, len(image_data), chunk_size):
            chunk = image_data[i:i + chunk_size]
            self.socket.sendall(chunk)
    
    def _receive_data(self) -> Optional[dict]:
        """Receive JSON data from socket"""
        try:
            length_data = self.socket.recv(4)
            if not length_data:
                return None
            
            message_length = int.from_bytes(length_data, byteorder='big')
            
            chunks = []
            received = 0
            while received < message_length:
                chunk = self.socket.recv(min(message_length - received, 4096))
                if not chunk:
                    return None
                chunks.append(chunk)
                received += len(chunk)
            
            message = b''.join(chunks)
            return json.loads(message.decode('utf-8'))
            
        except Exception as e:
            if self.running:
                print(f"⚠️  Error receiving data: {str(e)}")
            return None


def test_communication_module():
    """Test the communication module"""
    print("="*70)
    print("MODULE 7: COMMUNICATION LAYER TEST")
    print("="*70)
    
    # Test server
    print("\n1. Testing Server...")
    server = CommunicationServer(host='127.0.0.1', port=5555)
    if server.start():
        print("   ✓ Server started successfully")
        
        # Wait a bit
        time.sleep(1)
        
        # Test client
        print("\n2. Testing Client...")
        client = CommunicationClient('TestUser', 'test_public_key_pem')
        if client.connect('127.0.0.1', 5555):
            print("   ✓ Client connected successfully")
            
            time.sleep(1)
            
            # Disconnect
            client.disconnect()
            print("   ✓ Client disconnected")
        
        # Stop server
        server.stop()
        print("   ✓ Server stopped")
    
    print("\n" + "="*70)
    print("✅ Communication module test completed!")
    print("="*70)


if __name__ == "__main__":
    test_communication_module()
