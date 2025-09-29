<?php

$host = 'localhost';
$username = 'root';
$password = '';

$pdo = new PDO("mysql:host=$host", $username, $password);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);


$pdo->exec("CREATE DATABASE IF NOT EXISTS vulnerable_db");
$pdo->exec("USE vulnerable_db");


$pdo->exec("
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(100)
    )
");


$pdo->exec("
    INSERT IGNORE INTO users (username, password, email) VALUES
    ('admin', 'admin123', 'admin@digitaltrap.com'),
    ('user1', 'pass1', 'user1@digitaltrap.com'),
    ('user2', 'pass2', 'user2@digitaltrap.com')
");

echo "Database and table created successfully. Sample users added.";
?>