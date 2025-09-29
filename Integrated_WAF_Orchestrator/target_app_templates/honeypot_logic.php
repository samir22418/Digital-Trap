<?php
$log_path = 'ATTACK_LOGS_FILE_PATH'; 
$entry = array(
    "timestamp" => date("Y-m-d H:i:s"),
    "source_ip" => $_SERVER['REMOTE_ADDR'] ?? "unknown",
    "request_uri" => $_SERVER['REQUEST_URI'] ?? "",
    "payload" => json_encode(array("GET" => $_GET, "POST" => $_POST)),
    "action" => "honeypot_interaction"
);
$line = json_encode($entry, JSON_UNESCAPED_UNICODE) . PHP_EOL;
file_put_contents($log_path, $line, FILE_APPEND | LOCK_EX);
?>
