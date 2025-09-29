<?php
$db_file = 'vulnerable_db.sqlite'; 
$pdo = null; 

try {
    $pdo = new PDO("sqlite:$db_file");
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->exec("PRAGMA foreign_keys = ON;"); 
} catch(PDOException $e) {

    die("Connection failed: " . $e->getMessage());
}
?>