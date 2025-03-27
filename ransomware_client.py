#!/usr/bin/env python3
"""
Ransomware Client - Educational Edition

This is a CLI-based client for interacting with a simulated ransomware operation
for cybersecurity education purposes.

DISCLAIMER: This tool is for EDUCATIONAL PURPOSES ONLY.
Using this code for malicious purposes is ILLEGAL and UNETHICAL.
"""

import os
import sys
import time
import json
import base64
import logging
import argparse
import requests
import datetime
import socket
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ransomware_client.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RansomwareClient")

class RansomwareClient:
    """Educational client for the ransomware simulation."""

    def __init__(self, server_address=None):
        """Initialize the client with optional server address."""
        self.server_address = server_address
        self.client_id = self._generate_client_id()
        self.encryption_key = None
        self.encrypted_files = []
        self.simulation_active = False
        self.config = self._load_config()

    def _generate_client_id(self):
        """Generate a unique client ID based on machine info."""
        hostname = socket.gethostname()
        machine_id = f"{hostname}-{int(time.time())}"
        return base64.urlsafe_b64encode(machine_id.encode()).decode()[:12]

    def _load_config(self):
        """Load configuration from file or create default."""
        default_config = {
            "version": "1.0.0",
            "client_id": self.client_id,
            "simulation_active": False,
            "last_check_in": None,
            "encryption_details": None,
            "educational_mode": True  # Always keep as True
        }
        
        config_file = "ransomware_client_config.json"
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Ensure educational_mode is always True for safety
                    config["educational_mode"] = True
                    return config
            else:
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return default_config

    def _save_config(self):
        """Save current configuration to file."""
        try:
            # Always ensure educational_mode is True for safety
            self.config["educational_mode"] = True
            self.config["client_id"] = self.client_id
            self.config["simulation_active"] = self.simulation_active
            self.config["last_check_in"] = datetime.datetime.now().isoformat()
            
            with open("ransomware_client_config.json", 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")

    def check_status(self):
        """Check the status of the encryption and any commands from server."""
        if not self.server_address:
            print("No server configured. Running in standalone mode.")
            return None
            
        try:
            # This is a simulation - in reality, this would connect to a C2 server
            # For educational purposes, we're just pretending this happens
            print("Checking server status... (SIMULATION)")
            print(f"Client ID: {self.client_id}")
            
            # Simulate server response
            simulated_response = {
                "status": "active" if self.simulation_active else "inactive",
                "message": "System is operating normally",
                "command": None,
                "client_id": self.client_id,
                "last_check_in": datetime.datetime.now().isoformat()
            }
            
            # If active simulation, add auto-decrypt schedule
            if self.simulation_active and self.config.get("encryption_details"):
                encryption_time = datetime.datetime.fromisoformat(
                    self.config["encryption_details"]["timestamp"]
                )
                auto_decrypt_time = encryption_time + datetime.timedelta(hours=24)
                
                simulated_response["auto_decrypt_scheduled"] = auto_decrypt_time.isoformat()
                
                # Check if auto-decrypt time has passed
                if datetime.datetime.now() > auto_decrypt_time:
                    simulated_response["command"] = "decrypt"
                    simulated_response["message"] = "Auto-decrypt timer triggered"
            
            return simulated_response
            
        except Exception as e:
            logger.error(f"Error checking server status: {str(e)}")
            return None

    def send_encryption_results(self, results):
        """Send encryption results to the server (simulated for educational purposes)."""
        if not self.server_address:
            logger.info("No server configured. Running in standalone mode.")
            return False
            
        try:
            # This is a simulation - not actually sending anything malicious
            logger.info("Sending encryption results to server... (SIMULATION)")
            logger.info(f"Encrypted {len(results['encrypted_files'])} files")
            
            # Store encryption details in config
            self.config["encryption_details"] = {
                "timestamp": datetime.datetime.now().isoformat(),
                "file_count": len(results["encrypted_files"]),
                "target_directory": results["target_directory"],
                "simulation_id": results.get("simulation_id", "unknown")
            }
            self._save_config()
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending encryption results: {str(e)}")
            return False

    def receive_decryption_key(self):
        """Request decryption key from server (simulated for educational purposes)."""
        if not self.server_address:
            logger.info("No server configured. Running in standalone mode.")
            return self.encryption_key
            
        try:
            # This is a simulation - in a real attack, this would be where
            # the victim would have to pay a ransom to receive the key
            logger.info("Requesting decryption key from server... (SIMULATION)")
            
            # In our educational simulation, we actually have the key already
            # and are just pretending to request it from a server
            logger.info("Decryption key received")
            
            return self.encryption_key
            
        except Exception as e:
            logger.error(f"Error receiving decryption key: {str(e)}")
            return None

    def check_for_decryption_command(self):
        """Check if server has sent a decryption command."""
        status = self.check_status()
        
        if status and status.get("command") == "decrypt":
            logger.info("Received decryption command from server")
            return True
            
        return False

def main():
    """Main entry point for the client."""
    parser = argparse.ArgumentParser(description="Ransomware Client for Educational Simulation")
    parser.add_argument("--server", "-s", help="Server address (for demonstration purposes only)")
    parser.add_argument("--check", "-c", action="store_true", help="Check status with server")
    parser.add_argument("--report", "-r", help="Report file containing encryption results")
    parser.add_argument("--request-key", "-k", action="store_true", help="Request decryption key")
    
    args = parser.parse_args()
    
    print("""
========================================================
  EDUCATIONAL RANSOMWARE SIMULATION - CLIENT
========================================================

This application is for EDUCATIONAL PURPOSES ONLY.
It simulates the client portion of a ransomware operation
without any actual malicious functionality.

========================================================
""")
    
    # Create client instance
    client = RansomwareClient(server_address=args.server)
    
    # Check status with server
    if args.check:
        status = client.check_status()
        if status:
            print("\nServer Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
        else:
            print("Failed to check server status.")
    
    # Report encryption results
    if args.report:
        try:
            with open(args.report, 'r') as f:
                results = json.load(f)
            success = client.send_encryption_results(results)
            if success:
                print("Successfully reported encryption results to server.")
            else:
                print("Failed to report encryption results.")
        except Exception as e:
            print(f"Error loading report file: {str(e)}")
    
    # Request decryption key
    if args.request_key:
        key = client.receive_decryption_key()
        if key:
            print("\nDecryption key received:")
            print(key.decode() if isinstance(key, bytes) else key)
        else:
            print("Failed to receive decryption key.")
    
    # If no arguments provided, show help
    if not (args.check or args.report or args.request_key):
        parser.print_help()

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