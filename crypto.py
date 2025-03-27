#!/usr/bin/env python3
"""
Cryptography utility functions for the ransomware simulation

This module provides encryption and decryption functionality for the
educational ransomware simulation. It uses the Fernet symmetric encryption
from the cryptography library.

DISCLAIMER: This tool is for EDUCATIONAL PURPOSES ONLY.
Using this code for malicious purposes is ILLEGAL and UNETHICAL.
"""

import os
import logging
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CryptoUtils")

def generate_key():
    """Generate a secure encryption key"""
    key = Fernet.generate_key()
    logger.debug("New encryption key generated")
    return key

def encrypt_file(file_path, key):
    """
    Encrypts a single file using Fernet symmetric encryption
    Returns: path to encrypted file
    """
    try:
        # Initialize the Fernet cipher with the key
        cipher = Fernet(key)
        
        # Read the file content
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        # Encrypt the data
        encrypted_data = cipher.encrypt(file_data)
        
        # Write the encrypted data back to a new file
        encrypted_file_path = file_path + ".encrypted"
        with open(encrypted_file_path, 'wb') as file:
            file.write(encrypted_data)
        
        logger.debug(f"Encrypted file: {file_path}")
        return encrypted_file_path
    except Exception as e:
        logger.error(f"Error encrypting file {file_path}: {str(e)}")
        return None

def decrypt_file(encrypted_file_path, key):
    """
    Decrypts a single file that was encrypted using Fernet
    Returns: path to decrypted file
    """
    try:
        # Verify the file exists and has the .encrypted extension
        if not encrypted_file_path.endswith(".encrypted"):
            logger.warning(f"File {encrypted_file_path} doesn't have .encrypted extension")
            return None
        
        # Initialize the Fernet cipher with the key
        cipher = Fernet(key)
        
        # Read the encrypted data
        with open(encrypted_file_path, 'rb') as file:
            encrypted_data = file.read()
        
        # Decrypt the data
        try:
            decrypted_data = cipher.decrypt(encrypted_data)
        except InvalidToken:
            logger.error(f"Invalid decryption key for {encrypted_file_path}")
            return None
        
        # Write the decrypted data to the original file (without the .encrypted extension)
        original_file_path = encrypted_file_path[:-len(".encrypted")]
        with open(original_file_path, 'wb') as file:
            file.write(decrypted_data)
        
        # Remove the encrypted file
        os.remove(encrypted_file_path)
        
        logger.debug(f"Decrypted file: {encrypted_file_path}")
        return original_file_path
    except Exception as e:
        logger.error(f"Error decrypting file {encrypted_file_path}: {str(e)}")
        return None

def encrypt_directory(directory_path, key):
    """
    Encrypts all files in a directory
    Returns: list of encrypted files
    """
    encrypted_files = []
    
    try:
        for root, dirs, files in os.walk(directory_path):
            # Process files in current directory
            for filename in files:
                # Skip already encrypted files
                if filename.endswith(".encrypted"):
                    continue
                
                file_path = os.path.join(root, filename)
                encrypted_file_path = encrypt_file(file_path, key)
                if encrypted_file_path:
                    encrypted_files.append(encrypted_file_path)
        
        logger.info(f"Encrypted {len(encrypted_files)} files in {directory_path}")
        return encrypted_files
    except Exception as e:
        logger.error(f"Error encrypting directory {directory_path}: {str(e)}")
        return encrypted_files

def decrypt_directory(directory_path, key):
    """
    Decrypts all encrypted files in a directory
    Returns: list of decrypted files
    """
    decrypted_files = []
    
    try:
        for root, dirs, files in os.walk(directory_path):
            # Process files in current directory
            for filename in files:
                # Only decrypt files with .encrypted extension
                if filename.endswith(".encrypted"):
                    file_path = os.path.join(root, filename)
                    decrypted_file_path = decrypt_file(file_path, key)
                    if decrypted_file_path:
                        decrypted_files.append(decrypted_file_path)
        
        logger.info(f"Decrypted {len(decrypted_files)} files in {directory_path}")
        return decrypted_files
    except Exception as e:
        logger.error(f"Error decrypting directory {directory_path}: {str(e)}")
        return decrypted_files

if __name__ == "__main__":
    print("This module provides encryption/decryption utilities for the ransomware simulation.")
    print("It is not meant to be run directly. Import it into your simulation application.")