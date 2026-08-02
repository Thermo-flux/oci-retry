#!/usr/bin/env python3
"""
setup_oci.py — writes ~/.oci/config and ~/.oci/oci_api_key.pem
from environment variables, then validates the key.
"""
import os, sys, subprocess, hashlib

def main():
    key_raw = os.environ.get('OCI_CLI_KEY_CONTENT', '')
    # Strip quotes, carriage returns (\r), and unescape literal \n
    key = key_raw.strip().strip('"').strip("'")
    key = key.replace('\r', '').replace('\\n', '\n')
    if not key.endswith('\n'):
        key += '\n'

    user      = os.environ.get('OCI_CLI_USER', '').strip().strip('"').strip("'")
    tenancy   = os.environ.get('OCI_CLI_TENANCY', '').strip().strip('"').strip("'")
    secret_fp = os.environ.get('OCI_CLI_FINGERPRINT', '').strip().strip('"').strip("'").lower()
    region    = (os.environ.get('OCI_CLI_REGION', '') or 'ap-hyderabad-1').strip().strip('"').strip("'")

    oci_dir  = os.path.expanduser('~/.oci')
    key_path = os.path.join(oci_dir, 'oci_api_key.pem')
    cfg_path = os.path.join(oci_dir, 'config')

    os.makedirs(oci_dir, exist_ok=True)

    # Write PEM key with clean Linux \n line endings
    with open(key_path, 'wb') as f:
        f.write(key.encode('utf-8'))
    os.chmod(key_path, 0o600)

    # Validate key syntax
    res = subprocess.run(['openssl', 'rsa', '-in', key_path, '-check', '-noout'], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  [!] PEM key syntax error: {res.stderr.strip()}")
        sys.exit(1)

    # Compute key fingerprint
    calc_fp = ""
    try:
        der = subprocess.run(['openssl', 'rsa', '-in', key_path, '-pubout', '-outform', 'DER'], capture_output=True, check=True)
        md5_hex = hashlib.md5(der.stdout).hexdigest()
        calc_fp = ':'.join(md5_hex[i:i+2] for i in range(0, len(md5_hex), 2)).lower()
    except Exception as e:
        print(f"  [!] Fingerprint calculation error: {e}")

    active_fp = secret_fp if secret_fp else calc_fp

    # Write config
    config = f"[DEFAULT]\nuser={user}\nfingerprint={active_fp}\nkey_file={key_path}\ntenancy={tenancy}\nregion={region}\n"
    with open(cfg_path, 'w') as f:
        f.write(config)
    os.chmod(cfg_path, 0o600)

    print("=======================================================")
    print("  OCI Credential Verification Summary")
    print("=======================================================")
    print(f"  [*] Secret Fingerprint:  {secret_fp}")
    print(f"  [*] Derived Fingerprint: {calc_fp}")
    print(f"  [*] Active Fingerprint:  {active_fp}")
    print(f"  [*] Region:              {region}")
    print(f"  [*] User OCID:           {user[:12]}...{user[-8:] if len(user)>20 else user}")
    print(f"  [*] Tenancy OCID:        {tenancy[:12]}...{tenancy[-8:] if len(tenancy)>20 else tenancy}")
    print("=======================================================")

if __name__ == '__main__':
    main()
