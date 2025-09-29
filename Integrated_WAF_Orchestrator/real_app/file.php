<?php
session_start();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Viewer - Digital Trap</title>
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
        .output {
            background-color: #f9f9f9;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 3px;
            margin-top: 10px;
        }
        pre {
            background: white;
            padding: 10px;
            border: 1px solid #ddd;
            overflow: auto;
        }
        a {
            color: #A376A2;
            text-decoration: none;
            display: inline-block;
            padding: 10px;
            background: white;
            border-radius: 3px;
            margin-top: 10px;
        }
        a:hover {
            text-decoration: underline;
        }
        .session-info {
            background-color: #e8e8e8;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <header>
        <h1>Digital Trap Testing App</h1>
    </header>

    <div class="session-info">
        <strong>Session ID:</strong> <?php echo session_id(); ?><br>
        <strong>User ID:</strong> <?php echo $_SESSION['user_id']; ?>
    </div>

<?php
if (isset($_GET['file'])) {
    $file = $_GET['file'];

    echo "<div class='output'>";
    echo "<h3>File: " . htmlspecialchars($file) . "</h3>";
    
    if (file_exists($file)) {
        echo "<pre>";

        readfile($file);
        echo "</pre>";
    } else {
        echo "<p>File not found.</p>";
    }
    echo "</div>";
} else {
    echo "<div class='output'><p>No file specified.</p></div>";
}
?>

    <a href='index.php'>Back to Home</a>
</body>
</html>