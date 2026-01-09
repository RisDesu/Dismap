import argparse
import subprocess
import sys
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
import re

def banner():
    RED = "\033[91m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

    print(f"""
{CYAN}===================================================={RESET}
{GREEN} ██████╗ ██╗███████╗███╗   ███╗ █████╗ ██████╗ {RESET}
{GREEN} ██╔══██╗██║██╔════╝████╗ ████║██╔══██╗██╔══██╗{RESET}
{GREEN} ██║  ██║██║███████╗██╔████╔██║███████║██████╔╝{RESET}
{GREEN} ██║  ██║██║╚════██║██║╚██╔╝██║██╔══██║██╔═══╝ {RESET}
{GREEN} ██████╔╝██║███████║██║ ╚═╝ ██║██║  ██║██║     {RESET}
{CYAN}===================================================={RESET}
{RED}        DISMAP v0.1 — Discovery Information Mapping{RESET}
""")


def validate_target(target: str) -> bool:
    """
    Validate target input (IP address or domain name).
    
    Args:
        target: Target string to validate
        
    Returns:
        bool: True if target appears valid, False otherwise
    """
    if not target or len(target) > 255:
        return False
    
    # Basic IP validation (IPv4)
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ip_pattern, target):
        parts = target.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    # Basic domain validation
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    if re.match(domain_pattern, target):
        return True
    
    return False

def check_nmap() -> bool:
    """
    Check if Nmap is installed and accessible.
    
    Returns:
        bool: True if Nmap is available, False otherwise
    """
    try:
        # Run 'nmap --version' to check if Nmap exists
        result = subprocess.run(
            ["nmap", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True
        return False
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"[!] Error checking Nmap: {e}")
        return False

def run_nmap_scan(target: str) -> Optional[str]:
    """
    Run Nmap scan on target and return XML output.
    
    Args:
        target: IP address or domain name to scan
        
    Returns:
        str: XML output from Nmap, or None if scan fails
    """
    print(f"[*] Starting Nmap scan on {target}...")
    
    # Nmap command with XML output to stdout
    # -sS: SYN scan (requires root, but will fallback to -sT if not root)
    # -sV: Version detection
    # -oX -: Output XML to stdout
    nmap_cmd = [
        "nmap",
        "-sS",      # SYN scan (stealth scan)
        "-sV",      # Version detection
        "-oX", "-", # Output XML to stdout
        target
    ]
    
    try:
        # Run Nmap and capture XML output
        result = subprocess.run(
            nmap_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print("[+] Nmap scan completed successfully")
            return result.stdout
        else:
            print(f"[!] Nmap scan failed with return code: {result.returncode}")
            if result.stderr:
                print(f"[!] Error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("[!] Nmap scan timed out (exceeded 5 minutes)")
        return None
    except FileNotFoundError:
        print("[!] Error: Nmap not found. Please install Nmap.")
        return None
    except Exception as e:
        print(f"[!] Unexpected error during Nmap scan: {e}")
        return None

def parse_nmap_xml(xml_string: str) -> Optional[Dict[str, Any]]:
    """
    Parse Nmap XML output and extract structured data.
    
    Args:
        xml_string: XML output from Nmap
        
    Returns:
        dict: Structured scan data, or None if parsing fails
    """
    try:
        root = ET.fromstring(xml_string)
        
        # Initialize result structure
        scan_data = {
            "scan_info": {
                "scanner": "nmap",
                "args": root.get("args", ""),
                "start": root.get("startstr", ""),
                "version": root.get("version", "")
            },
            "hosts": []
        }
        
        # Parse each host
        for host in root.findall("host"):
            host_data = {
                "status": {},
                "addresses": [],
                "ports": []
            }
            
            # Get host status
            status_elem = host.find("status")
            if status_elem is not None:
                host_data["status"] = {
                    "state": status_elem.get("state", "unknown"),
                    "reason": status_elem.get("reason", "")
                }
            
            # Get addresses (IP, MAC, etc.)
            for address in host.findall("address"):
                addr_info = {
                    "addr": address.get("addr", ""),
                    "addrtype": address.get("addrtype", "")
                }
                host_data["addresses"].append(addr_info)
            
            # Get hostnames
            hostnames = host.find("hostnames")
            if hostnames is not None:
                host_data["hostnames"] = []
                for hostname in hostnames.findall("hostname"):
                    host_data["hostnames"].append({
                        "name": hostname.get("name", ""),
                        "type": hostname.get("type", "")
                    })
            
            # Get ports and services
            ports_elem = host.find("ports")
            if ports_elem is not None:
                for port in ports_elem.findall("port"):
                    port_data = {
                        "port": port.get("portid", ""),
                        "protocol": port.get("protocol", ""),
                        "state": {},
                        "service": {}
                    }
                    
                    # Get port state
                    state_elem = port.find("state")
                    if state_elem is not None:
                        port_data["state"] = {
                            "state": state_elem.get("state", ""),
                            "reason": state_elem.get("reason", ""),
                            "reason_ttl": state_elem.get("reason_ttl", "")
                        }
                    
                    # Get service information
                    service_elem = port.find("service")
                    if service_elem is not None:
                        port_data["service"] = {
                            "name": service_elem.get("name", ""),
                            "product": service_elem.get("product", ""),
                            "version": service_elem.get("version", ""),
                            "extrainfo": service_elem.get("extrainfo", ""),
                            "method": service_elem.get("method", ""),
                            "conf": service_elem.get("conf", "")
                        }
                    
                    host_data["ports"].append(port_data)
            
            scan_data["hosts"].append(host_data)
        
        return scan_data
        
    except ET.ParseError as e:
        print(f"[!] Error parsing XML: {e}")
        return None
    except Exception as e:
        print(f"[!] Unexpected error during XML parsing: {e}")
        return None

def save_json_output(data: Dict[str, Any], target: str) -> Optional[str]:
    """
    Save scan results to JSON file in ./output/ directory.
    
    Args:
        data: Structured scan data dictionary
        target: Target name for filename
        
    Returns:
        str: Path to saved file, or None if save fails
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize target for filename
        safe_target = re.sub(r'[^\w\.-]', '_', target)
        filename = f"dismap_{safe_target}_{timestamp}.json"
        filepath = output_dir / filename
        
        # Write JSON file with pretty formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[+] Results saved to: {filepath}")
        return str(filepath)
        
    except PermissionError:
        print(f"[!] Error: Permission denied when writing to {filepath}")
        return None
    except Exception as e:
        print(f"[!] Error saving JSON file: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="DISMAP - Information Mapping Tool")
    parser.add_argument("-t", "--target", required=True, help="Target IP or Domain")
    args = parser.parse_args()

    banner()
    print(f"[+] Target: {args.target}")
    
    # Validate target input
    if not validate_target(args.target):
        print("[!] Error: Invalid target format. Please provide a valid IP address or domain name.")
        sys.exit(1)
    
    # Check if Nmap is available
    if not check_nmap():
        print("[!] Error: Nmap is not installed or not in PATH")
        print("[!] Please install Nmap: sudo apt-get install nmap (on Kali/Debian)")
        sys.exit(1)
    
    # Run Nmap scan
    xml_output = run_nmap_scan(args.target)
    
    if not xml_output:
        print("[!] Failed to retrieve scan data")
        sys.exit(1)
    
    # Parse XML output (Phase 2)
    print("[*] Parsing scan results...")
    scan_data = parse_nmap_xml(xml_output)
    
    if not scan_data:
        print("[!] Failed to parse scan data")
        sys.exit(1)
    
    # Display summary
    print(f"[+] Found {len(scan_data['hosts'])} host(s)")
    for host in scan_data['hosts']:
        if host.get('addresses'):
            ip = host['addresses'][0].get('addr', 'unknown')
            status = host.get('status', {}).get('state', 'unknown')
            port_count = len(host.get('ports', []))
            print(f"    - {ip}: {status} ({port_count} port(s) found)")
    
    # Save to JSON (Phase 3)
    print("[*] Exporting results to JSON...")
    output_file = save_json_output(scan_data, args.target)
    
    if output_file:
        print("[+] DISMAP scan completed successfully!")
    else:
        print("[!] Warning: Scan completed but failed to save results")
        sys.exit(1)

if __name__ == "__main__":
    main()
