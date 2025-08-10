import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import os
import numpy as np

st.set_page_config(page_title="FocusFlow - Smart Study Tracker", layout="wide")

try:
    from zoneinfo import ZoneInfo
    KOLKATA = ZoneInfo("Asia/Kolkata")
except ImportError:
    KOLKATA = None

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

# =====================================================================
# 1. ALL FUNCTION DEFINITIONS
# =====================================================================

def save_session_to_csv(entry_dict, filename="data/study_logs.csv"):
	"""Append one session dict to CSV (create file with header if missing)."""
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	df_new = pd.DataFrame([entry_dict])
	write_header = not os.path.exists(filename) or os.path.getsize(filename) == 0
	df_new.to_csv(filename, mode='a', header=write_header, index=False)


def apply_plotly_theme(fig):
    """Applies the correct Plotly theme based on the session state."""
    if st.session_state.get("dark_mode", False):
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e6eef3"),
            # --- ✅ Add these specific color settings for the title ---
            title_font_color="#e6eef3",
            legend_font_color="#e6eef3"
        )
    else:
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#000000"),
            # --- ✅ Add these specific color settings for the title ---
            title_font_color="#000000",
            legend_font_color="#000000"
        )
    return fig

def _now_kolkata():
    """Gets the current time in Asia/Kolkata timezone if available."""
    if KOLKATA:
        return datetime.now(KOLKATA)
    return datetime.now()

def compute_streak(dates_set, today_date):
    """Counts consecutive study days leading up to today."""
    streak = 0
    cur = today_date
    while cur in dates_set:
        streak += 1
        cur = cur - timedelta(days=1)
    return streak

st.markdown("# 🎓 FocusFlow - Smart Study Tracker")

def header_section(data_path="data/study_logs.csv", user_name="You"):
    """Displays the header with greeting, metrics, and the dark mode toggle."""
    now = _now_kolkata()
    hour = now.hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    total_hours, week_hours, streak, best_subject = 0.0, 0.0, 0, "—"
    today_date = now.date()

    if os.path.exists(data_path) and os.path.getsize(data_path) > 0:
        try:
            df = pd.read_csv(data_path, encoding="utf-8-sig")
            df.columns = df.columns.str.strip()
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                df["DateOnly"] = df["Date"].dt.date
            else:
                df["DateOnly"] = pd.NaT
            if "Hours" in df.columns:
                df["Hours"] = pd.to_numeric(df["Hours"], errors="coerce").fillna(0.0)
            else:
                df["Hours"] = 0.0

            total_hours = float(df["Hours"].sum())
            week_start = today_date - timedelta(days=6)
            df_week = df[df["DateOnly"].notna() & (df["DateOnly"] >= week_start)]
            week_hours = float(df_week["Hours"].sum())

            if df["DateOnly"].notna().any():
                dates_set = set(df["DateOnly"].dropna().astype("O"))
                streak = compute_streak(dates_set, today_date)

            if "Subject" in df.columns and not df.empty:
                subj = df.groupby("Subject")["Hours"].sum()
                if not subj.empty:
                    best_subject = subj.idxmax()
        except Exception:
            pass

    left, right = st.columns([3, 1])
    with left:
        st.markdown(f"### {greeting}, **{user_name}** 👋")
        st.markdown("**FocusFlow** — track your study, keep momentum, and reach your goals.")
    with right:
        st.checkbox("🌙 Dark mode", key="dark_mode")

    m1, m2, m3 = st.columns(3)
    m1.metric("📚 Total hours", f"{total_hours:.1f} hrs")
    m2.metric("🗓️ Hours (7d)", f"{week_hours:.1f} hrs")
    m3.metric("🔥 Streak", f"{streak} days")
    st.markdown(f"**Top subject:** {best_subject}")

# =====================================================================
# 2. APP CONFIG AND EXECUTION FLOW
# =====================================================================

# Step 1: Render the header, which includes the dark mode checkbox
header_section(data_path="data/study_logs.csv", user_name="Vayu")

# Step 2: Apply the CSS theme based on the session state
_common_selectors = """
body, .stMarkdown, .stText, .stMetric, [class*="st-emotion-cache"],
h1, h2, h3, h4, h5, h6,
label, input, textarea, select, option,
div[data-testid="stDataFrame"], .stDataFrame, .st-bq {
    opacity: 1 !important;
}
"""

if st.session_state.get("dark_mode", False):
    dark_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap');
    :root {{ color-scheme: dark; }}
    body, .stApp, .stMarkdown, .stText, .stMetric, [class*="st-emotion-cache"], h1, h2, h3, h4, h5, h6 {{
        font-family: 'Source Sans Pro', sans-serif !important;
    }}
    .stApp, .block-container, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: #0b1220 !important;
        color: #e6eef3 !important;
    }}
    section[data-testid="stSidebar"] {{
        background-color: #111827 !important;
        color: #e6eef3 !important;
    }}
    {_common_selectors}
    h1,h2,h3,h4,h5,h6, p, div[data-testid="stMetricLabel"], div[data-testid="stMetricValue"] {{
        color: #e6eef3 !important;
        -webkit-text-fill-color: #e6eef3 !important;
    }}
    .stButton>button {{
        background-color: #0ea5a4 !important;
        color: #001 !important;
    }}

    /* Input widget backgrounds */
    div[data-baseweb="base-input"],
    div[data-baseweb="select"] > div:first-child {{
        background-color: #111827 !important;
        border-color: #374151 !important;
    }}

    /* Text color inside all input widgets */
    div[data-baseweb="base-input"] input,
    div[data-baseweb="select"] * {{
        -webkit-text-fill-color: #e6eef3 !important;
        color: #e6eef3 !important;
    }}

    /* Tab styling */
    button[data-baseweb="tab"] {{
        border-radius: 8px 8px 0px 0px !important;
        background-color: transparent !important;
        color: #e6eef3 !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: #111827 !important;
        border-bottom: 2px solid #0ea5a4;
    }}

    /* Plotly chart text */
    .plotly-graph-div .gtitle, .plotly-graph-div text {{
        fill: #e6eef3 !important;
    }}
    </style>
    """
    st.markdown(dark_css, unsafe_allow_html=True)
else:
    # --- Light Mode CSS (No changes needed here, but included for completeness) ---
    light_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap');
    :root {{ color-scheme: light; }}
    body, .stApp, .stMarkdown, .stText, .stMetric, [class*="st-emotion-cache"], h1, h2, h3, h4, h5, h6 {{
        font-family: 'Source Sans Pro', sans-serif !important;
    }}
    .stApp, .block-container, [data-testid="stAppViewContainer"] {{ background-color: #ffffff !important; color: #000000 !important; }}
    section[data-testid="stSidebar"] {{ background-color: #f9f9f9 !important; color: #000000 !important; }}
    {_common_selectors}
    .stButton>button {{ background-color: #0ea5a4 !important; color: #fff !important; }}
    button[data-baseweb="tab"] {{
        border-radius: 8px 8px 0px 0px !important;
        background-color: transparent !important;
        color: #000000 !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: #F0F2F6 !important;
        border-bottom: 2px solid #0ea5a4;
    }}
    .plotly-graph-div .gtitle, .plotly-graph-div text {{
        fill: #000000 !important;
    }}
    </style>
    """
    st.markdown(light_css, unsafe_allow_html=True)

# Step 3: Render the rest of the app

page = st.sidebar.radio(
    "📁 Navigate",
    ["📝 Log Study Session", "📊 Dashboard", "📈 Goals", "⚙️ Settings"],
    key="navigation_radio"
)

# =====================================================================
# 3. PAGE ROUTING LOGIC
# =====================================================================

if page == "📝 Log Study Session":
    st.title("📚 FocusFlow - Study Logger")
    st.write("Log your daily study sessions and track your productivity.")
    if "active_session" not in st.session_state:
        with st.form("start_session_form", clear_on_submit=True):
            col1, col2 = st.columns([1, 1])
            with col1:
                subject = st.selectbox("📘 Subject *", ["", "DSA", "Development", "DS", "GATE"])
                topic = st.text_input("🔖 Topic *")
            with col2:
                now_t = datetime.now()
                start_time = st.time_input("⏰ Start Time", value=now_t.time())
                planned_end_default = (now_t + timedelta(hours=1)).time()
                planned_end_time = st.time_input("⏳ Planned End Time", value=planned_end_default)
            col3, col4 = st.columns(2)
            with col3:
                start_mood = st.selectbox("🎵 Mood at start", ["Focus Mode", "Calm", "Motivated", "Lofi", "Stressed", "Tired", "Happy"])
            with col4:
                st.markdown("⏱️ You'll provide productivity & end-mood when you stop the session")

            if st.form_submit_button("▶️ Start Session"):
                if subject and topic:
                    st.session_state.active_session = {
                        "subject": subject, "topic": topic, "start_dt": datetime.now(),
                        "start_time": start_time.strftime("%H:%M"),
                        "planned_end_time": planned_end_time.strftime("%H:%M"),
                        "start_mood": start_mood
                    }
                    st.success("✅ Session started — good luck!")
                else:
                    st.error("❌ Please fill Subject and Topic to start.")
    else:
        sess = st.session_state.active_session
        st.markdown("### 🔴 Active Session")
        st.write(f"**Subject:** {sess['subject']}  •  **Topic:** {sess['topic']}")
        st.write(f"**Started at:** {sess['start_dt'].strftime('%Y-%m-%d %H:%M:%S')}")
        elapsed = datetime.now() - sess["start_dt"]
        st.info(f"⏳ Elapsed: {str(elapsed).split('.')[0]}")

        if st.button("⏹️ Stop Session and Save"):
            st.session_state.show_end_form = True

        if st.session_state.get("show_end_form", False):
            st.markdown("### ✅ End Session")
            with st.form("end_session_form"):
                end_mood = st.selectbox("🎵 Mood at end", ["Focus Mode", "Calm", "Motivated", "Lofi", "Stressed", "Tired", "Happy"], index=0)
                productivity = st.slider("🚀 Productivity (1-10)", 1, 10, 7)
                notes = st.text_area("Notes (optional) — what went well / blockers")
                if st.form_submit_button("💾 Save Session"):
                    end_dt = datetime.now()
                    total_hours = round((end_dt - sess["start_dt"]).total_seconds() / 3600.0, 2)
                    entry = {
                        "Date": sess["start_dt"].strftime("%Y-%m-%d"), "Subject": sess["subject"],
                        "Topic": sess["topic"], "Start Time": sess["start_time"],
                        "End Time": end_dt.strftime("%H:%M"), "Planned End Time": sess["planned_end_time"],
                        "Hours": total_hours, "Productivity": productivity,
                        "Start Mood": sess["start_mood"], "End Mood": end_mood,
                        "Notes": notes, "Timestamp": end_dt.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    save_session_to_csv(entry)
                    st.success("✅ Session saved to data/study_logs.csv")
                    del st.session_state["active_session"]
                    if "show_end_form" in st.session_state:
                        del st.session_state["show_end_form"]
                    st.rerun()

elif page == "📊 Dashboard":
    st.header("📊 Study Analytics")
    filename = "data/study_logs.csv"

    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        st.info("No study logs found. Start by adding a session on the '📝 Log Study Session' page!")
    else:
        # Load and process data once, before the tabs
        df = pd.read_csv(filename)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df[df['Hours'] >= 0] # Filter out negative hours

        if "Start Time" in df.columns and "End Time" in df.columns:
            df["Start Time"] = df["Start Time"].astype(str).str.strip().apply(lambda x: x.zfill(5) if ":" in x else x)
            df["End Time"] = df["End Time"].astype(str).str.strip().apply(lambda x: x.zfill(5) if ":" in x else x)
            df["Start_dt"] = pd.to_datetime(df["Date"].dt.strftime("%Y-%m-%d") + " " + df["Start Time"], errors="coerce")
            df["End_dt"] = pd.to_datetime(df["Date"].dt.strftime("%Y-%m-%d") + " " + df["End Time"], errors="coerce")
            df.loc[df["End_dt"] < df["Start_dt"], "End_dt"] += timedelta(days=1)

        # Create the tabs
        tab1, tab2 = st.tabs(["📈 Overview", "🧠 Smart Insights"])

        with tab1:
            # --- OVERVIEW CHARTS ---
            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader("📅 Hours Studied Over Time")
                if "Hours" in df.columns and not df.empty and df['Date'].notna().any():
                    chart_data = df.groupby(df["Date"].dt.date)["Hours"].sum().reset_index()
                    fig = px.line(chart_data, x="Date", y="Hours", title="Daily Study Hours")
                    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
                else: st.info("No 'Hours' data found.")

            with col2:
                st.subheader("⏱️ Time of Day You Study")
                if "Start_dt" in df.columns and not df.dropna(subset=["Start_dt", "End_dt"]).empty:
                    expanded_hours = [h for _, row in df.dropna(subset=["Start_dt", "End_dt"]).iterrows() for h in pd.date_range(row["Start_dt"].floor('H'), row["End_dt"], freq='H').hour]
                    if expanded_hours:
                        hour_data = pd.Series(expanded_hours).value_counts().sort_index().reset_index()
                        hour_data.columns = ["Hour", "Sessions"]
                        fig2 = px.bar(hour_data, x="Hour", y="Sessions", title="Study Hours by Time of Day")
                        st.plotly_chart(apply_plotly_theme(fig2), use_container_width=True)
                    else: st.info("No hourly data.")
                else: st.warning("Start/End Time columns missing.")

            col3, col4 = st.columns([1, 1])
            with col3:
                st.subheader("📚 Subjects Studied")
                if "Subject" in df.columns and "Hours" in df.columns and not df.empty:
                    subject_data = df.groupby("Subject")["Hours"].sum().reset_index()
                    fig3 = px.pie(subject_data, names="Subject", values="Hours", title="Time Spent per Subject")
                    st.plotly_chart(apply_plotly_theme(fig3), use_container_width=True)
                else: st.info("No subject data found.")

            with col4:
                st.subheader("📈 Cumulative Study Time")
                if "Hours" in df.columns and "Date" in df.columns and not df.empty:
                    df_positive_hours = df[df['Hours'] >= 0]
                    if not df_positive_hours.empty and df_positive_hours["Date"].notna().any():
                        df_sorted = df_positive_hours.sort_values(by="Date").dropna(subset=["Date", "Hours"])
                        if not df_sorted.empty:
                            cumulative = df_sorted.groupby(df_sorted["Date"].dt.date)["Hours"].sum().cumsum().reset_index()
                            fig4 = px.line(cumulative, x="Date", y="Hours", title="Cumulative Study Time")
                            fig4.update_layout(xaxis_title="Date", yaxis_title="Total Cumulative Hours", yaxis_ticksuffix=" hrs", xaxis_tickformat="%d-%b-%Y")
                            st.plotly_chart(apply_plotly_theme(fig4), use_container_width=True)
                        else: st.info("No valid data for cumulative time.")
                    else: st.info("No valid data for cumulative time.")
                else: st.info("No data for cumulative time.")

        with tab2:
            # --- SMART INSIGHTS ---
            st.subheader("🧠 Smart Insights")
            c1, c2 = st.columns(2)

            with c1:
                st.markdown("##### Productivity by Time of Day")
                if "Productivity" in df.columns and "Start_dt" in df.columns and not df.dropna(subset=["Start_dt", "Productivity"]).empty:
                    df["Start_Hour"] = df["Start_dt"].dt.hour
                    prod_by_hour = df.groupby("Start_Hour")["Productivity"].mean().round(1).reset_index()
                    fig = px.bar(prod_by_hour, x="Start_Hour", y="Productivity", text="Productivity")
                    fig.update_traces(textposition='outside')
                    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
                    if not prod_by_hour.empty:
                        peak_hour_row = prod_by_hour.loc[prod_by_hour['Productivity'].idxmax()]
                        peak_hour, peak_prod = int(peak_hour_row['Start_Hour']), peak_hour_row['Productivity']
                        st.markdown(f"**💡 Recommendation:** Your productivity peaks at **{peak_hour}:00** (avg score: {peak_prod}). Try scheduling your most challenging subjects then!")
                else:
                    st.info("Log more sessions with productivity scores to see insights here.")

            with c2:
                st.markdown("##### Productivity by Starting Mood")
                if "Productivity" in df.columns and "Start Mood" in df.columns and not df.dropna(subset=["Start Mood", "Productivity"]).empty:
                    prod_by_mood = df.groupby("Start Mood")["Productivity"].mean().round(1).sort_values(ascending=False).reset_index()
                    fig = px.bar(prod_by_mood, x="Start Mood", y="Productivity", text="Productivity")
                    fig.update_traces(textposition='outside')
                    st.plotly_chart(apply_plotly_theme(fig), use_container_width=True)
                    if len(prod_by_mood) > 1:
                        best_mood, worst_mood = prod_by_mood.iloc[0]["Start Mood"], prod_by_mood.iloc[-1]["Start Mood"]
                        st.markdown(f"**💡 Recommendation:** You're most productive when you feel **{best_mood}**. On days you feel **{worst_mood}**, a warm-up might boost your focus.")
                else:
                    st.info("Log more sessions with starting moods to see insights here.")

elif page == "📈 Goals":
    st.subheader("🎯 Weekly Study Goals")
    goals_file = "data/goals.csv"
    if not os.path.exists(goals_file) or os.path.getsize(goals_file) == 0:
        default_goals = pd.DataFrame({"Subject": ["DSA", "Dev", "DS", "GATE"], "TargetHours": [10, 8, 6, 12]})
        default_goals.to_csv(goals_file, index=False)

    goals_df = pd.read_csv(goals_file)
    log_file = "data/study_logs.csv"

    if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
        log_df = pd.read_csv(log_file)
        actuals = log_df.groupby("Subject")["Hours"].sum().reset_index()
        actuals.columns = ["Subject", "ActualHours"]
        merged = pd.merge(goals_df, actuals, on="Subject", how="left").fillna(0)
    else:
        st.warning("⚠️ No study log found yet. Add logs to see progress.")
        merged = goals_df.copy()
        merged["ActualHours"] = 0

    merged["Progress (%)"] = (merged["ActualHours"] / merged["TargetHours"].replace(0, np.inf)) * 100
    merged["Progress (%)"] = merged["Progress (%)"].clip(upper=100).astype(int)

    for _, row in merged.iterrows():
        st.write(f"**{row['Subject']}** — {row['ActualHours']:.1f}h / {row['TargetHours']:.0f}h")
        st.progress(row["Progress (%)"])

    with st.expander("✏️ Edit Goals"):
        edited_df = st.data_editor(goals_df, num_rows="dynamic", use_container_width=True)
        if st.button("✅ Save Goals"):
            edited_df.to_csv(goals_file, index=False)
            st.success("Goals updated!")
            st.rerun()

elif page == "⚙️ Settings":
    st.header("⚙️ Settings")
    st.info("🔧 Settings will be added in future updates. You can clear your study history here.")

    if st.button("⚠️ Clear All Study Logs", type="primary"):
        log_file = "data/study_logs.csv"
        if os.path.exists(log_file):
            header_columns = [
                "Date", "Subject", "Topic", "Start Time", "End Time",
                "Planned End Time", "Hours", "Productivity", "Start Mood",
                "End Mood", "Notes", "Timestamp"
            ]
            empty_df = pd.DataFrame(columns=header_columns)
            empty_df.to_csv(log_file, index=False)
            st.success("All study logs have been cleared. The file is now empty.")
            st.rerun()
        else:
            st.warning("No study logs found to clear.")
