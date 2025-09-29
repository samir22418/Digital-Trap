
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uvicorn
import httpx
import time
import json
import os
import logging
import asyncio
from config import *


os.makedirs(os.path.dirname(ERROR_LOG_FILE), exist_ok=True)
logging.basicConfig(filename=ERROR_LOG_FILE, level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s - %(message)s", encoding="utf-8")

app = FastAPI()
client: httpx.AsyncClient | None = None

WAF_SERVICE_URL = f"http://127.0.0.1:{WAF_PORT}/analyze"
REAL_BACKEND_URL = f"http://127.0.0.1:{PHP_REAL_PORT}"
HONEYPOT_BACKEND_URL = f"http://127.0.0.1:{PHP_HONEY_PORT}"


BAN_LIST = {}  
BAN_DURATION = 60 * 5  

request_counts = {}
RATE_LIMIT = 100
RATE_WINDOW = 60

def is_banned(ip: str) -> bool:
    expiry = BAN_LIST.get(ip)
    if not expiry:
        return False
    if time.time() > expiry:
        BAN_LIST.pop(ip, None)
        return False
    return True

def ban_ip(ip: str, duration: int = None):
    if duration is None:
        duration = BAN_DURATION
    BAN_LIST[ip] = time.time() + duration
    logging.info(f"Banned IP {ip} for {duration}s")

def log_attack(source_ip, request_uri, payload, action):
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source_ip": source_ip,
        "request_uri": request_uri,
        "payload": payload,
        "action": action
    }
    try:
        os.makedirs(os.path.dirname(ATTACK_LOGS_FILE), exist_ok=True)
        with open(ATTACK_LOGS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logging.error(f"Error writing attack log: {e}")

async def _request_with_retries(client_obj, method, url, **kwargs):
    attempts = 3
    backoff = 0.5
    for i in range(attempts):
        try:
            return await client_obj.request(method=method, url=url, **kwargs)
        except (httpx.ConnectError, httpx.ReadTimeout) as e:
            if i == attempts - 1:
                raise
            await asyncio.sleep(backoff * (2 ** i))

async def mirror_to_waf(source_ip: str, req_path: str, method: str, body_bytes: bytes, headers: dict):
    try:
        body_text = body_bytes.decode('utf-8', errors='ignore')
        waf_payload = {"uri": req_path, "method": method, "body": body_text}
        async with httpx.AsyncClient() as mirror_client:
            resp = await mirror_client.post(WAF_SERVICE_URL, json=waf_payload, timeout=WAF_TIMEOUT)
            try:
                data = resp.json()
            except Exception:
                data = {}
            decision = data.get("decision", "CLEAN")
            if decision == "SUSPICIOUS":
                ban_ip(source_ip)
                log_attack(source_ip, req_path, body_text, "Mirrored -> WAF flagged; IP banned")
    except Exception as e:
        logging.error(f"Mirror to WAF error: {e}")

@app.api_route("/{path:path}", methods=["GET","POST","PUT","DELETE","PATCH","HEAD","OPTIONS"])
async def proxy_request(path: str, request: Request):
    source_ip = request.client.host if request.client else "unknown"

    now = time.time()
    if source_ip in request_counts:
        count, start = request_counts[source_ip]
        if now - start < RATE_WINDOW:
            if count >= RATE_LIMIT:
                log_attack(source_ip, request.url.path, "", "Rate Limit Exceeded")
                return JSONResponse({"error":"Rate limit exceeded"}, status_code=429)
            request_counts[source_ip] = (count + 1, start)
        else:
            request_counts[source_ip] = (1, now)
    else:
        request_counts[source_ip] = (1, now)

    body = await request.body()
    headers = dict(request.headers)

    if is_banned(source_ip):
        target = f"{HONEYPOT_BACKEND_URL}/{path}"
        action = "Blocked (banlist) -> Honeypot"
        log_attack(source_ip, request.url.path, "", action)
    else:
        target = f"{REAL_BACKEND_URL}/{path}"

        asyncio.create_task(mirror_to_waf(source_ip, request.url.path, request.method, body, headers))

    forward_headers = {k: v for k, v in headers.items() if k.lower() not in ["host","content-length","transfer-encoding","connection"]}
    forward_headers["Host"] = "localhost"

    try:
        proxy_resp = await _request_with_retries(
            client,
            request.method,
            target,
            headers=forward_headers,
            content=body,
            params=request.query_params,
            timeout=30
        )
        response = Response(content=proxy_resp.content, status_code=proxy_resp.status_code,
                            media_type=proxy_resp.headers.get("Content-Type"))
        for header, value in proxy_resp.headers.items():
            if header.lower() not in ["content-encoding","content-length","transfer-encoding","connection"]:
                response.headers[header] = value
        return response
    except Exception as e:
        err = f"Error forwarding to {target}: {e}"
        logging.error(err)
        return Response(content=err, status_code=503)

@app.on_event("startup")
async def startup_event():
    global client
    client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown_event():
    global client
    if client:
        await client.aclose()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PROXY_PORT)
