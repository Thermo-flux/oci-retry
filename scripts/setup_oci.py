#!/usr/bin/env python3
"""
setup_oci.py — writes ~/.oci/config and ~/.oci/oci_api_key.pem
from environment variables, then validates the key.
"""
import os, sys, subprocess, hashlib

def main():
    key_raw = os.environ.get('OCI_CLI_KEY_CONTENT', '')
    # Handle both literal \n and actual newlines
    key = key_raw.strip().strip('"').strip("'")
    key = key.replace('\\n', '\n')
    if not key.endswith('\n'):
        key += '\n'

    user     = os.environ.get('OCI_CLI_USER', '').strip().strip('"').strip("'")
    tenancy  = os.environ.get('OCI_CLI_TENANCY', '').strip().strip('"').strip("'")
    fp       = os.environ.get('OCI_CLI_FINGERPRINT', '').strip().strip('"').strip("'")
    region   = (os.environ.get('OCI_CLI_REGION', '') or 'ap-hyderabad-1').strip().strip('"').strip("'")

    oci_dir  = os.path.expanduser('~/.oci')
    key_path = os.path.join(oci_dir, 'oci_api_key.pem')
    cfg_path = os.path.join(oci_dir, 'config')

    os.makedirs(oci_dir, exist_ok=True)

    # Write PEM key
    with open(key_path, 'w') as f:
        f.write(key)
    os.chmod(key_path, 0o600)
    print(f"  [*] PEM key written: {len(key)} bytes")

    # Validate key with openssl
    result = subprocess.run(
        ['openssl', 'rsa', '-in', key_path, '-check', '-noout'],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  [*] PEM key: VALID ✓")
    else:
        print(f"  [!] PEM key: INVALID — {result.stderr.strip()}")
        print("  [!] Check your OCI_CLI_KEY_CONTENT GitHub secret!")
        sys.exit(1)

    # Compute fingerprint from key to verify it matches
    try:
        der = subprocess.run(
            ['openssl', 'rsa', '-in', key_path, '-pubout', '-outform', 'DER'],
            capture_output=True, check=True
        )
        md5_hex = hashlib.md5(der.stdout).hexdigest()
        calc_fp = ':'.join(md5_hex[i:i+2] for i in range(0, len(md5_hex), 2))
        if calc_fp.lower() == fp.lower():
            print(f"  [*] Fingerprint match: {fp} ✓")
        else:
            print(f"  [!] Fingerprint MISMATCH!")
            print(f"      Secret FP : {fp}")
            print(f"      Key FP    : {calc_fp}")
            print("  [!] Update OCI_CLI_FINGERPRINT or OCI_CLI_KEY_CONTENT secret!")
            sys.exit(1)
    except Exception as e:
        print(f"  [!] Fingerprint check error: {e}")
        sys.exit(1)

    # Write config
    config = f"[DEFAULT]\nuser={user}\nfingerprint={fp}\nkey_file={key_path}\ntenancy={tenancy}\nregion={region}\n"
    with open(cfg_path, 'w') as f:
        f.write(config)
    os.chmod(cfg_path, 0o600)

    print("=" * 55)
    print("  OCI Credentials configured successfully")
    print(f"  Region:      {region}")
    print(f"  Fingerprint: {fp}")
    print(f"  User:        {user[:20]}...{user[-6:]}")
    print("=" * 55)

if __name__ == '__main__':
    main()
