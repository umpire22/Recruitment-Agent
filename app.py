import streamlit as st
import pandas as pd

st.title("📝 Recruitment Screening Agent")

st.write("Screen candidates manually or in bulk.")

# Manual Entry
st.subheader("Manual Candidate Entry")
name = st.text_input("Candidate Name")
experience = st.number_input("Years of Experience", min_value=0, step=1)
skills = st.text_area("Skills (comma-separated)")
education = st.selectbox("Education Level", ["High School", "Bachelors", "Masters", "PhD"])

if st.button("Evaluate Candidate"):
    st.subheader(f"Evaluation for {name if name else 'Candidate'}")

    if experience >= 5 and "python" in skills.lower() and education in ["Masters", "PhD"]:
        st.write("⭐ Strong Candidate (Shortlist)")
    elif experience >= 2 and education in ["Bachelors", "Masters"]:
        st.write("⚠️ Average Candidate (Consider further screening)")
    else:
        st.write("❌ Weak Candidate (Not suitable)")

# Bulk Upload
st.subheader("Upload Candidate Dataset (CSV)")
uploaded_file = st.file_uploader("Upload file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    def evaluate(row):
        if row["Experience"] >= 5 and "python" in str(row["Skills"]).lower() and row["Education"] in ["Masters", "PhD"]:
            return "Strong"
        elif row["Experience"] >= 2 and row["Education"] in ["Bachelors", "Masters"]:
            return "Average"
        else:
            return "Weak"

    df["Result"] = df.apply(evaluate, axis=1)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Results", data=csv, file_name="recruitment_results.csv")
