import streamlit as st
import pandas as pd
import time
import os
import re

# CONFIG
LOG_FILE = "test_logs.txt"

# 1. Page Config
st.set_page_config(page_title="Sentinel Dashboard", layout="wide")
st.title("🛡️ Sentinel Edge AI: Live Monitor")

# 2. Check for File existence to prevent crash
if not os.path.exists(LOG_FILE):
    st.warning(f"⏳ Waiting for {LOG_FILE} to be created...")
    st.info("Please start the main sentinel script first.")
    time.sleep(2)
    st.rerun()

# 3. Load Data with error handling
try:
    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
except Exception as e:
    st.error(f"Error reading log file: {e}")
    st.stop()

# 4. Metrics
threat_keywords = ["Failed password", "SQL injection", "XSS", "malicious", "attack"]
threat_count = sum(1 for line in lines if any(keyword.lower() in line.lower() for keyword in threat_keywords))

col1, col2, col3 = st.columns(3)
col1.metric("System Status", "ONLINE", "🟢 Active")
col2.metric("AI Model", "Phi-3.5", "✓ Running")
col3.metric("Threats Detected", threat_count, delta_color="inverse")

# 5. Data Display
st.subheader("📊 Recent Activity (Last 10 Entries)")

if lines:
    data = []
    for idx, line in enumerate(lines[-10:]):  # Last 10 lines
        # Check for threat indicators
        is_threat = any(keyword.lower() in line.lower() for keyword in threat_keywords)
        status = "🚨 THREAT" if is_threat else "✅ SAFE"
        
        # Extract IP if present
        ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
        ip = ip_match.group(1) if ip_match else "N/A"
        
        data.append({
            "#": len(lines) - 10 + idx + 1,
            "Status": status,
            "IP": ip,
            "Log": line.strip()[:100]  # Truncate long logs
        })
    
    df = pd.DataFrame(data)
    
    # Styling function
    def highlight_threats(row):
        if "🚨" in row['Status']:
            return ['background-color: #ff4444; color: white'] * len(row)
        return [''] * len(row)
    
    # FIXED: Use apply with axis=1 for row-wise styling
    styled_df = df.style.apply(highlight_threats, axis=1)
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
else:
    st.info("No logs yet. Waiting for activity...")

# 6. Real-time Stats
st.subheader("📈 Statistics")
col4, col5, col6 = st.columns(3)

total_logs = len(lines)
safe_logs = total_logs - threat_count
threat_percentage = (threat_count / total_logs * 100) if total_logs > 0 else 0

col4.metric("Total Logs", total_logs)
col5.metric("Safe Events", safe_logs)
col6.metric("Threat Rate", f"{threat_percentage:.1f}%")

# 7. Auto-refresh control
st.sidebar.header("⚙️ Settings")
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 1, 10, 2)

if auto_refresh:
    st.sidebar.info(f"Refreshing every {refresh_interval}s")
    time.sleep(refresh_interval)
    st.rerun()
else:
    if st.sidebar.button("🔄 Manual Refresh"):
        st.rerun()