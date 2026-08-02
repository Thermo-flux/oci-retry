#!/usr/bin/env python3
"""
setup_oci.py — writes ~/.oci/config and ~/.oci/oci_api_key.pem
from environment variables, then validates the key.
"""
import os, sys, subprocess, hashlib

def main():
    key_raw = os.environ.get('OCI_CLI_KEY_CONTENT', '')
    key = key_raw.strip().strip('"').strip("'")
    key = key.replace('\\n', '\n')
    if not key.endswith('\n'):
        key += '\n'

    user     = os.environ.get('OCI_CLI_USER', '').strip().strip('"').strip("'")
    tenancy  = os.environ.get('OCI_CLI_TENANCY', '').strip().strip('"').strip("'")
    secret_fp= os.environ.get('OCI_CLI_FINGERPRINT', '').strip().strip('"').strip("'")
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
        print("  [*] PEM key syntax: VALID ✓")
    else:
        print(f"  [!] PEM key syntax: INVALID — {result.stderr.strip()}")
        sys.exit(1)

    # Compute true fingerprint from key
    calc_fp = ""
    try:
        der = subprocess.run(
            ['openssl', 'rsa', '-in', key_path, '-pubout', '-outform', 'DER'],
            capture_output=True, check=True
        )
        md5_hex = hashlib.md5(der.stdout).hexdigest()
        calc_fp = ':'.join(md5_hex[i:i+2] for i in range(0, len(md5_hex), 2))
        print(f"  [*] Derived Key Fingerprint: {calc_fp}")
    except Exception as e:
        print(f"  [!] Fingerprint calculation error: {e}")
        sys.exit(1)

    # Use derived fingerprint if secret FP doesn't match or is missing
    active_fp = secret_fp if secret_fp else calc_fp
    if secret_fp and secret_fp.lower() != calc_fp.lower():
        print(f"  [!] Secret FP ({secret_fp}) != Derived FP ({calc_fp}). Using Derived Key FP ({calc_fp}).")
        active_fp = calc_fp

    # Write config
    config = f"[DEFAULT]\nuser={user}\nfingerprint={active_fp}\nkey_file={key_path}\ntenancy={tenancy}\nregion={region}\n"
    with open(cfg_path, 'w') as f:
        f.write(config)
    os.chmod(cfg_path, 0o600)

    print("=" * 55)
    print("  OCI Credentials Configured Successfully")
    print(f"  Region:      {region}")
    print(f"  Fingerprint: {active_fp}")
    print(f"  User:        {user[:15]}...{user[-6:] if len(user)>20 else user}")
    print("=" * 55)

if __name__ == '__main__':
    main()
