<?php
function get_client_ip() {
    $ipaddress = '';
    if (isset($_SERVER['HTTP_CLIENT_IP']))
        $ipaddress = $_SERVER['HTTP_CLIENT_IP'];
    else if(isset($_SERVER['HTTP_X_FORWARDED_FOR']))
        $ipaddress = $_SERVER['HTTP_X_FORWARDED_FOR'];
    else if(isset($_SERVER['HTTP_X_FORWARDED']))
        $ipaddress = $_SERVER['HTTP_X_FORWARDED'];
    else if(isset($_SERVER['HTTP_FORWARDED_FOR']))
        $ipaddress = $_SERVER['HTTP_FORWARDED_FOR'];
    else if(isset($_SERVER['HTTP_FORWARDED']))
        $ipaddress = $_SERVER['HTTP_FORWARDED'];
    else if(isset($_SERVER['REMOTE_ADDR']))
        $ipaddress = $_SERVER['REMOTE_ADDR'];
    else
        $ipaddress = 'UNKNOWN';
    return $ipaddress;
}


$attack_logs_file = __DIR__ . '/../../user_data/attack_logs.json'; 


$log_entry = [
    'timestamp' => date('Y-m-%d %H:%M:%S'),
    'source_ip' => get_client_ip(),
    'request_uri' => $_SERVER['REQUEST_URI'] ?? '/',
    'method' => $_SERVER['REQUEST_METHOD'] ?? 'GET',
    'payload' => file_get_contents('php://input'), 
    'get_params' => $_GET,
    'post_params' => $_POST,
    'action' => 'Honeypot Accessed'
];

if (file_put_contents($attack_logs_file, json_encode($log_entry, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . "\n", FILE_APPEND | LOCK_EX) === false) {
    error_log("Failed to write to attack log file: " . $attack_logs_file);
}

?>
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>صفحة خطأ (Honeypot)</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a1a;
            color: #e0e0e0;
            text-align: center;
            padding: 50px;
            direction: rtl;
        }
        .container {
            background-color: #333;
            border: 1px solid #ff0000;
            border-radius: 8px;
            padding: 30px;
            margin: 0 auto;
            max-width: 600px;
            box-shadow: 0 0 15px rgba(255, 0, 0, 0.5);
        }
        h1 {
            color: #ff4d4d;
        }
        p {
            font-size: 1.1em;
            line-height: 1.6;
        }
        .small-text {
            font-size: 0.8em;
            color: #aaaaaa;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>خطأ: الصفحة المطلوبة غير متوفرة!</h1>
        <p>عذرًا، يبدو أن هناك مشكلة في معالجة طلبك أو أن الصفحة التي تبحث عنها غير موجودة.</p>
        <p>يرجى العودة إلى الصفحة الرئيسية أو الاتصال بالدعم الفني إذا استمرت المشكلة.</p>
        <div class="small-text">
            تم تسجيل هذه المحاولة لأغراض التدقيق الأمني.
            <br>
            معرف الطلب: <?php echo uniqid(); ?>
        </div>
    </div>
</body>
</html>
<?php

exit(); 
?>
<?php
session_start();


if (!isset($_SESSION['user_id'])) {
    $_SESSION['user_id'] = uniqid('digitaltrap_', true);
}

include 'config.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Trap Vulnerable App</title>
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
        h1 {
            margin: 0;
        }
        .session-info {
            background-color: #e8e8e8;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        form {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], input[type="file"], textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 3px;
            box-sizing: border-box;
        }
        button {
            background-color: #A376A2;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        button:hover {
            background-color: #8e5e8e;
        }
        .output {
            background-color: #f9f9f9;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 3px;
            margin-top: 10px;
        }
        .vuln-section {
            border-left: 4px solid #A376A2;
            padding-left: 10px;
        }
        footer {
            text-align: center;
            margin-top: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <header>
        <h1>Digital Trap Testing App</h1>
        <p>Vulnerable Web App for WAF Testing</p>
    </header>

    <div class="session-info">
        <strong>Session ID:</strong> <?php echo session_id(); ?><br>
        <strong>User ID:</strong> <?php echo $_SESSION['user_id']; ?>
    </div>

    <div class="vuln-section">
        <h2>SQL Search (Vulnerable to Injection)</h2>
        <form action="search.php" method="POST">
            <label for="sql_search">Search Users:</label>
            <input type="text" id="sql_search" name="search" placeholder="Enter search term" required>
            <button type="submit">Search</button>
        </form>
    </div>

    <div class="vuln-section">
        <h2>XSS Comment (Vulnerable to Script Injection)</h2>
        <form action="comment.php" method="POST">
            <label for="xss_comment">Post a Comment:</label>
            <textarea id="xss_comment" name="comment" rows="4" placeholder="Enter your comment"></textarea>
            <button type="submit">Post</button>
        </form>
    </div>

    <div class="vuln-section">
        <h2>File Viewer (Vulnerable to Path Traversal)</h2>
        <form action="file.php" method="GET">
            <label for="file_path">File Path:</label>
            <input type="text" id="file_path" name="file" placeholder="Enter file path (e.g., test.txt)" required>
            <button type="submit">View File</button>
        </form>
        <p><em>Note: Try relative paths like ../../etc/passwd</em></p>
    </div>

    <footer>
        <p>&copy; 2025 Digital Trap</p>
    </footer>
</body>
</html>