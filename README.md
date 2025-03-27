# Educational Ransomware Simulation Tool

**DISCLAIMER: This tool is for EDUCATIONAL PURPOSES ONLY. Using this code for malicious purposes is ILLEGAL and UNETHICAL.**

This project provides a simulated ransomware environment for cybersecurity education, allowing users to understand how ransomware operates in a controlled and safe manner.

## Educational Objectives

- Demonstrate how ransomware encrypts files
- Show how encryption keys are managed
- Illustrate the recovery process
- Teach ransomware prevention strategies
- Provide a hands-on learning environment for cybersecurity education

## Components

This project consists of three main components:

1. **Desktop Simulator** (`ransomware_simulation_desktop.py`): A standalone application that simulates ransomware encryption and recovery in a controlled environment
2. **Client Simulator** (`ransomware_client.py`): Simulates the client portion of a ransomware operation
3. **Server Simulator** (`ransomware_server.py`): Simulates the command & control server operations

## Safety Features

This simulator contains multiple safety features:

- **Educational Mode Only**: All components enforce educational-only operation
- **Auto-Decrypt**: Files are automatically decrypted after 24 hours (configurable)
- **Local Key Storage**: Encryption keys are always saved locally for recovery
- **System Protection**: Critical system directories are protected from encryption
- **Backup Creation**: Original files are backed up rather than deleted
- **Controlled Environment**: Only operates on files in a specified directory

## Usage

### Desktop Simulator

The desktop simulator provides a command-line interface for simulating ransomware:

```bash
python ransomware_simulation_desktop.py --interactive
```

This will start the interactive mode where you can:
- Start a new simulation on a selected directory
- Stop an active simulation and decrypt files
- Configure settings like auto-decrypt
- View educational information

### Command-Line Options

```
usage: ransomware_simulation_desktop.py [-h] [--target TARGET] [--encrypt] [--decrypt]
                                        [--key KEY] [--status] [--recursive] [--interactive]

options:
  -h, --help            show this help message and exit
  --target TARGET, -t TARGET
                        Target directory for simulation
  --encrypt, -e         Encrypt the target directory
  --decrypt, -d         Decrypt the target directory
  --key KEY, -k KEY     Encryption/decryption key
  --status, -s          Show current simulation status
  --recursive, -r       Process subdirectories recursively
  --interactive, -i     Run in interactive mode
```

### Client and Server Simulators

These components demonstrate how ransomware might communicate with a command and control server:

**Start the server:**
```bash
python ransomware_server.py --interactive
```

**Use the client:**
```bash
python ransomware_client.py --check
```

## Educational Content

The simulators include educational information about:

- Real ransomware characteristics
- Best practices for prevention
- What to do if infected
- How encryption works
- Safety mechanisms

## Requirements

- Python 3.6+
- cryptography
- schedule
- tqdm (for progress bars)
- requests (for client/server communication)

## License

This project is for educational purposes only. By using this software, you agree to use it responsibly and ethically.

## Disclaimer

This software is provided "as is", without warranty of any kind. The authors are not responsible for any damage caused by the misuse of this software. This tool is designed for cybersecurity education in controlled environments only.

Using ransomware or similar malicious software against systems without explicit permission is illegal and unethical.