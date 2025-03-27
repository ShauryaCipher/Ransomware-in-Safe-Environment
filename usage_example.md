# Using the Educational Ransomware Simulation Tool

This document provides a quick guide to using the ransomware simulation tool for educational purposes.

## Disclaimer

**IMPORTANT:** This tool is for **EDUCATIONAL PURPOSES ONLY**. Using this code for malicious purposes is ILLEGAL and UNETHICAL.

## Installation

1. Unzip the package file
2. Run the appropriate installation script:
   - On Linux/Mac: `sh install.sh`
   - On Windows: Double-click `install.bat`

## Desktop Simulator Usage

The desktop simulator provides a standalone way to test and understand ransomware behavior in a safe environment.

### Interactive Mode

The easiest way to use the simulator is in interactive mode:

```bash
python ransomware_simulation_desktop.py --interactive
```

This will present a menu with options:
1. Start new simulation
2. Stop active simulation
3. Show simulation status
4. Configure settings
5. Help & educational information
6. Exit

### Command-Line Options

You can also use command-line options for specific operations:

```bash
# Start a simulation on a specific directory
python ransomware_simulation_desktop.py --target /path/to/test_directory --encrypt

# Decrypt files after a simulation
python ransomware_simulation_desktop.py --target /path/to/test_directory --decrypt --key YOUR_KEY

# Show current simulation status
python ransomware_simulation_desktop.py --status
```

## Client-Server Simulation

The package also includes a client-server simulation that demonstrates how ransomware communicates with command and control servers.

### Server

Start the server simulator:

```bash
python ransomware_server.py --interactive
```

### Client

Use the client to communicate with the server:

```bash
python ransomware_client.py --server localhost:8080 --check
```

## Safe Testing Environment

For testing, create a dedicated directory with non-sensitive test files:

```bash
mkdir test_directory
echo "This is a test file" > test_directory/document1.txt
echo "Another test file" > test_directory/document2.txt
```

Then run the simulation on this directory:

```bash
python ransomware_simulation_desktop.py --target test_directory --encrypt
```

## Safety Features

The simulator includes several safety features:

1. All encrypted files can be recovered with the provided key
2. Original files are backed up before encryption
3. System directories are protected from encryption
4. Automatic decryption occurs after 24 hours (configurable)
5. Recovery keys are always stored locally

## Educational Resources

Refer to the `educational_resources` directory for information about ransomware prevention strategies and best practices for security.

## Examples of What You'll Learn

- How encryption is used in ransomware attacks
- The communication between infected clients and command servers
- Best practices for preventing ransomware attacks
- The importance of secure backups
- How encryption keys are managed in attacks

Remember: This tool is designed to educate, not to cause harm. Use it responsibly in controlled environments only.