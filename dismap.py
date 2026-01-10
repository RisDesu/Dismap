import argparse
import subprocess
import sys
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
import re
import os
import platform

def setup_colors():
    """Setup color codes with Windows compatibility."""
    # Enable ANSI escape sequences on Windows 10+
    if platform.system() == 'Windows':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)  # Enable ANSI
        except:
            pass  # Fallback to no colors if fails
    
    # Return color codes
    return {
        'RED': '\033[91m',
        'GREEN': '\033[92m',
        'CYAN': '\033[96m',
        'YELLOW': '\033[93m',
        'RESET': '\033[0m'
    }

def banner():
    colors = setup_colors()
    RED = colors['RED']
    GREEN = colors['GREEN']
    CYAN = colors['CYAN']
    RESET = colors['RESET']

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
    Validate target input (IP address, CIDR range, or domain name).
    
    Args:
        target: Target string to validate
        
    Returns:
        bool: True if target appears valid, False otherwise
    """
    if not target or len(target) > 255:
        return False
    
    # CIDR range validation (IPv4)
    cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
    if re.match(cidr_pattern, target):
        parts = target.split('/')
        ip = parts[0]
        cidr = int(parts[1])
        if 0 <= cidr <= 32:
            ip_parts = ip.split('.')
            if all(0 <= int(part) <= 255 for part in ip_parts):
                return True
        return False
    
    # IPv4 validation
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, target):
        parts = target.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    # IPv6 validation (basic)
    ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'
    if re.match(ipv6_pattern, target.replace('::', ':')):
        return True
    
    # IPv6 CIDR validation
    ipv6_cidr_pattern = r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}/\d{1,3}$'
    if re.match(ipv6_cidr_pattern, target.replace('::', ':')):
        parts = target.split('/')
        if 0 <= int(parts[1]) <= 128:
            return True
        return False
    
    # Domain validation
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
        colors = setup_colors()
        print(f"{colors['YELLOW']}[!]{colors['RESET']} Error checking Nmap: {e}")
        return False

def run_nmap_scan(target: str, scan_type: str = "syn", version_detection: bool = True, 
                  os_detection: bool = False, ports: Optional[str] = None, 
                  timing: Optional[str] = None, verbose: bool = False) -> Optional[str]:
    """
    Run Nmap scan on target and return XML output.
    
    Args:
        target: IP address, CIDR range, or domain name to scan
        scan_type: Type of scan (syn, connect, udp, etc.)
        version_detection: Enable version detection (-sV)
        os_detection: Enable OS detection (-O)
        ports: Port range or specific ports (e.g., "80,443" or "1-1000")
        timing: Timing template (T0-T5)
        verbose: Enable verbose output
        
    Returns:
        str: XML output from Nmap, or None if scan fails
    """
    colors = setup_colors()
    print(f"{colors['CYAN']}[*]{colors['RESET']} Starting Nmap scan on {target}...")
    
    # Build Nmap command
    nmap_cmd = ["nmap"]
    
    # Scan type
    if scan_type == "syn":
        nmap_cmd.append("-sS")
    elif scan_type == "connect":
        nmap_cmd.append("-sT")
    elif scan_type == "udp":
        nmap_cmd.append("-sU")
    else:
        nmap_cmd.append("-sS")  # Default to SYN scan
    
    # Version detection
    if version_detection:
        nmap_cmd.append("-sV")
    
    # OS detection (requires root)
    if os_detection:
        nmap_cmd.append("-O")
    
    # Port specification
    if ports:
        nmap_cmd.extend(["-p", ports])
    
    # Timing template
    if timing:
        nmap_cmd.append(f"-T{timing}")
    
    # Verbose mode
    if verbose:
        nmap_cmd.append("-v")
    
    # Output XML to stdout
    nmap_cmd.extend(["-oX", "-"])
    
    # Add target
    nmap_cmd.append(target)
    
    try:
        # Run Nmap and capture XML output
        if verbose:
            print(f"{colors['YELLOW']}[DEBUG]{colors['RESET']} Running: {' '.join(nmap_cmd)}")
        
        result = subprocess.run(
            nmap_cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout (increased for larger scans)
        )
        
        if result.returncode == 0:
            print(f"{colors['GREEN']}[+]{colors['RESET']} Nmap scan completed successfully")
            if verbose and result.stderr:
                print(f"{colors['YELLOW']}[INFO]{colors['RESET']} {result.stderr}")
            return result.stdout
        else:
            print(f"{colors['RED']}[!]{colors['RESET']} Nmap scan failed with return code: {result.returncode}")
            if result.stderr:
                print(f"{colors['RED']}[!]{colors['RESET']} Error: {result.stderr}")
            # Check if it's a permission issue
            if "requires root privileges" in result.stderr or "Operation not permitted" in result.stderr:
                print(f"{colors['YELLOW']}[!]{colors['RESET']} Note: Some scan types require root/administrator privileges.")
                print(f"{colors['YELLOW']}[!]{colors['RESET']} Try: sudo python3 dismap.py -t {target}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"{colors['RED']}[!]{colors['RESET']} Nmap scan timed out (exceeded 10 minutes)")
        return None
    except FileNotFoundError:
        print(f"{colors['RED']}[!]{colors['RESET']} Error: Nmap not found. Please install Nmap.")
        return None
    except Exception as e:
        print(f"{colors['RED']}[!]{colors['RESET']} Unexpected error during Nmap scan: {e}")
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
            host_data["hostnames"] = []
            if hostnames is not None:
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
                            "conf": service_elem.get("conf", ""),
                            "cpe": service_elem.get("cpe", "")
                        }
                    
                    host_data["ports"].append(port_data)
            
            # Get OS detection results
            os_elem = host.find("os")
            host_data["os"] = {}
            if os_elem is not None:
                os_matches = []
                for osmatch in os_elem.findall("osmatch"):
                    os_matches.append({
                        "name": osmatch.get("name", ""),
                        "accuracy": osmatch.get("accuracy", ""),
                        "line": osmatch.get("line", "")
                    })
                host_data["os"]["matches"] = os_matches
                
                # Get OS classes
                os_classes = []
                for osclass in os_elem.findall("osclass"):
                    os_classes.append({
                        "type": osclass.get("type", ""),
                        "vendor": osclass.get("vendor", ""),
                        "osgen": osclass.get("osgen", ""),
                        "accuracy": osclass.get("accuracy", ""),
                        "cpe": osclass.get("cpe", "")
                    })
                if os_classes:
                    host_data["os"]["classes"] = os_classes
            
            scan_data["hosts"].append(host_data)
        
        return scan_data
        
    except ET.ParseError as e:
        colors = setup_colors()
        print(f"{colors['RED']}[!]{colors['RESET']} Error parsing XML: {e}")
        return None
    except Exception as e:
        colors = setup_colors()
        print(f"{colors['RED']}[!]{colors['RESET']} Unexpected error during XML parsing: {e}")
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
        
        colors = setup_colors()
        print(f"{colors['GREEN']}[+]{colors['RESET']} Results saved to: {filepath}")
        return str(filepath)
        
    except PermissionError:
        colors = setup_colors()
        print(f"{colors['RED']}[!]{colors['RESET']} Error: Permission denied when writing to output directory")
        return None
    except Exception as e:
        colors = setup_colors()
        print(f"{colors['RED']}[!]{colors['RESET']} Error saving JSON file: {e}")
        return None

def main():
    colors = setup_colors()
    parser = argparse.ArgumentParser(
        description="DISMAP - Discovery Information Mapping Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 dismap.py -t 192.168.1.1
  python3 dismap.py -t example.com -O -v
  python3 dismap.py -t 192.168.1.0/24 -p 80,443,8080
  python3 dismap.py -t 192.168.1.1 --scan-type connect --timing T4
        """
    )
    parser.add_argument("-t", "--target", required=True, 
                       help="Target IP address, CIDR range (e.g., 192.168.1.0/24), or domain name")
    parser.add_argument("-s", "--scan-type", choices=["syn", "connect", "udp"], 
                       default="syn", help="Scan type (default: syn)")
    parser.add_argument("-p", "--ports", 
                       help="Port range or specific ports (e.g., '80,443' or '1-1000')")
    parser.add_argument("-O", "--os-detection", action="store_true",
                       help="Enable OS detection (requires root privileges)")
    parser.add_argument("--no-version", action="store_true",
                       help="Disable version detection (faster scan)")
    parser.add_argument("-T", "--timing", choices=["0", "1", "2", "3", "4", "5"],
                       help="Timing template (0=paranoid, 5=insane, default: 3)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--no-banner", action="store_true",
                       help="Hide banner")
    
    args = parser.parse_args()

    if not args.no_banner:
        banner()
    
    print(f"{colors['GREEN']}[+]{colors['RESET']} Target: {args.target}")
    
    # Validate target input
    if not validate_target(args.target):
        print(f"{colors['RED']}[!]{colors['RESET']} Error: Invalid target format.")
        print(f"{colors['RED']}[!]{colors['RESET']} Please provide a valid IP address, CIDR range, or domain name.")
        sys.exit(1)
    
    # Check if Nmap is available
    if not check_nmap():
        print(f"{colors['RED']}[!]{colors['RESET']} Error: Nmap is not installed or not in PATH")
        print(f"{colors['RED']}[!]{colors['RESET']} Please install Nmap:")
        if platform.system() == "Windows":
            print(f"{colors['YELLOW']}    Download from: https://nmap.org/download.html{colors['RESET']}")
        else:
            print(f"{colors['YELLOW']}    sudo apt-get install nmap (on Kali/Debian/Ubuntu){colors['RESET']}")
        sys.exit(1)
    
    # Run Nmap scan
    xml_output = run_nmap_scan(
        target=args.target,
        scan_type=args.scan_type,
        version_detection=not args.no_version,
        os_detection=args.os_detection,
        ports=args.ports,
        timing=args.timing,
        verbose=args.verbose
    )
    
    if not xml_output:
        print(f"{colors['RED']}[!]{colors['RESET']} Failed to retrieve scan data")
        sys.exit(1)
    
    # Parse XML output
    print(f"{colors['CYAN']}[*]{colors['RESET']} Parsing scan results...")
    scan_data = parse_nmap_xml(xml_output)
    
    if not scan_data:
        print(f"{colors['RED']}[!]{colors['RESET']} Failed to parse scan data")
        sys.exit(1)
    
    # Display summary
    print(f"\n{colors['GREEN']}[+]{colors['RESET']} Found {len(scan_data['hosts'])} host(s)")
    for host in scan_data['hosts']:
        if host.get('addresses'):
            ip = host['addresses'][0].get('addr', 'unknown')
            status = host.get('status', {}).get('state', 'unknown')
            port_count = len(host.get('ports', []))
            
            # Count open ports
            open_ports = sum(1 for p in host.get('ports', []) 
                           if p.get('state', {}).get('state') == 'open')
            
            # Get OS info if available
            os_info = ""
            if host.get('os', {}).get('matches'):
                os_info = f" | OS: {host['os']['matches'][0].get('name', 'unknown')}"
            
            print(f"    {colors['CYAN']}-{colors['RESET']} {ip}: {status} | {open_ports}/{port_count} open port(s){os_info}")
            
            # Show open ports summary
            if args.verbose and host.get('ports'):
                for port in host['ports']:
                    if port.get('state', {}).get('state') == 'open':
                        port_num = port.get('port', '')
                        service = port.get('service', {})
                        service_name = service.get('name', 'unknown')
                        product = service.get('product', '')
                        version = service.get('version', '')
                        if product or version:
                            print(f"        {colors['GREEN']}└─{colors['RESET']} Port {port_num}/{port.get('protocol', 'tcp')}: {service_name} {product} {version}".strip())
                        else:
                            print(f"        {colors['GREEN']}└─{colors['RESET']} Port {port_num}/{port.get('protocol', 'tcp')}: {service_name}")
    
    # Save to JSON
    print(f"\n{colors['CYAN']}[*]{colors['RESET']} Exporting results to JSON...")
    output_file = save_json_output(scan_data, args.target)
    
    if output_file:
        print(f"{colors['GREEN']}[+]{colors['RESET']} DISMAP scan completed successfully!")
        print(f"{colors['GREEN']}[+]{colors['RESET']} Results saved to: {output_file}")
    else:
        print(f"{colors['RED']}[!]{colors['RESET']} Warning: Scan completed but failed to save results")
        sys.exit(1)

if __name__ == "__main__":
    main()
