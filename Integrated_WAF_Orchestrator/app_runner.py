
import subprocess
import time
import logging
import os
from config import *

logger = logging.getLogger(__name__)
RUN_PROCESSES = []

def _start_process(cmd, cwd=None):
    logger.debug("Starting: %s", " ".join(cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, text=True)
    RUN_PROCESSES.append(p)
    time.sleep(0.3)
    return p

def start_php_server(path, port):
    cmd = [PHP_EXE_PATH, '-S', f'127.0.0.1:{port}', '-t', path]
    return _start_process(cmd, cwd=path)

def start_uvicorn(module_path, port):
    cmd = [PYTHON_EXE, '-m', 'uvicorn', f'{module_path}:app', '--host', '127.0.0.1', '--port', str(port)]
    return _start_process(cmd)

def start_all_services(app_name="app"):
    try:
        os.makedirs(REAL_PATH, exist_ok=True)
        os.makedirs(HONEY_PATH, exist_ok=True)
        start_uvicorn('waf_service', WAF_PORT)
        start_uvicorn('proxy_service', PROXY_PORT)
        start_php_server(REAL_PATH, PHP_REAL_PORT)
        start_php_server(HONEY_PATH, PHP_HONEY_PORT)
        time.sleep(1.0)
        return True
    except Exception as e:
        logger.error("Failed to start services: %s", e)
        return False

def stop_all_processes():
    for p in RUN_PROCESSES:
        try:
            p.terminate()
        except Exception:
            pass
    RUN_PROCESSES.clear()

def get_running_service_statuses():
    statuses = {
        "Python_Proxy": {"status": "Unknown"},
        "WAF_LLM": {"status": "Unknown"},
        "PHP_Real": {"status": "Unknown"},
        "PHP_Honey": {"status": "Unknown"},
    }
    import socket
    def _is_running(port):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.6):
                return True
        except Exception:
            return False

    statuses["Python_Proxy"]["status"] = "Running" if _is_running(PROXY_PORT) else "Stopped"
    statuses["WAF_LLM"]["status"] = "Running" if _is_running(WAF_PORT) else "Stopped"
    statuses["PHP_Real"]["status"] = "Running" if _is_running(PHP_REAL_PORT) else "Stopped"
    statuses["PHP_Honey"]["status"] = "Running" if _is_running(PHP_HONEY_PORT) else "Stopped"
    return statuses
