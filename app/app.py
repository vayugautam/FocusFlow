import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px
import os

# Helper function to log study entries
def log_study_entry(subject, topic, hours, productivity, mood, date):
    filename = "data/study_logs.csv"
    new_entry = pd.DataFrame([{
        "Subject": subject,
        "Topic": topic,
        "Hours": hours,
        "Productivity": productivity,
        "Mood": mood,
        "Date": date.strftime("%Y-%m-%d %H:%M:%S")
    }])
    if os.path.exists(filename):
        new_entry.to_csv(filename, mode='a', header=False, index=False)
    else:
        os.makedirs("data", exist_ok=True)
        new_entry.to_csv(filename, index=False)

# Set page config
st.set_page_config(page_title="FocusFlow - Smart Study Tracker", layout="wide")

# Add main title at the top (visible on all pages)
st.markdown("# 🎓 FocusFlow - Smart Study Tracker")

# Sidebar navigation
page = st.sidebar.radio("📁 Navigate", ["📝 Log Study Session", "📊 Dashboard", "📈 Goals", "⚙️ Settings"])

# 📝 Log Study Session
if page == "📝 Log Study Session":
    st.title("📚 FocusFlow - Study Logger")
    st.write("Log your daily study sessions and track your productivity.")

    with st.form("study_log_form"):
        col1, col2 = st.columns([1, 1])
        with col1:
            subject = st.selectbox("📘 Subject *", ["", "DSA", "Development", "DS", "GATE"])
        with col2:
            topic = st.text_input("🔖 Topic *")

        hours = st.slider("⏰ Study Duration (hours) *", 0.5, 8.0, 1.0, 0.5, format="%.1f")
        st.markdown(f"**Selected Duration:** {hours} hrs")

        col3, col4 = st.columns(2)
        with col3:
            productivity = st.slider("🚀 Productivity (1-10)", 1, 10, 7)
        with col4:
            mood = st.selectbox("🎵 Study Mood", ["Focus Mode", "Calm", "Motivated", "Lofi", "Stressed", "Tired", "Happy"])

        date = st.date_input("📅 Date of Study", datetime.today())

        submitted = st.form_submit_button("✅ Log Study Entry")
        if submitted:
            if subject and topic:
                log_study_entry(subject, topic, hours, productivity, mood, date)
                st.success("✅ Study entry logged successfully!")
            else:
                st.error("❌ Please fill all required fields marked with *")

# 📊 Dashboard
elif page == "📊 Dashboard":
    st.header("📊 Study Analytics")

    # Load the data
    filename = "data/study_logs.csv"
    if os.path.isfile(filename):
        df = pd.read_csv(filename)
        df.columns = df.columns.str.strip()
        df["Date"] = pd.to_datetime(df["Date"])

        with st.expander("📄 Show Study Log Table"):
            st.dataframe(df)

        # Row 1
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📅 Hours Studied Over Time")
            chart_data = df.groupby(df["Date"].dt.date)["Hours"].sum().reset_index()
            chart_data["Date"] = pd.to_datetime(chart_data["Date"])
            fig = px.line(chart_data, x="Date", y="Hours", title="Daily Study Hours")
            fig.update_layout(xaxis_tickformat="%Y-%m-%d")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("⏱️ Time of Day You Study")
            df["Hour"] = df["Date"].dt.hour
            hour_data = df.groupby("Hour")["Hours"].sum().reset_index()
            fig2 = px.bar(hour_data, x="Hour", y="Hours", title="Study Hours by Time of Day")
            fig2.update_xaxes(
                title="Hour of Day",
                tickvals=[0, 4, 8, 12, 16, 20, 24],
                range=[0, 24]
            )
            fig2.update_yaxes(title="Total Study Hours")
            st.plotly_chart(fig2, use_container_width=True)

        # Row 2
        col3, col4 = st.columns([1, 1])

        with col3:
            st.subheader("📚 Subjects Studied")
            subject_data = df.groupby("Subject")["Hours"].sum().reset_index()
            fig3 = px.pie(subject_data, names="Subject", values="Hours", title="Time Spent per Subject")
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.subheader("📈 Cumulative Study Time")
            cumulative = df.groupby(df["Date"].dt.date)["Hours"].sum().cumsum().reset_index()
            cumulative["Date"] = pd.to_datetime(cumulative["Date"])
            fig4 = px.line(cumulative, x="Date", y="Hours", title="Cumulative Study Time")
            fig4.update_layout(xaxis_tickformat="%Y-%m-%d")
            st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No study logs found yet. Log your first session to see the dashboard!")

# 📈 Goals
elif page == "📈 Goals":
    import pandas as pd
    import os

    st.subheader("🎯 Weekly Study Goals")

    goals_file = "data/goals.csv"

    # Ensure file exists and is non-empty
    if not os.path.exists(goals_file) or os.path.getsize(goals_file) == 0:
        default_goals = pd.DataFrame({
            "Subject": ["DSA", "Dev", "DS", "GATE"],
            "TargetHours": [10, 8, 6, 12]
        })
        default_goals.to_csv(goals_file, index=False)

    # Now safely read goals
    goals_df = pd.read_csv(goals_file)

    # Load study log (ensure it also exists)
    try:
        log_df = pd.read_csv("data/study_log.csv")
    except FileNotFoundError:
        st.warning("⚠️ No study log found yet. Add logs to see progress.")
        log_df = pd.DataFrame(columns=["Date", "Subject", "Hours"])

    # Calculate actual hours studied
    actuals = log_df.groupby("Subject")["Hours"].sum().reset_index()
    actuals.columns = ["Subject", "ActualHours"]

    # Merge actuals with goals
    merged = pd.merge(goals_df, actuals, on="Subject", how="left").fillna(0)
    merged["Progress (%)"] = (merged["ActualHours"] / merged["TargetHours"]) * 100
    merged["Progress (%)"] = merged["Progress (%)"].clip(upper=100)

    # Display progress bars
    for _, row in merged.iterrows():
        st.write(f"**{row['Subject']}** — {row['ActualHours']}h / {row['TargetHours']}h")
        if pd.notna(row["Progress (%)"]):
            st.progress(int(row["Progress (%)"]))
        else:
            st.progress(0)

    # Option to log new study session directly from goals page
    st.markdown("### ⏱️ Log New Study Session")

    with st.form("log_form"):
        subject = st.selectbox("Subject", options=goals_df["Subject"].unique())
        hours = st.number_input("Hours Studied", min_value=0.0, step=0.5)
        log_date = st.date_input("Date", value=pd.Timestamp.today())

        submitted = st.form_submit_button("📌 Add Log")
        if submitted:
            new_log = pd.DataFrame({
                "Date": [log_date],
                "Subject": [subject],
                "Hours": [hours]
            })

            log_path = "data/study_log.csv"
            if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
                log_df = pd.read_csv(log_path)
                log_df = pd.concat([log_df, new_log], ignore_index=True)
            else:
                log_df = new_log

            log_df.to_csv(log_path, index=False)
            st.success("✅ Study log added! Refresh to see progress update.")

    # Editable goals section
    with st.expander("✏️ Edit Goals"):
        edited_df = st.data_editor(goals_df, num_rows="dynamic", use_container_width=True)
        if st.button("✅ Save Goals"):
            edited_df.to_csv(goals_file, index=False)
            st.success("Goals updated! Refresh to see changes.")
        if st.button("🔁 Reset to Default Goals"):
            default_goals = pd.DataFrame({
                "Subject": ["DSA", "Dev", "DS", "GATE"],
                "TargetHours": [10, 8, 6, 12]
            })
            default_goals.to_csv(goals_file, index=False)
            st.success("Goals reset to default! Refresh to see changes.")


# ⚙️ Settings
elif page == "⚙️ Settings":
    st.header("⚙️ Settings")
    st.info("🔧 Settings will be added in future updates.")
