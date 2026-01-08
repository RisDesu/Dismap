import argparse

def banner():
    print("""
    =========================
        DISMAP v0.1
    =========================
    """)

def main():
    parser = argparse.ArgumentParser(description="DISMAP - Information Mapping Tool")
    parser.add_argument("-t", "--target", required=True, help="Target IP or Domain")
    args = parser.parse_args()

    banner()
    print(f"[+] Target: {args.target}")
    print("[*] DISMAP is ready!")

if __name__ == "__main__":
    main()
