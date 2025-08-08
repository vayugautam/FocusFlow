import streamlit as st
from utils.helpers import log_study_entry

st.title("📚 FocusFlow - Study Logger")

st.subheader("Log Today's Study Session")

# Input fields
subject = st.selectbox("Subject", ["DSA", "Dev", "DS", "GATE"])
topic = st.text_input("Topic Studied")
hours = st.slider("Hours Studied", 0.5, 8.0, step=0.5)
productivity = st.slider("How Productive Were You?", 1, 5)
mood = st.selectbox("Music/Mood", ["None", "Lofi", "Calm", "Upbeat", "Focus"])

# Submit button
if st.button("📥 Log Study Entry"):
    if topic.strip() == "":
        st.warning("Please enter a topic.")
    else:
        log_study_entry(subject, topic, hours, productivity, mood)
        st.success("✅ Entry logged successfully!")
