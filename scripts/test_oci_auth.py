#!/usr/bin/env python3
"""
test_oci_auth.py — test OCI API signature and report exact error response
"""
import os, sys, requests, datetime, base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def main():
    user = os.environ.get('OCI_CLI_USER', '').strip()
    tenancy = os.environ.get('OCI_CLI_TENANCY', '').strip()
    fingerprint = os.environ.get('OCI_CLI_FINGERPRINT', '').strip()
    region = os.environ.get('OCI_CLI_REGION', 'ap-hyderabad-1').strip()
    key_content = os.environ.get('OCI_CLI_KEY_CONTENT', '').strip()

    key_content = key_content.replace('\r', '').replace('\\n', '\n')
    if not key_content.endswith('\n'): key_content += '\n'

    private_key = serialization.load_pem_private_key(key_content.encode('utf-8'), password=None)

    host = f"iaas.{region}.oraclecloud.com"
    target = f"/20160918/users/{user}"
    url = f"https://{host}{target}"

    date_str = datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

    signing_string = f"(request-target): get {target}\ndate: {date_str}\nhost: {host}"

    signature_bytes = private_key.sign(
        signing_string.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')

    key_id = f"{tenancy}/{user}/{fingerprint}"
    auth_header = f'Signature version="1",keyId="{key_id}",algorithm="rsa-sha256",headers="(request-target) date host",signature="{signature_b64}"'

    headers = {
        'date': date_str,
        'host': host,
        'authorization': auth_header,
        'accept': 'application/json'
    }

    print("=======================================================")
    print("  Testing OCI Direct API Authentication")
    print(f"  URL: {url}")
    print(f"  Key ID: {key_id}")
    print("=======================================================")

    resp = requests.get(url, headers=headers)
    print(f"  HTTP Status Code: {resp.status_code}")
    print(f"  Response Body: {resp.text}")
    print("=======================================================")

if __name__ == '__main__':
    main()
