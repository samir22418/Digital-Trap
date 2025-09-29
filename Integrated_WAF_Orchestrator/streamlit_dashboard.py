import streamlit as st
import os, json, time, socket, httpx
from datetime import datetime
import pandas as pd
from config import *
import app_runner

st.set_page_config(page_title="لوحة حماية المنصة", layout="wide", initial_sidebar_state="expanded")
st.title("🛡️ لوحة حماية المنصة — WAF")
os.makedirs(os.path.dirname(ERROR_LOG_FILE), exist_ok=True)
LOGS_FILE = ATTACK_LOGS_FILE
BANLIST_FILE = os.path.join(os.path.dirname(LOGS_FILE), "banlist.json")

def port_open(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.3):
            return True
    except:
        return False

def read_logs(limit=None):
    if not os.path.exists(LOGS_FILE):
        return []
    out = []
    try:
        with open(LOGS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if limit:
                lines = lines[-limit:]
            for L in lines:
                L = L.strip()
                if not L:
                    continue
                try:
                    out.append(json.loads(L))
                except:
                    out.append({"timestamp": "", "raw": L})
    except Exception as e:
        st.error(f"خطأ عند قراءة ملف السجلات: {e}")
    return out

def load_banlist():
    if os.path.exists(BANLIST_FILE):
        try:
            with open(BANLIST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_banlist(b):
    try:
        with open(BANLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(b, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"فشل حفظ قائمة الحظر: {e}")

def human_ts(ts=None):
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") if ts is None else datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

def waf_health():
    try:
        resp = httpx.get(f"http://127.0.0.1:{WAF_PORT}/health", timeout=1.0)
        return (resp.status_code==200, {}) if resp.status_code==200 else (False, {"status_code": resp.status_code})
    except:
        return False, {}
with st.sidebar:
    st.header("⚡ تحكم سريع")
    if st.button("▶️ شغل كل الخدمات"):
        ok = app_runner.start_all_services()
        st.success("تمام يا مستر، حاولنا نشغل الخدمات 😎" if ok else "حصلت مشكلة في التشغيل!")
    if st.button("⏹️ وقف كل الخدمات"):
        app_runner.stop_all_processes()
        st.warning("وقفنا كل الخدمات، خلي بالك يا مستر.")

    st.markdown("---")
    st.subheader("حظر IP")
    banlist = load_banlist()
    new_ip = st.text_input("أدخل IP للحظر:")
    minutes = st.number_input("مدة الحظر بالدقايق", min_value=1, max_value=1440, value=5)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("حظر دلوقتي"):
            if new_ip:
                until = time.time() + minutes*60
                banlist[new_ip] = {"until": until, "reason": "manual", "ts": human_ts()}
                save_banlist(banlist)
                st.success(f"تم حظر {new_ip} لحد {human_ts(until)}")
            else:
                st.error("ادخل IP صحيح يا مستر.")
    with c2:
        if st.button("إلغاء الحظر"):
            if new_ip and new_ip in banlist:
                banlist.pop(new_ip, None)
                save_banlist(banlist)
                st.success(f"تم إلغاء الحظر لـ {new_ip}")
            else:
                st.info("IP مش موجود في القائمة.")

    st.markdown("---")
    auto_refresh = st.checkbox("تحديث تلقائي (5 ثواني)", value=False)


st.markdown("## حالة الخدمات 🔎")
cols = st.columns(4)
cols[0].metric("البروكسي", "شغال" if port_open(PROXY_PORT) else "مقفول")
cols[1].metric("WAF", "شغال" if waf_health()[0] else "مش شغال")
cols[2].metric("التطبيق الحقيقي", "شغال" if port_open(PHP_REAL_PORT) else "مش شغال")
cols[3].metric("Honeypot", "شغال" if port_open(PHP_HONEY_PORT) else "مش شغال")

st.markdown("---")


st.markdown("## السجلات الأخيرة 📜")
logs = read_logs(limit=500)
df = pd.DataFrame(logs) if logs else pd.DataFrame()
if not df.empty:
    st.dataframe(df[["timestamp","source_ip","request_uri","action"]].sort_values(by="timestamp", ascending=False), use_container_width=True)
else:
    st.info("لسه مفيش هجمات يا مستر 😎")


st.markdown("---")
st.markdown("## قائمة الحظر")
banlist = load_banlist()
now_ts = time.time()
expired = [ip for ip,v in banlist.items() if v.get("until",0) < now_ts]
for ip in expired: banlist.pop(ip)
save_banlist(banlist)

if banlist:
    st.table(pd.DataFrame([{"IP":ip,"لحد":human_ts(v["until"]),"سبب":v["reason"]} for ip,v in banlist.items()]))
else:
    st.info("قائمة الحظر فاضية يا مستر 😎")


if "last_log_count" not in st.session_state:
    st.session_state.last_log_count = len(df)
current_count = len(df)
if current_count > st.session_state.last_log_count:
    st.success(f"🚨 {current_count - st.session_state.last_log_count} هجمات جديدة اتسجلت!")
st.session_state.last_log_count = current_count


st.markdown("---")
if st.button("🧾 فرغ السجلات (خلي نسخة احتياطية)"):
    if os.path.exists(LOGS_FILE):
        backup = LOGS_FILE + ".backup." + datetime.now().strftime("%Y%m%d%H%M%S")
        os.rename(LOGS_FILE, backup)
        st.success(f"تم التفريغ. النسخة الاحتياطية: {backup}")
    else:
        st.info("مفيش سجلات لتفريغها 😎")


if auto_refresh:
    time.sleep(5)
    st.experimental_rerun()

st.caption(f"آخر تحديث: {human_ts()}")


