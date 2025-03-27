#!/usr/bin/env python3
"""
Ransomware Simulation Desktop Application for Educational Purposes Only

This application is designed for cybersecurity education to demonstrate
how ransomware works in a controlled environment. It simulates encryption
and recovery processes with built-in safety features.

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
import threading
import datetime
import schedule
from tqdm import tqdm
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ransomware_simulation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RansomwareSimulation")

# Global variables
SIMULATION_DIR = os.path.join(os.path.expanduser("~"), "RansomwareSimulation")
LOG_FILE = os.path.join(SIMULATION_DIR, "simulation.log")
CONFIG_FILE = os.path.join(SIMULATION_DIR, "config.json")
ENCRYPTED_EXT = ".encrypted"
DEFAULT_TIMEOUT_HOURS = 24
EXCLUDED_DIRS = [
    "System Volume Information", 
    "$Recycle.Bin", 
    "Windows",
    "Program Files", 
    "Program Files (x86)",
    "ProgramData"
]

class RansomwareSimulator:
    """Educational Ransomware Simulator for demonstration purposes only."""

    def __init__(self):
        """Initialize the simulator with default settings."""
        self.simulation_id = None
        self.encryption_key = None
        self.encrypted_files = []
        self.target_directory = None
        self.is_simulation_active = False
        self.auto_decrypt_timer = None
        self.config = self._load_config()
        
        # Ensure simulation directory exists
        os.makedirs(SIMULATION_DIR, exist_ok=True)

    def _load_config(self):
        """Load configuration from file or create default if not exists."""
        default_config = {
            "version": "1.0.0",
            "auto_decrypt_enabled": True,
            "auto_decrypt_hours": DEFAULT_TIMEOUT_HOURS,
            "allowed_extensions": [".txt", ".docx", ".xlsx", ".pdf", ".jpg", ".png"],
            "simulation_active": False,
            "last_simulation_id": None,
            "educational_mode": True  # Always keep as True
        }
        
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    # Ensure educational_mode is always True for safety
                    config["educational_mode"] = True
                    return config
            else:
                with open(CONFIG_FILE, 'w') as f:
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
            self.config["simulation_active"] = self.is_simulation_active
            self.config["last_simulation_id"] = self.simulation_id
            
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")

    def generate_key(self):
        """Generate a secure encryption key."""
        key = Fernet.generate_key()
        logger.debug("New encryption key generated")
        return key

    def is_safe_to_encrypt(self, path):
        """Check if it's safe to encrypt a file or directory."""
        abs_path = os.path.abspath(path)
        
        # Safety checks
        system_path = os.path.join(os.environ.get('SystemDrive', 'C:'), os.sep)
        
        # Never encrypt system directories or this application's directory
        if abs_path.startswith(system_path):
            for excluded in EXCLUDED_DIRS:
                if excluded in abs_path.split(os.sep):
                    logger.warning(f"Refusing to process system directory: {abs_path}")
                    return False
        
        # Never encrypt the simulation directory itself
        if abs_path.startswith(SIMULATION_DIR):
            logger.warning(f"Refusing to encrypt simulation directory: {abs_path}")
            return False
            
        # If we're in educational mode (which should always be True),
        # only encrypt within the target directory
        if self.config.get("educational_mode", True):
            if not abs_path.startswith(self.target_directory):
                logger.warning(f"Path {abs_path} is outside target directory - skipping")
                return False
                
        return True

    def encrypt_file(self, file_path):
        """
        Encrypt a single file using Fernet symmetric encryption.
        Returns: path to encrypted file
        """
        if not self.is_safe_to_encrypt(file_path):
            return None
            
        # Skip files that are already encrypted
        if file_path.endswith(ENCRYPTED_EXT):
            return None
            
        # Skip files that don't match allowed extensions in educational mode
        file_ext = os.path.splitext(file_path)[1].lower()
        allowed_extensions = self.config.get("allowed_extensions", [])
        if allowed_extensions and file_ext not in allowed_extensions:
            logger.debug(f"Skipping file with extension {file_ext}: {file_path}")
            return None
            
        try:
            # Initialize the Fernet cipher with the key
            cipher = Fernet(self.encryption_key)
            
            # Read the file content
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            # Encrypt the data
            encrypted_data = cipher.encrypt(file_data)
            
            # Write the encrypted data back to a new file
            encrypted_file_path = file_path + ENCRYPTED_EXT
            with open(encrypted_file_path, 'wb') as file:
                file.write(encrypted_data)
                
            # Create a metadata file with original filename for recovery
            metadata = {
                "original_filename": os.path.basename(file_path),
                "encryption_time": datetime.datetime.now().isoformat(),
                "simulation_id": self.simulation_id
            }
            
            metadata_path = encrypted_file_path + ".meta"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
                
            # In educational mode, don't delete original file, just rename it
            if self.config.get("educational_mode", True):
                backup_path = file_path + ".backup"
                os.rename(file_path, backup_path)
            else:
                # This should never execute due to safety checks
                pass
            
            logger.debug(f"Encrypted file: {file_path}")
            return encrypted_file_path
        except Exception as e:
            logger.error(f"Error encrypting file {file_path}: {str(e)}")
            return None

    def decrypt_file(self, encrypted_file_path):
        """
        Decrypt a single file that was encrypted using Fernet.
        Returns: path to decrypted file
        """
        try:
            # Verify the file exists and has the .encrypted extension
            if not encrypted_file_path.endswith(ENCRYPTED_EXT):
                logger.warning(f"File {encrypted_file_path} doesn't have {ENCRYPTED_EXT} extension")
                return None
                
            # Initialize the Fernet cipher with the key
            cipher = Fernet(self.encryption_key)
            
            # Read the encrypted data
            with open(encrypted_file_path, 'rb') as file:
                encrypted_data = file.read()
                
            # Decrypt the data
            try:
                decrypted_data = cipher.decrypt(encrypted_data)
            except Exception as e:
                logger.error(f"Decryption failed for {encrypted_file_path}: {str(e)}")
                return None
            
            # Check for metadata file to get original filename
            metadata_path = encrypted_file_path + ".meta"
            original_file_path = encrypted_file_path[:-len(ENCRYPTED_EXT)]  # Default: just remove extension
            
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    # We could use the original filename from metadata if needed
                except Exception:
                    pass
                    
            # Write the decrypted data to the original file
            with open(original_file_path, 'wb') as file:
                file.write(decrypted_data)
                
            # Remove the encrypted file and metadata
            os.remove(encrypted_file_path)
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
                
            # Remove backup file if it exists
            backup_path = original_file_path + ".backup"
            if os.path.exists(backup_path):
                os.remove(backup_path)
            
            logger.debug(f"Decrypted file: {encrypted_file_path}")
            return original_file_path
        except Exception as e:
            logger.error(f"Error decrypting file {encrypted_file_path}: {str(e)}")
            return None

    def encrypt_directory(self, directory_path, recursive=True):
        """
        Encrypt all files in a directory.
        Returns: list of encrypted files
        """
        if not self.is_safe_to_encrypt(directory_path):
            logger.warning(f"Directory {directory_path} failed safety check - aborting")
            return []
            
        self.target_directory = os.path.abspath(directory_path)
        encrypted_files = []
        
        try:
            for root, dirs, files in os.walk(directory_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
                
                # Process files in current directory
                for filename in files:
                    # Skip already encrypted files
                    if filename.endswith(ENCRYPTED_EXT) or filename.endswith(".meta") or filename.endswith(".backup"):
                        continue
                        
                    file_path = os.path.join(root, filename)
                    encrypted_file_path = self.encrypt_file(file_path)
                    if encrypted_file_path:
                        encrypted_files.append(encrypted_file_path)
                
                # If not recursive, break after first directory
                if not recursive:
                    break
            
            logger.info(f"Encrypted {len(encrypted_files)} files in {directory_path}")
            return encrypted_files
        except Exception as e:
            logger.error(f"Error encrypting directory {directory_path}: {str(e)}")
            return encrypted_files

    def decrypt_directory(self, directory_path, recursive=True):
        """
        Decrypt all encrypted files in a directory.
        Returns: list of decrypted files
        """
        decrypted_files = []
        
        try:
            for root, dirs, files in os.walk(directory_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
                
                # Process files in current directory
                for filename in files:
                    # Only decrypt files with .encrypted extension
                    if filename.endswith(ENCRYPTED_EXT):
                        file_path = os.path.join(root, filename)
                        decrypted_file_path = self.decrypt_file(file_path)
                        if decrypted_file_path:
                            decrypted_files.append(decrypted_file_path)
                
                # If not recursive, break after first directory
                if not recursive:
                    break
            
            logger.info(f"Decrypted {len(decrypted_files)} files in {directory_path}")
            return decrypted_files
        except Exception as e:
            logger.error(f"Error decrypting directory {directory_path}: {str(e)}")
            return decrypted_files

    def start_simulation(self, target_directory, recursive=True):
        """Start a new ransomware simulation."""
        if self.is_simulation_active:
            logger.warning("A simulation is already active. Please stop it first.")
            return False
            
        logger.info(f"Starting ransomware simulation on directory: {target_directory}")
        
        # Generate a unique ID for this simulation
        self.simulation_id = f"SIM-{int(time.time())}"
        
        # Generate and store encryption key
        self.encryption_key = self.generate_key()
        
        # Save the key to the simulation directory for safety
        key_file = os.path.join(SIMULATION_DIR, f"recovery_key_{self.simulation_id}.key")
        with open(key_file, 'wb') as f:
            f.write(self.encryption_key)
        logger.info(f"Recovery key saved to: {key_file}")
        
        # Set simulation as active and save config
        self.is_simulation_active = True
        self.target_directory = os.path.abspath(target_directory)
        self._save_config()
        
        # Start encrypting files
        self.encrypted_files = self.encrypt_directory(target_directory, recursive)
        
        # Create ransom note
        self.create_ransom_note(target_directory)
        
        # Schedule auto-decrypt if enabled
        if self.config.get("auto_decrypt_enabled", True):
            self.schedule_auto_decrypt()
            
        logger.info(f"Simulation {self.simulation_id} started successfully. Encrypted {len(self.encrypted_files)} files.")
        return True

    def stop_simulation(self):
        """Stop the active simulation and decrypt all files."""
        if not self.is_simulation_active:
            logger.warning("No active simulation to stop.")
            return False
            
        logger.info("Stopping simulation and decrypting files...")
        
        if self.target_directory and os.path.exists(self.target_directory):
            decrypted_files = self.decrypt_directory(self.target_directory)
            logger.info(f"Decrypted {len(decrypted_files)} files.")
            
            # Remove any ransom notes
            ransom_note_path = os.path.join(self.target_directory, "RANSOM_NOTE.txt")
            if os.path.exists(ransom_note_path):
                os.remove(ransom_note_path)
        else:
            logger.error("Target directory not found or not set.")
            
        # Reset simulation state
        self.is_simulation_active = False
        self.simulation_id = None
        self.encrypted_files = []
        self.target_directory = None
        
        # Cancel auto-decrypt timer
        if self.auto_decrypt_timer:
            self.auto_decrypt_timer = None
            
        # Update config
        self._save_config()
        logger.info("Simulation stopped successfully.")
        return True

    def create_ransom_note(self, target_directory):
        """Create a simulated ransom note in the target directory."""
        ransom_note_path = os.path.join(target_directory, "RANSOM_NOTE.txt")
        
        # Convert the key to a string for display
        key_str = self.encryption_key.decode('utf-8')
        
        # Format the note
        note_text = f"""
========================================
    EDUCATIONAL RANSOMWARE SIMULATION
========================================

THIS IS A SIMULATION - NO REAL DANGER

Your files have been encrypted as part of an educational demonstration.

Simulation ID: {self.simulation_id}
Files Encrypted: {len(self.encrypted_files)}
Encryption Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

To decrypt your files, you can:

1. Use the recovery key provided below with the decryption tool
2. Wait for the automatic decryption (if enabled)

RECOVERY KEY: {key_str}

----------------------------------------
IMPORTANT EDUCATIONAL NOTICE:
----------------------------------------
This is a cybersecurity educational demonstration.
In a real ransomware attack:
- Victims would not receive the decryption key
- Payment would be demanded (typically in cryptocurrency)
- No guarantee of recovery would exist even after payment
- Files might be permanently lost

Best practices for ransomware prevention:
- Regular backups stored offline
- Up-to-date antivirus and security software
- Employee security training
- Careful email and attachment handling
- System and software updates

========================================
"""
        
        try:
            with open(ransom_note_path, 'w') as f:
                f.write(note_text)
            logger.info(f"Created ransom note at: {ransom_note_path}")
        except Exception as e:
            logger.error(f"Error creating ransom note: {str(e)}")

    def schedule_auto_decrypt(self):
        """Schedule automatic decryption after the configured timeout."""
        hours = self.config.get("auto_decrypt_hours", DEFAULT_TIMEOUT_HOURS)
        
        logger.info(f"Scheduling automatic decryption after {hours} hours")
        
        # Schedule the auto-decrypt job
        def auto_decrypt_job():
            logger.info("Auto-decrypt timer triggered")
            self.stop_simulation()
        
        # Calculate the target time
        target_time = datetime.datetime.now() + datetime.timedelta(hours=hours)
        
        # Display when auto-decrypt will happen
        logger.info(f"Auto-decrypt scheduled for: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Schedule the job
        self.auto_decrypt_timer = threading.Timer(hours * 3600, auto_decrypt_job)
        self.auto_decrypt_timer.daemon = True
        self.auto_decrypt_timer.start()

    def display_status(self):
        """Display the current status of the simulator."""
        status = {
            "Simulation Active": self.is_simulation_active,
            "Simulation ID": self.simulation_id or "None",
            "Target Directory": self.target_directory or "None",
            "Files Encrypted": len(self.encrypted_files),
            "Auto-Decrypt Enabled": self.config.get("auto_decrypt_enabled", True),
            "Auto-Decrypt Timeout": f"{self.config.get('auto_decrypt_hours', DEFAULT_TIMEOUT_HOURS)} hours"
        }
        
        print("\n=== Ransomware Simulator Status ===")
        for key, value in status.items():
            print(f"{key}: {value}")
        print("===================================\n")
        
        # If simulation is active, show the recovery key
        if self.is_simulation_active and self.encryption_key:
            print("RECOVERY KEY (Save this for decryption):")
            print(self.encryption_key.decode('utf-8'))
            print()
        
        return status

    def save_encrypted_file_list(self):
        """Save the list of encrypted files for recovery tracking."""
        if not self.encrypted_files:
            return
            
        list_path = os.path.join(SIMULATION_DIR, f"encrypted_files_{self.simulation_id}.json")
        try:
            with open(list_path, 'w') as f:
                json.dump(self.encrypted_files, f, indent=4)
            logger.info(f"Saved encrypted file list to: {list_path}")
        except Exception as e:
            logger.error(f"Error saving encrypted file list: {str(e)}")

def print_disclaimer():
    """Print the disclaimer notice."""
    disclaimer = """
========================================================
  EDUCATIONAL RANSOMWARE SIMULATION - DISCLAIMER
========================================================

This application is for EDUCATIONAL PURPOSES ONLY.

It is designed to demonstrate ransomware mechanics in a
controlled environment to help understand cybersecurity
threats and defenses.

THE SOFTWARE CONTAINS MULTIPLE SAFETY FEATURES:
- Files are never permanently encrypted
- Automatic decryption failsafe is built-in
- Recovery keys are always saved locally
- System directories are protected

USING THIS SOFTWARE FOR MALICIOUS PURPOSES IS:
1. ILLEGAL - Unauthorized encryption of data is a crime
2. UNETHICAL - Causing harm to others is wrong
3. POTENTIALLY HARMFUL - Even with safeguards

By using this software, you agree to use it responsibly
and ethically for educational purposes only.

========================================================
"""
    print(disclaimer)
    confirmation = input("Do you understand and agree to use this tool for educational purposes only? (yes/no): ")
    if confirmation.lower() not in ["yes", "y"]:
        print("Exiting application. Agreement required to continue.")
        sys.exit(0)

def interactive_mode(simulator):
    """Run the simulator in interactive command-line mode."""
    print_disclaimer()
    
    while True:
        print("\n=== Ransomware Simulation Tool (Educational) ===")
        print("1. Start new simulation")
        print("2. Stop active simulation")
        print("3. Show simulation status")
        print("4. Configure settings")
        print("5. Help & educational information")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ")
        
        if choice == "1":
            if simulator.is_simulation_active:
                print("A simulation is already active. Please stop it first.")
                continue
                
            target_dir = input("Enter target directory path: ")
            if not os.path.exists(target_dir):
                print(f"Directory does not exist: {target_dir}")
                continue
                
            recursive = input("Process subdirectories? (yes/no, default: yes): ").lower() != "no"
            
            print(f"\nStarting simulation on: {target_dir}")
            print("Encrypting files... (this may take a while)")
            
            success = simulator.start_simulation(target_dir, recursive)
            if success:
                print(f"Simulation started! Encrypted {len(simulator.encrypted_files)} files.")
                print(f"A ransom note has been created in the target directory.")
                print("\nIMPORTANT: Save your recovery key:")
                print(simulator.encryption_key.decode('utf-8'))
                simulator.save_encrypted_file_list()
            else:
                print("Failed to start simulation. Check the logs for details.")
                
        elif choice == "2":
            if not simulator.is_simulation_active:
                print("No active simulation to stop.")
                continue
                
            confirm = input("Are you sure you want to stop the simulation and decrypt all files? (yes/no): ")
            if confirm.lower() not in ["yes", "y"]:
                continue
                
            print("Decrypting files... (this may take a while)")
            success = simulator.stop_simulation()
            if success:
                print("Simulation stopped successfully! All files have been decrypted.")
            else:
                print("Failed to stop simulation. Check the logs for details.")
                
        elif choice == "3":
            simulator.display_status()
            
        elif choice == "4":
            print("\n=== Configuration Settings ===")
            print(f"1. Auto-decrypt: {'Enabled' if simulator.config.get('auto_decrypt_enabled', True) else 'Disabled'}")
            print(f"2. Auto-decrypt timeout: {simulator.config.get('auto_decrypt_hours', DEFAULT_TIMEOUT_HOURS)} hours")
            print("3. Return to main menu")
            
            config_choice = input("\nEnter setting to change (1-3): ")
            
            if config_choice == "1":
                current = simulator.config.get("auto_decrypt_enabled", True)
                new_value = input(f"Auto-decrypt is currently {'enabled' if current else 'disabled'}. Change? (yes/no): ")
                if new_value.lower() in ["yes", "y"]:
                    simulator.config["auto_decrypt_enabled"] = not current
                    simulator._save_config()
                    print(f"Auto-decrypt is now {'enabled' if not current else 'disabled'}")
                    
            elif config_choice == "2":
                current = simulator.config.get("auto_decrypt_hours", DEFAULT_TIMEOUT_HOURS)
                try:
                    new_value = int(input(f"Enter new timeout in hours (current: {current}): "))
                    if new_value < 1:
                        print("Timeout must be at least 1 hour.")
                    else:
                        simulator.config["auto_decrypt_hours"] = new_value
                        simulator._save_config()
                        print(f"Auto-decrypt timeout set to {new_value} hours")
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    
        elif choice == "5":
            print("\n=== Educational Information ===")
            print("\nReal Ransomware Characteristics:")
            print("- Uses strong encryption algorithms (RSA, AES)")
            print("- Targets valuable files (.doc, .pdf, databases, etc.)")
            print("- Deletes backups and shadow copies")
            print("- Demands payment in cryptocurrency")
            print("- May threaten to publish sensitive data")
            print("- Often spreads through phishing, RDP, or exploits")
            
            print("\nBest Practices for Prevention:")
            print("1. Regular offline backups")
            print("2. Updated security software")
            print("3. Employee security training")
            print("4. Email filtering and caution with attachments")
            print("5. Network segmentation")
            print("6. Principle of least privilege")
            print("7. Patching and updates")
            
            print("\nWhat To Do If Really Infected:")
            print("1. Isolate infected systems")
            print("2. Report to authorities")
            print("3. Consult cybersecurity experts")
            print("4. Restore from backups if available")
            print("5. Consider business impact before paying ransom")
            
            input("\nPress Enter to continue...")
            
        elif choice == "6":
            if simulator.is_simulation_active:
                confirm = input("A simulation is still active. Stop it and decrypt files before exiting? (yes/no): ")
                if confirm.lower() in ["yes", "y"]:
                    simulator.stop_simulation()
                    
            print("Exiting. Thank you for using the educational simulator.")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Ransomware Simulation Tool (For Educational Purposes Only)")
    parser.add_argument("--target", "-t", help="Target directory for simulation")
    parser.add_argument("--encrypt", "-e", action="store_true", help="Encrypt the target directory")
    parser.add_argument("--decrypt", "-d", action="store_true", help="Decrypt the target directory")
    parser.add_argument("--key", "-k", help="Encryption/decryption key (if not provided, a new one will be generated)")
    parser.add_argument("--status", "-s", action="store_true", help="Show current simulation status")
    parser.add_argument("--recursive", "-r", action="store_true", help="Process subdirectories recursively")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Create simulator instance
    simulator = RansomwareSimulator()
    
    # If no arguments provided, default to interactive mode
    if len(sys.argv) == 1:
        args.interactive = True
    
    # Interactive mode
    if args.interactive:
        interactive_mode(simulator)
        return
    
    # Display status and exit
    if args.status:
        simulator.display_status()
        return
    
    # Ensure target directory is provided for encryption/decryption
    if (args.encrypt or args.decrypt) and not args.target:
        print("Error: Target directory is required for encryption/decryption.")
        parser.print_help()
        return
    
    # Handle encryption
    if args.encrypt:
        print_disclaimer()
        
        if not os.path.exists(args.target):
            print(f"Error: Target directory does not exist: {args.target}")
            return
            
        if args.key:
            try:
                simulator.encryption_key = args.key.encode()
            except Exception as e:
                print(f"Error with provided key: {str(e)}")
                return
        
        print(f"Starting simulation on: {args.target}")
        success = simulator.start_simulation(args.target, args.recursive)
        
        if success:
            print(f"Simulation started! Encrypted {len(simulator.encrypted_files)} files.")
            print(f"A ransom note has been created in the target directory.")
            print("\nIMPORTANT: Save your recovery key:")
            print(simulator.encryption_key.decode('utf-8'))
            simulator.save_encrypted_file_list()
        else:
            print("Failed to start simulation. Check the logs for details.")
    
    # Handle decryption
    elif args.decrypt:
        if not os.path.exists(args.target):
            print(f"Error: Target directory does not exist: {args.target}")
            return
            
        if args.key:
            try:
                simulator.encryption_key = args.key.encode()
            except Exception as e:
                print(f"Error with provided key: {str(e)}")
                return
        elif simulator.is_simulation_active and simulator.encryption_key:
            # Use the active simulation key
            pass
        else:
            print("Error: Decryption key is required. Provide with --key or use an active simulation.")
            return
            
        print(f"Decrypting directory: {args.target}")
        decrypted_files = simulator.decrypt_directory(args.target, args.recursive)
        print(f"Decryption complete! Recovered {len(decrypted_files)} files.")

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