<?php
declare(strict_types=1);

header('Content-Type: text/plain; charset=utf-8');

echo "=======================================================\n";
echo " Executing Hitrov OCI Capacity Check on Google Cloud\n";
echo " Time: " . date('Y-m-d H:i:s UTC') . "\n";
echo "=======================================================\n\n";

// Configure credentials file ~/.oci/oci_api_key.pem
exec('python3 /app/scripts/setup_oci.py 2>&1', $cfgOutput, $cfgExit);
echo implode("\n", $cfgOutput) . "\n\n";

// Run Hitrov script
chdir('/app/hitrov-app');
exec('php index.php 2>&1', $runOutput, $runExit);
echo implode("\n", $runOutput) . "\n";

echo "\n=======================================================\n";
echo " Execution Completed (Exit Code: $runExit)\n";
echo "=======================================================\n";
