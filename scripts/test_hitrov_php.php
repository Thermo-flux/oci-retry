<?php
$keyPath = $_SERVER['HOME'] . '/.oci/oci_api_key.pem';
if (!file_exists($keyPath)) {
    echo "[!] Key file does not exist: $keyPath\n";
    exit(1);
}
$content = file_get_contents($keyPath);
echo "[*] Key file size: " . strlen($content) . " bytes\n";
$res = openssl_pkey_get_private($content);
if ($res === false) {
    echo "[!] openssl_pkey_get_private FAILED! Error:\n";
    while ($msg = openssl_error_string()) {
        echo "  - $msg\n";
    }
} else {
    echo "[*] openssl_pkey_get_private SUCCESS!\n";
    $details = openssl_pkey_get_details($res);
    echo "  - Key bits: " . $details['bits'] . "\n";
    echo "  - Key type: " . $details['type'] . "\n";
}
