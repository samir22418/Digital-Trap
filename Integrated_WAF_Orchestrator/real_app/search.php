<?php
error_reporting(0);
session_start();
include 'config.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Results - Digital Trap</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }
        header {
            background-color: #A376A2;
            color: white;
            padding: 10px;
            text-align: center;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .session-info {
            background-color: #e8e8e8;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .output {
            background-color: #f9f9f9;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 3px;
            margin-top: 10px;
            white-space: pre-wrap;
        }
        a {
            color: #A376A2;
            text-decoration: none;
            display: inline-block;
            padding: 10px 15px;
            background: white;
            border-radius: 3px;
            margin-top: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        a:hover {
            text-decoration: underline;
        }
        .error {
            background-color: #ffe6e6;
            border: 1px solid #ff9999;
            color: #cc0000;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            background: white;
            margin: 5px 0;
            padding: 10px;
            border-radius: 3px;
            border-left: 4px solid #A376A2;
        }
    </style>
</head>
<body>
    <header>
        <h1>Digital Trap Testing App</h1>
        <p>SQL Injection Test Results</p>
    </header>

    <div class="session-info">
        <strong>Session ID:</strong> <?php echo session_id(); ?><br>
        <strong>User ID:</strong> <?php echo $_SESSION['user_id']; ?>
    </div>

<?php
$search = '';
$results = [];
$sql_error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['search'])) {
    $search = $_POST['search'];
    
    try {
        $search_escaped = str_replace("'", "''", $search); 
        $like_pattern = '%' . $search_escaped . '%';
        $sql = "SELECT * FROM users WHERE username LIKE '$like_pattern' OR email LIKE '$like_pattern'";
        echo "<!-- DEBUG SQL: $sql -->";
        
        $stmt = $pdo->query($sql);
        $results = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
    } catch (PDOException $e) {
        $sql_error = "SQL Error: " . $e->getMessage();
        echo "<!-- DEBUG ERROR: " . $e->getMessage() . " -->";
    }
}
?>

    <div class="output <?php echo $sql_error ? 'error' : ''; ?>">
        <?php if ($search): ?>
            <h3>🔍 Search Query: <code><?php echo htmlspecialchars($search); ?></code></h3>
            <p><strong>Generated SQL:</strong> <code><?php 
                $like_pattern = '%' . str_replace("'", "''", $search) . '%';
                echo htmlspecialchars("SELECT * FROM users WHERE username LIKE '$like_pattern' OR email LIKE '$like_pattern'");
            ?></code></p>
            
            <?php if ($sql_error): ?>
                <h4>❌ SQL Error (This is expected for some payloads):</h4>
                <pre><?php echo htmlspecialchars($sql_error); ?></pre>
                <p><em>Note: SQL errors are normal for injection testing - your WAF should catch the malicious input!</em></p>
            <?php elseif ($results): ?>
                <h4>✅ Results Found (<?php echo count($results); ?> users):</h4>
                <ul>
                    <?php foreach ($results as $row): ?>
                        <li>
                            <strong>ID:</strong> <?php echo $row['id']; ?> | 
                            <strong>Username:</strong> <?php echo htmlspecialchars($row['username']); ?> | 
                            <strong>Email:</strong> <?php echo htmlspecialchars($row['email']); ?><br>
                            <small>Password Hash: <?php echo htmlspecialchars(substr($row['password'], 0, 10)) . '...'; ?></small>
                        </li>
                    <?php endforeach; ?>
                </ul>
            <?php else: ?>
                <h4>📭 No results found</h4>
                <p>This search didn't match any users.</p>
            <?php endif; ?>
        <?php else: ?>
            <h3>No search performed</h3>
            <p>Enter a search term above to test SQL injection.</p>
        <?php endif; ?>
    </div>

    <div style="margin-top: 20px;">
        <h4>🧪 Test Payloads (Copy & Paste):</h4>
        <div style="background: #f0f0f0; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px;">
            <strong>Basic SQLi:</strong> <code>' OR 1=1 --</code><br>
            <strong>Union Attack:</strong> <code>' UNION SELECT 1,2,3,4 --</code><br>
            <strong>Bypass Auth:</strong> <code>admin' --</code><br>
            <strong>Error-based:</strong> <code>'; SELECT @@version --</code>
        </div>
    </div>

    <a href='index.php'>🏠 Back to Home</a>
</body>
</html>