
import streamlit as st
import time
import json
import zipfile
import shutil
import os
import sys
import pandas as pd
import numpy as np 
import subprocess 

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

try:
    import app_runner
except ImportError:
    st.error("خطأ فادح: لم يتم العثور على ملف app_runner.py. تأكد من وجوده في المجلد الرئيسي.")
    sys.exit(1)


USER_DATA_DIR = os.path.join(PROJECT_ROOT, "user_data")
ATTACK_LOGS_FILE = os.path.join(USER_DATA_DIR, 'attack_logs.json')
HONEYPOT_LOGIC_PATH = os.path.join(PROJECT_ROOT, r"target_app_templates\honeypot_logic.php")


app_runner.USER_DATA_DIR = USER_DATA_DIR
app_runner.REAL_PATH = os.path.join(USER_DATA_DIR, 'real_backend')
app_runner.HONEY_PATH = os.path.join(USER_DATA_DIR, 'honeypot_backend')
def prepare_application_folders(uploaded_file):
    """ تنظيف، استخراج، مضاعفة التطبيق، وحقن كود Honeypot. """
    
    if os.path.exists(USER_DATA_DIR):
        try: shutil.rmtree(USER_DATA_DIR)
        except PermissionError:
            st.error("خطأ: لا يمكن إزالة الملفات القديمة. أوقف جميع الخدمات أولاً.")
            return False

    os.makedirs(USER_DATA_DIR, exist_ok=True)
    temp_extract_path = os.path.join(USER_DATA_DIR, 'source_app')
    os.makedirs(temp_extract_path)
    
    zip_path = os.path.join(USER_DATA_DIR, uploaded_file.name)
    with open(zip_path, "wb") as f: f.write(uploaded_file.getbuffer())

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_path)
    except Exception as e:
        st.error(f"خطأ في استخراج الملف المضغوط: {e}")
        return False
    
    app_source_dir = temp_extract_path
    contents = os.listdir(temp_extract_path)
    if len(contents) == 1 and os.path.isdir(os.path.join(temp_extract_path, contents[0])):
        app_source_dir = os.path.join(temp_extract_path, contents[0])

    shutil.copytree(app_source_dir, app_runner.REAL_PATH)
    shutil.copytree(app_source_dir, app_runner.HONEY_PATH)
    
    entry_file = os.path.join(app_runner.HONEY_PATH, 'index.php')
    
    if os.path.exists(entry_file):
        try:

            with open(HONEYPOT_LOGIC_PATH, 'r', encoding='utf-8') as h_logic:
                honeypot_code = h_logic.read()

            with open(entry_file, 'r', encoding='utf-8') as f: 
                original_content = f.read()

            with open(entry_file, 'w', encoding='utf-8') as f: 
                f.write(honeypot_code.rstrip() + "\n" + original_content)           
            with open(ATTACK_LOGS_FILE, 'w') as f: # Initialize logs
                pass    
        except Exception as e:
            st.error(f"خطأ في حقن كود Honeypot: {e}")
            return False

    return True

def get_attack_data():
    """ يقرأ بيانات الهجوم من ملف attack_logs.json. """
    if not os.path.exists(ATTACK_LOGS_FILE): return []
    attacks = []
    try:
        with open(ATTACK_LOGS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try: attacks.append(json.loads(line))
                    except json.JSONDecodeError: continue
    except Exception: return []
    return attacks

def calculate_metrics(attacks):
    """ يحسب مؤشرات الأداء الرئيسية (KPIs) وتصنيفات الهجوم. """
    total_attacks = len(attacks)
    time_threshold = time.time() - (5 * 60)
    recent_attacks_count = sum(1 for a in attacks if time.mktime(time.strptime(a.get('timestamp', '2000-01-01 00:00:00'), "%Y-%m-%d %H:%M:%S")) > time_threshold)
    intensity = recent_attacks_count / 5 if recent_attacks_count > 0 else 0
    
    type_counts = {}
    for a in attacks:
        payload = a.get('payload', '') + a.get('request_uri', '')
        if 'SELECT' in payload.upper() or 'UNION' in payload.upper(): attack_type = "SQLi محتمل"
        elif '<SCRIPT' in payload.upper() or 'ALERT(' in payload.upper(): attack_type = "XSS محتمل"
        elif 'ETC/PASSWD' in payload.upper(): attack_type = "تجاوز مسار"
        else: attack_type = "فحص عام"
        type_counts[attack_type] = type_counts.get(attack_type, 0) + 1
    return total_attacks, intensity, type_counts

def display_service_status(statuses):
    """ يعرض حالة الخدمات في جدول بسيط. """
    st.subheader("حالة الخدمات الحالية")
    display_names = {
        "Python_Proxy": "الوكيل العكسي (8080)",
        "WAF_LLM": "جدار الحماية (8000)",
        "PHP_Real": "الخلفية الأساسية (8082)",
        "PHP_Honey": "بيئة الخداع (8081)",
    }
    data = []
    for name, data_item in statuses.items():
        status_text = "🟢 يعمل" if data_item.get('status') == 'Running' else "🔴 متوقف"
        data.append({"الخدمة": display_names.get(name, name), "الحالة": status_text})
    
    df = pd.DataFrame(data)
    st.dataframe(df, width='stretch', hide_index=True) 




def main():
    st.markdown("""
        <style>
            /* Custom styling and RTL support */
            .st-emotion-cache-18ni4b5 { text-align: right; }
            section.main { direction: rtl; }
            .st-emotion-cache-12fmw1z { text-align: right; }
            .stButton>button { width: 100%; margin-top: 10px;}
            .st-emotion-cache-10trblm { visibility: hidden;}
            .metric-card { background-color: #1A1A2E; padding: 15px; border-radius: 10px; border-left: 5px solid #00CC99; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.5); text-align: right; }
            .metric-value { font-size: 2.5rem; font-weight: bold; color: #00CC99; margin-top: 5px; }
            .metric-label { color: #A0A0A0; font-size: 1rem; }
            .status-running { color: #00CC99; font-weight: bold; }
            .status-stopped { color: #FF4B4B; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)
    st.set_page_config(page_title="لوحة تحكم WAF", layout="wide")
    if 'app_deployed' not in st.session_state: st.session_state.app_deployed = False
    if 'app_name' not in st.session_state: st.session_state.app_name = "غير مُحمَّل"

    st.title("🛡️ لوحة تحكم نظام جدار الحماية المتكامل")

    # 3. Data Loading
    attack_events = get_attack_data()
    total_attacks, intensity, attack_types = calculate_metrics(attack_events)
    service_statuses = app_runner.get_running_service_statuses() 

    # 4. KPI Rendering
    kpi_cols = st.columns(3)
    def render_html_metric(col, label, value, unit="", color="#00CC99"):
        col.markdown(f"""<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value" style="color: {color};">{value}{unit}</div></div>""", unsafe_allow_html=True)

    with kpi_cols[2]: render_html_metric(kpi_cols[2], "إجمالي الهجمات المسجلة", total_attacks)
    with kpi_cols[1]: render_html_metric(kpi_cols[1], "شدة الهجوم (آخر 5 د)", f"{intensity:.1f}", "/دقيقة", color="#FFC107")
    with kpi_cols[0]: render_html_metric(kpi_cols[0], "التطبيق الحالي", st.session_state.app_name, color="#17A2B8")
    
    st.markdown("---")

    # 5. Layout and Control
    sidebar_col, main_col = st.columns([0.3, 0.7]) 

    with sidebar_col:
        st.header("🚀 إدارة ونشر التطبيق")

        # Deploy Section
        with st.expander("تجهيز التطبيق (ZIP)", expanded=True):
            uploaded_file = st.file_uploader("حمّل ملف التطبيق (ZIP)", type="zip", key="app_uploader")

            if uploaded_file and not st.session_state.app_deployed:
                if st.button("تجهيز وحقن كود الخداع", width='stretch'):
                    with st.spinner('جارٍ تجهيز الملفات...'):
                        if prepare_application_folders(uploaded_file):
                            st.session_state.app_name = uploaded_file.name
                            st.session_state.app_deployed = True
                            st.success(f"✅ تم تجهيز '{st.session_state.app_name}' بنجاح!")
        
        # Control Section
        st.markdown("---")
        if st.session_state.app_deployed:
            if st.button("🚀 بدء تشغيل جميع الخدمات", key="start_btn", type="primary"):
                st.info("بدء التشغيل... (انتظر 5 ثوانٍ لتحميل LLM)")
                if app_runner.start_all_services(st.session_state.app_name):
                    st.success("✅ النظام يعمل! الوصول عبر: [http://localhost:8080](http://localhost:8080)")
            
            if st.button("🛑 إيقاف جميع الخدمات", key="stop_btn"):
                app_runner.stop_all_processes()
                st.warning("تم إيقاف جميع الخدمات.")
        
        st.markdown("---")
        display_service_status(service_statuses)

    with main_col:
        st.header("📝 تحليل الهجوم والسجلات المباشرة")
        
        # Attack Logs/Analysis
        if total_attacks > 0:
            st.subheader("إجمالي تصنيفات الهجمات")
            df_types = pd.DataFrame(list(attack_types.items()), columns=['نوع الهجوم', 'العدد'])
            st.dataframe(df_types, width='stretch', hide_index=True)
            
            st.markdown("---")

            st.subheader(f"آخر {min(10, total_attacks)} محاولات هجوم مسجلة")
            df_logs = pd.DataFrame(attack_events)
            df_logs = df_logs.sort_values(by='timestamp', ascending=False)
            df_display = df_logs.head(10)[['timestamp', 'source_ip', 'request_uri', 'action']].copy()
            df_display.columns = ['التاريخ والوقت', 'الآي بي المصدر', 'المسار المطلوب', 'الإجراء']
            
            st.dataframe(df_display, width='stretch', hide_index=True)
            
        else:
            st.info("لا توجد سجلات هجوم حتى الآن. قم بتشغيل الخدمات وحاول إرسال حزم اختبار.")


    time.sleep(1) 
    st.rerun() 

if __name__ == '__main__':
    try:
        def check_service_status_simple():
            statuses = {}
            process_names = ["Python_Proxy", "WAF_LLM", "PHP_Real", "PHP_Honey"]
            for name in process_names:
                process = app_runner.RUNNING_PROCESSES.get(name)
                statuses[name] = True if process and process.poll() is None else False
            return statuses

        def get_running_service_statuses():
            status_map = {
                "Python_Proxy": {"port": 8080, "status": "Stopped"},
                "WAF_LLM": {"port": 8000, "status": "Stopped"},
                "PHP_Real": {"port": 8082, "status": "Stopped"},
                "PHP_Honey": {"port": 8081, "status": "Stopped"},
            }
            statuses = check_service_status_simple()
            for name, is_running in statuses.items():
                 status_map[name]['status'] = 'Running' if is_running else 'Stopped'
            return status_map

        app_runner.get_running_service_statuses = get_running_service_statuses

    except AttributeError:
         pass 
    main()