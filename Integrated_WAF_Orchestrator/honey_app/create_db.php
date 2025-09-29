// create_db.php (Modified for SQLite)
<?php

$db_file = 'vulnerable_db.sqlite';

try {

    $pdo = new PDO("sqlite:$db_file");
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    $pdo->exec("
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(100)
        )
    ");

    $pdo->exec("
        INSERT OR IGNORE INTO users (username, password, email) VALUES
        ('admin', 'admin123', 'admin@digitaltrap.com'),
        ('user1', 'pass1', 'user1@digitaltrap.com'),
        ('user2', 'pass2', 'user2@digitaltrap.com')
    ");

    echo "SQLite database file '$db_file' and table created successfully. Sample users added.";

} catch (PDOException $e) {
    die("Database setup failed: " . $e->getMessage());
}
?>