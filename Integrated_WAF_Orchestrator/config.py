import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


USER_DATA_DIR = os.path.join(BASE_DIR, "user_data")
REAL_PATH = os.path.join(BASE_DIR, "real_app")
HONEY_PATH = os.path.join(BASE_DIR, "honey_app")
TARGET_TEMPLATES = os.path.join(BASE_DIR, "target_app_templates")

LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)


PHP_EXE_PATH = r"C:\php\php.exe"           
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


PYTHON_EXE = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")


PROXY_PORT = 8081
WAF_PORT = 8000
PHP_REAL_PORT = 8082
PHP_HONEY_PORT = 8083


WAF_TIMEOUT = 5.0  


ERROR_LOG_FILE = os.path.join(LOGS_DIR, "error.log")
ATTACK_LOGS_FILE = os.path.join(LOGS_DIR, "attack_logs.jsonl")


HONEYPOT_LOGIC_PATH = os.path.join(TARGET_TEMPLATES, "honeypot_logic.php")

LLM_MODEL_DIR = r"C:\Users\fayrouz\Desktop\waf\waf\fine_tuned_model"
MAX_LOG_SIZE = 10 * 1024 * 1024
