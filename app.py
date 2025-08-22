import streamlit as st
import pandas as pd
import random
import re
from io import StringIO
from pdfplumber import PDFPlumber
from docx import Document

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
st.markdown("<p style='text-align: center; font-size:18px;'>Upload CVs, CSVs or enter candidate details to evaluate efficiently</p>", unsafe_allow_html=True)

# --- SESSION STATE ---
if "history" not in st.session_state:
    st.session_state.history = []

QUAL_SCORE = {"O'LEVEL":5, "OND":10, "HND":15, "BSC":20, "MSC":25, "PHD":30}

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(file):
    text = ""
    with PDFPlumber(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + " "
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    text = " ".join([p.text for p in doc.paragraphs])
    return text

def parse_candidate_info(text):
    skills_pattern = r"(Python|Java|C\+\+|SQL|Excel|Machine Learning|Data Analysis|React|Django|JavaScript|HTML|CSS)"
    skills_found = list(set(re.findall(skills_pattern, text, re.IGNORECASE)))
    skills_str = ", ".join(skills_found) if skills_found else "N/A"

    exp_match = re.search(r"(\d+)\s+years", text, re.IGNORECASE)
    experience = int(exp_match.group(1)) if exp_match else 0

    qual_match = re.search(r"(O'LEVEL|OND|HND|BSC|MSC|PHD)", text, re.IGNORECASE)
    qualification = qual_match.group(1).upper() if qual_match else "N/A"

    return skills_str, experience, qualification

def score_candidate(skills, experience, qualification):
    skill_count = len(skills.split(",")) if skills != "N/A" else 0
    qual_score = QUAL_SCORE.get(qualification, 0)
    score = min(100, skill_count * 10 + experience * 5 + qual_score + random.randint(-5,5))
    if score < 40:
        result = f"❌ Weak Candidate ({score}%)"
    elif score < 70:
        result = f"⚠️ Average Candidate ({score}%)"
    else:
        result = f"✅ Strong Candidate ({score}%)"
    return score, result

# --- MANUAL CANDIDATE SCREENING ---
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📝 Manual Candidate Screening")

    name = st.text_input("Candidate Name")
    skills = st.text_area("Skills & Experience (comma-separated)")
    years_exp = st.number_input("Years of Experience", min_value=0, max_value=40, step=1)
    qualification = st.selectbox("Qualification", ["O'LEVEL", "OND", "HND", "BSC", "MSC", "PHD"])

    if st.button("🔎 Evaluate Candidate"):
        if name.strip() and skills.strip():
            score, result = score_candidate(skills, years_exp, qualification)
            color = "green" if "Strong" in result else "orange" if "Average" in result else "red"
            st.markdown(f"<p style='color:{color}; font-size:18px; font-weight:bold;'>{result}</p>", unsafe_allow_html=True)

            st.session_state.history.append({
                "Name": name,
                "Skills": skills,
                "Experience (Years)": years_exp,
                "Qualification": qualification,
                "Score": score,
                "Result": result
            })
        else:
            st.warning("Please enter candidate details.")

    if st.button("🗑 Clear History"):
        st.session_state.history = []
        st.success("History cleared!")

    st.markdown("</div>", unsafe_allow_html=True)

# --- BULK CSV SCREENING ---
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📂 Bulk Candidate Screening (CSV Upload)")

    uploaded_file = st.file_uploader("Upload a CSV with columns: Name, Skills, Experience (Years), Qualification", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if {"Name", "Skills", "Experience (Years)", "Qualification"}.issubset(df.columns):
            results, scores = [], []
            for _, row in df.iterrows():
                score, result = score_candidate(row["Skills"], row["Experience (Years)"], row["Qualification"])
                scores.append(score)
                results.append(result)
                st.session_state.history.append({
                    "Name": row["Name"],
                    "Skills": row["Skills"],
                    "Experience (Years)": row["Experience (Years)"],
                    "Qualification": row["Qualification"],
                    "Score": score,
                    "Result": result
                })

            df["Score"] = scores
            df["Screening Result"] = results

            def highlight_result(val):
                if "Strong" in val: return "background-color: #c8e6c9; color: green;"
                elif "Average" in val: return "background-color: #fff9c4; color: orange;"
                else: return "background-color: #ffcdd2; color: red;"

            st.dataframe(df.style.applymap(highlight_result, subset=["Screening Result"]))
            st.download_button("⬇️ Download Results", data=df.to_csv(index=False), file_name="screening_results.csv", mime="text/csv")
        else:
            st.error("CSV must contain: Name, Skills, Experience (Years), Qualification.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- CV SCREENING ---
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📄 CV Screening (PDF/DOCX Upload)")

    uploaded_files = st.file_uploader("Upload one or multiple CVs", type=["pdf","docx"], accept_multiple_files=True)

    if uploaded_files:
        for file in uploaded_files:
            if file.type == "application/pdf":
                text = extract_text_from_pdf(file)
            else:
                text = extract_text_from_docx(file)

            skills, exp, qual = parse_candidate_info(text)
            score, result = score_candidate(skills, exp, qual)

            st.markdown(f"**{file.name}**")
            st.write(f"Skills: {skills}")
            st.write(f"Experience: {exp} years")
            st.write(f"Qualification: {qual}")
            color = "green" if "Strong" in result else "orange" if "Average" in result else "red"
            st.markdown(f"<p style='color:{color}; font-weight:bold;'>{result}</p>", unsafe_allow_html=True)

            st.session_state.history.append({
                "Name": file.name,
                "Skills": skills,
                "Experience (Years)": exp,
                "Qualification": qual,
                "Score": score,
                "Result": result
            })
    st.markdown("</div>", unsafe_allow_html=True)

# --- HISTORY & TOP CANDIDATES ---
if st.session_state.history:
    hist_df = pd.DataFrame(st.session_state.history)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📜 Screening History")
    st.dataframe(hist_df, use_container_width=True)
    st.download_button("⬇️ Download History", data=hist_df.to_csv(index=False), file_name="screening_history.csv", mime="text/csv")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🏆 Top Candidates")
    top_df = hist_df.sort_values(by="Score", ascending=False).head(5)
    st.dataframe(top_df, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- FILTER PANEL ---
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🔍 Filter Candidates")

    if st.session_state.history:
        all_skills = sorted({skill.strip() for skills in hist_df["Skills"] for skill in skills.split(",") if skill})
        selected_skills = st.multiselect("Select Skills", options=all_skills)
        min_score = st.slider("Minimum Score (%)", 0, 100, 0)
        qualifications = ["O'LEVEL","OND","HND","BSC","MSC","PHD"]
        selected_quals = st.multiselect("Select Qualifications", options=qualifications)

        filtered_df = hist_df.copy()
        if selected_skills:
            filtered_df = filtered_df[filtered_df["Skills"].apply(lambda x: all(skill.lower() in x.lower() for skill in selected_skills))]
        if selected_quals:
            filtered_df = filtered_df[filtered_df["Qualification"].isin(selected_quals)]
        filtered_df = filtered_df[filtered_df["Score"] >= min_score]

        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("No candidates match the filters.")
    else:
        st.info("No candidates in history yet.")

    st.markdown("</div>", unsafe_allow_html=True)
