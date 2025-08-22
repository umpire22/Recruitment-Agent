import streamlit as st
import pandas as pd
import random

# --- PAGE CONFIG ---
st.set_page_config(page_title="🧑‍💼 Recruitment Screening Agent", page_icon="🧑‍💼", layout="wide")

# --- CUSTOM STYLES ---
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #e3f2fd, #ffffff);
        }
        .stButton > button {
            background: linear-gradient(to right, #1565c0, #42a5f5);
            color: white;
            border-radius: 12px;
            padding: 10px 20px;
            font-weight: bold;
            transition: 0.3s;
        }
        .stButton > button:hover {
            background: linear-gradient(to right, #42a5f5, #1565c0);
            transform: scale(1.05);
        }
        .card {
            padding: 20px;
            border-radius: 15px;
            background-color: #ffffff;
            box-shadow: 2px 2px 12px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- APP HEADER ---
st.markdown("<h1 style='text-align: center; color: #1565c0;'>🧑‍💼 Recruitment Screening Agent</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:18px;'>Evaluate candidates efficiently and identify top talent</p>", unsafe_allow_html=True)

# --- SESSION STATE FOR HISTORY ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- MANUAL CANDIDATE SCREENING ---
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📝 Manual Candidate Screening")

    name = st.text_input("Candidate Name")
    skills = st.text_area("Skills & Experience (comma-separated)")
    years_exp = st.number_input("Years of Experience", min_value=0, max_value=40, step=1)

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("🔎 Evaluate Candidate"):
            if name.strip() and skills.strip():
                # Simple candidate score simulation
                score = random.randint(1, 100)
                if score < 40:
                    result = f"❌ Weak Candidate ({score}%)"
                    color = "red"
                elif 40 <= score < 70:
                    result = f"⚠️ Average Candidate ({score}%)"
                    color = "orange"
                else:
                    result = f"✅ Strong Candidate ({score}%)"
                    color = "green"

                st.markdown(f"<p style='color:{color}; font-size:18px; font-weight:bold;'>{result}</p>", unsafe_allow_html=True)

                # Save to history
                st.session_state.history.append({
                    "Name": name,
                    "Skills": skills,
                    "Experience (Years)": years_exp,
                    "Score": score,
                    "Result": result
                })
            else:
                st.warning("Please enter candidate details.")

    with col2:
        if st.button("🗑 Clear History"):
            st.session_state.history = []
            st.success("History cleared!")

    st.markdown("</div>", unsafe_allow_html=True)

# --- HISTORY LOG ---
if st.session_state.history:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📜 Screening History")
    hist_df = pd.DataFrame(st.session_state.history)
    st.dataframe(hist_df, use_container_width=True)
    st.download_button("⬇️ Download History", data=hist_df.to_csv(index=False), file_name="screening_history.csv", mime="text/csv")
    st.markdown("</div>", unsafe_allow_html=True)

# --- BULK SCREENING ---
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📂 Bulk Candidate Screening (CSV Upload)")

    uploaded_file = st.file_uploader("Upload a CSV with columns: Name, Skills, Experience (Years)", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        if {"Name", "Skills", "Experience (Years)"}.issubset(df.columns):
            results = []
            scores = []
            for _, row in df.iterrows():
                score = random.randint(1, 100)
                scores.append(score)
                if score < 40:
                    results.append("❌ Weak Candidate")
                elif 40 <= score < 70:
                    results.append("⚠️ Average Candidate")
                else:
                    results.append("✅ Strong Candidate")

            df["Score"] = scores
            df["Screening Result"] = results

            # Highlight results
            def highlight_result(val):
                if "Strong" in val:
                    return "background-color: #c8e6c9; color: green;"
                elif "Average" in val:
                    return "background-color: #fff9c4; color: orange;"
                else:
                    return "background-color: #ffcdd2; color: red;"

            st.write("🔎 Screening Results:")
            st.dataframe(df.style.applymap(highlight_result, subset=["Screening Result"]))

            # Download button
            st.download_button("⬇️ Download Results", data=df.to_csv(index=False), file_name="screening_results.csv", mime="text/csv")
        else:
            st.error("CSV must contain: Name, Skills, Experience (Years).")
    st.markdown("</div>", unsafe_allow_html=True)
