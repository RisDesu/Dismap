# DISMAP v0.1
**Discovery Information Mapping Tool**

[![Version](https://img.shields.io/badge/version-0.1-blue.svg)](https://github.com/yourusername/Dismap)
[![Python](https://img.shields.io/badge/python-3.5+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

## 📋 Overview

DISMAP is a lightweight, educational cybersecurity tool designed for **information gathering** and **data mapping**. It automates Nmap scans and provides structured JSON output for analysis.

**⚠️ Educational Purpose Only**: This tool is designed for learning and legitimate security testing. Always ensure you have proper authorization before scanning any target.

## ✨ Features

- 🔍 Automated Nmap scanning with SYN scan and version detection
- 📊 Structured data extraction (hosts, ports, services, versions)
- 💾 JSON export with timestamped filenames
- ✅ Input validation (IP addresses and domain names)
- 🛡️ Error handling and safety checks
- 📝 Clean, readable code for educational purposes

## 🚀 Installation

### Prerequisites

- **Kali Linux** (recommended) or any Linux distribution
- **Python 3.5+** (uses only standard library)
- **Nmap** (must be installed separately)

### Install Nmap

```bash
# On Kali Linux / Debian / Ubuntu
sudo apt-get update
sudo apt-get install nmap

# Verify installation
nmap --version
```

### Clone Repository

```bash
git clone https://github.com/yourusername/Dismap.git
cd Dismap
```

## 📖 Usage

### Basic Usage

```bash
python3 dismap.py -t <target>
```

### Examples

```bash
# Scan an IP address
python3 dismap.py -t 192.168.1.1

# Scan a domain
python3 dismap.py -t example.com

# Scan localhost
python3 dismap.py -t 127.0.0.1
```

### Command-Line Arguments

```
-t, --target    Target IP address or domain name (required)
```

## 📁 Output

Results are saved in the `./output/` directory with the following naming format:

```
dismap_<target>_<timestamp>.json
```

Example: `dismap_192.168.1.1_20240101_120000.json`

### JSON Structure

```json
{
  "scan_info": {
    "scanner": "nmap",
    "args": "nmap -sS -sV -oX - target",
    "start": "Mon Jan 1 12:00:00 2024",
    "version": "7.94"
  },
  "hosts": [
    {
      "status": {
        "state": "up",
        "reason": "echo-reply"
      },
      "addresses": [
        {
          "addr": "192.168.1.1",
          "addrtype": "ipv4"
        }
      ],
      "hostnames": [],
      "ports": [
        {
          "port": "80",
          "protocol": "tcp",
          "state": {
            "state": "open",
            "reason": "syn-ack"
          },
          "service": {
            "name": "http",
            "product": "Apache",
            "version": "2.4.41"
          }
        }
      ]
    }
  ]
}
```

## 🏗️ Project Structure

```
Dismap/
├── dismap.py          # Main script
├── README.md          # This file
├── requirements.txt   # Dependencies (none - uses stdlib)
├── Define.md         # Documentation (Vietnamese)
├── CODE_REVIEW.md    # Code review and improvements
└── output/           # Output directory (created automatically)
```

## 🔧 How It Works

1. **Input Validation**: Validates target format (IP or domain)
2. **Nmap Check**: Verifies Nmap is installed and accessible
3. **Scan Execution**: Runs Nmap with SYN scan (`-sS`) and version detection (`-sV`)
4. **XML Parsing**: Extracts structured data from Nmap XML output
5. **JSON Export**: Saves results to timestamped JSON file

## ⚙️ Technical Details

### Nmap Parameters Used

- `-sS`: SYN scan (stealth scan, requires root privileges)
- `-sV`: Version detection (identifies service versions)
- `-oX -`: XML output to stdout

### Python Modules

- `argparse`: Command-line argument parsing
- `subprocess`: Running Nmap process
- `xml.etree.ElementTree`: Parsing XML output
- `json`: Exporting to JSON format
- `datetime`: Timestamp generation
- `pathlib`: File path handling
- `re`: Input validation with regular expressions

## 🛡️ Security & Ethics

- **Authorization Required**: Only scan targets you own or have explicit permission to scan
- **Educational Purpose**: This tool is for learning and legitimate security testing
- **No Exploitation**: DISMAP does not perform exploitation, brute-force, or post-exploitation activities
- **Information Gathering Only**: Focuses strictly on reconnaissance and data mapping

## 🐛 Troubleshooting

### Nmap Not Found

```bash
# Install Nmap
sudo apt-get install nmap

# Verify it's in PATH
which nmap
```

### Permission Denied

SYN scan (`-sS`) requires root privileges. If you don't have root, Nmap will automatically fall back to TCP connect scan (`-sT`).

```bash
# Run with sudo (if needed)
sudo python3 dismap.py -t <target>
```

### Invalid Target Error

Ensure your target is a valid:
- IPv4 address (e.g., `192.168.1.1`)
- Domain name (e.g., `example.com`)

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is an educational project. Contributions, suggestions, and improvements are welcome!

## 📧 Contact

For questions or issues, please open an issue on GitHub.

---

**Disclaimer**: This tool is for educational and authorized security testing purposes only. Users are responsible for ensuring they have proper authorization before scanning any target.
