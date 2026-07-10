import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import io

from resume_parser import extract_text_from_pdf, extract_name
from skill_extractor import extract_skills_from_text, DEFAULT_SKILLS
from ranking import calculate_match_scores
from utils import SAMPLE_JOB_DESCRIPTIONS, export_to_csv, export_to_excel

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Recruiter - Resume Screening & Ranking",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PREMIUM LOOK & FEEL ---
st.markdown("""
    <style>
    /* Main Background and Typography */
    .main {
        background-color: #F8FAFC;
    }
    
    /* Title and Subtitle */
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 2rem;
    }
    
    /* Card Container */
    .metric-card {
        background-color: white;
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 1rem;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }
    .metric-value {
        font-size: 1.8rem;
        color: #1E293B;
        font-weight: 700;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #3182CE;
        font-weight: 500;
        margin-top: 0.25rem;
    }
    
    /* Skill Badges styling */
    .skill-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        font-size: 0.8rem;
        font-weight: 600;
        border-radius: 9999px;
        margin: 0.2rem;
    }
    .badge-matched {
        background-color: #DEF7EC;
        color: #03543F;
        border: 1px solid #BCF0DA;
    }
    .badge-missing {
        background-color: #FDE8E8;
        color: #9B1C1C;
        border: 1px solid #FBD5D5;
    }
    .badge-additional {
        background-color: #E1EFFE;
        color: #1E429F;
        border: 1px solid #C3DDFD;
    }
    
    /* Recruiter Table Badges */
    .status-excellent {
        background-color: #DEF7EC;
        color: #03543F;
        font-weight: bold;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    .status-good {
        background-color: #E1EFFE;
        color: #1E429F;
        font-weight: bold;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    .status-average {
        background-color: #FEF08A;
        color: #713F12;
        font-weight: bold;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    .status-improvement {
        background-color: #FDE8E8;
        color: #9B1C1C;
        font-weight: bold;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "job_description" not in st.session_state:
    st.session_state.job_description = ""
if "processed_resumes" not in st.session_state:
    st.session_state.processed_resumes = []
if "rankings" not in st.session_state:
    st.session_state.rankings = []
if "failures" not in st.session_state:
    st.session_state.failures = []
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

# --- HEADER SECTION ---
st.markdown('<h1 class="main-title">💼 AI-Powered Resume Screening & Candidate Ranking</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Automate screening, extract skills, compare candidate gaps, and rank applicants objectively using TF-IDF and Cosine Similarity.</p>', unsafe_allow_html=True)

# --- INPUT SECTION (2 Columns) ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1. Job Description")
    
    # Pre-load sample buttons
    st.write("💡 Quick Load Sample Job Descriptions:")
    sample_cols = st.columns(len(SAMPLE_JOB_DESCRIPTIONS))
    for idx, (title, jd_text) in enumerate(SAMPLE_JOB_DESCRIPTIONS.items()):
        if sample_cols[idx].button(title, key=f"btn_sample_{idx}", width="stretch"):
            st.session_state.job_description = jd_text
            
    # Text input for job description
    st.session_state.job_description = st.text_area(
        "Enter or paste the Job Description here:",
        value=st.session_state.job_description,
        height=280,
        placeholder="We are looking for a software developer with skills in Python, Git..."
    )

with col2:
    st.subheader("2. Upload Candidate Resumes")
    
    uploaded_files = st.file_uploader(
        "Upload multiple resume files (PDF format only):",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload multiple candidate resumes as PDF files to parse and rank."
    )
    
    if uploaded_files:
        st.success(f"📂 {len(uploaded_files)} PDF file(s) selected.")
        # Visual list of uploaded files
        with st.expander("Show uploaded filenames", expanded=True):
            for f in uploaded_files:
                st.markdown(f"- `{f.name}` ({round(f.size/1024, 1)} KB)")

# --- TRIGGER EVALUATION ---
st.markdown("---")
analyze_btn = st.button("🚀 Analyze & Rank Resumes", type="primary", width="stretch")

if analyze_btn:
    if not st.session_state.job_description.strip():
        st.error("⚠️ Please enter a job description or load one of the samples first.")
    elif not uploaded_files:
        st.error("⚠️ Please upload at least one PDF resume file.")
    else:
        with st.spinner("Processing resumes, extracting names/skills, and computing AI match scores..."):
            parsed_resumes = []
            failures_list = []
            seen_filenames = set()
            duplicates_count = 0
            
            for file_obj in uploaded_files:
                filename = file_obj.name
                
                # Deduplication check
                if filename in seen_filenames:
                    duplicates_count += 1
                    continue
                seen_filenames.add(filename)
                
                # Text Extraction & parsing
                try:
                    # PyPDF2 extraction
                    extracted_text = extract_text_from_pdf(file_obj)
                    candidate_name = extract_name(extracted_text, filename)
                    
                    parsed_resumes.append({
                        "name": candidate_name,
                        "filename": filename,
                        "text": extracted_text
                    })
                except Exception as e:
                    failures_list.append({
                        "filename": filename,
                        "error": str(e)
                    })
                    
            if duplicates_count > 0:
                st.warning(f"⚠️ Skipped {duplicates_count} duplicate file(s) with matching filenames.")
                
            if parsed_resumes:
                # Rank resumes
                rankings = calculate_match_scores(st.session_state.job_description, parsed_resumes)
                
                # Save to session state
                st.session_state.processed_resumes = parsed_resumes
                st.session_state.rankings = rankings
                st.session_state.failures = failures_list
                st.session_state.analyzed = True
                
                st.balloons()
            else:
                st.error("❌ Failed to extract readable text from any of the uploaded PDFs. Check the Parser Failures tab below.")
                st.session_state.analyzed = False
                st.session_state.failures = failures_list

# --- DISPLAY ANALYSIS RESULTS (TABS) ---
if st.session_state.analyzed:
    # 1. SIDEBAR FILTERS
    st.sidebar.markdown("### ⚙️ Analysis Filters")
    
    search_query = st.sidebar.text_input("🔍 Search Candidate by Name", value="")
    
    min_score = st.sidebar.slider("🎯 Minimum Match Score (%)", min_value=0.0, max_value=100.0, value=0.0, step=5.0)
    
    status_options = ["Excellent", "Good", "Average", "Needs Improvement"]
    selected_statuses = st.sidebar.multiselect("🏷️ Filter by Status", options=status_options, default=status_options)
    
    sort_option = st.sidebar.selectbox("⇅ Sort Candidates By", options=["Score (High to Low)", "Score (Low to High)", "Name (A-Z)"])
    
    # Apply filtering
    filtered_data = []
    for item in st.session_state.rankings:
        # Search filter
        if search_query and search_query.lower() not in item["name"].lower():
            continue
        # Score filter
        if item["score"] < min_score:
            continue
        # Status filter
        if item["status"] not in selected_statuses:
            continue
        filtered_data.append(item)
        
    # Apply sorting
    if sort_option == "Score (High to Low)":
        filtered_data.sort(key=lambda x: x["score"], reverse=True)
    elif sort_option == "Score (Low to High)":
        filtered_data.sort(key=lambda x: x["score"])
    elif sort_option == "Name (A-Z)":
        filtered_data.sort(key=lambda x: x["name"])

    # 2. RENDER KPI CARDS
    # Gather statistics
    total_uploaded = len(st.session_state.processed_resumes) + len(st.session_state.failures)
    total_processed = len(st.session_state.processed_resumes)
    shortlisted_candidates = len([r for r in st.session_state.rankings if r["score"] >= 75.0])
    
    if total_processed > 0:
        scores = [r["score"] for r in st.session_state.rankings]
        max_score = max(scores)
        min_score_val = min(scores)
        avg_score = round(np.mean(scores), 2)
        top_cand = st.session_state.rankings[0]["name"]
    else:
        max_score = 0.0
        min_score_val = 0.0
        avg_score = 0.0
        top_cand = "N/A"
        
    st.markdown("### 📊 Recruitment Campaign Summary")
    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5, metric_col6 = st.columns(6)
    
    with metric_col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Resumes</div>
                <div class="metric-value">{total_uploaded}</div>
                <div class="metric-sub">{total_processed} parsed, {len(st.session_state.failures)} failed</div>
            </div>
        """, unsafe_allow_html=True)
        
    with metric_col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Shortlisted</div>
                <div class="metric-value">{shortlisted_candidates}</div>
                <div class="metric-sub">Score &ge; 75% (Good/Excel)</div>
            </div>
        """, unsafe_allow_html=True)
        
    with metric_col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Top Candidate</div>
                <div class="metric-value" style="font-size: 1.25rem; line-height: 1.5; padding-top: 0.5rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{top_cand}</div>
                <div class="metric-sub">Ranked 🥇 overall</div>
            </div>
        """, unsafe_allow_html=True)
        
    with metric_col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Highest Score</div>
                <div class="metric-value">{max_score}%</div>
                <div class="metric-sub">Best JD Match</div>
            </div>
        """, unsafe_allow_html=True)
        
    with metric_col5:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Average Score</div>
                <div class="metric-value">{avg_score}%</div>
                <div class="metric-sub">Across all parsed</div>
            </div>
        """, unsafe_allow_html=True)
        
    with metric_col6:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Lowest Score</div>
                <div class="metric-value">{min_score_val}%</div>
                <div class="metric-sub">Needs Improvement</div>
            </div>
        """, unsafe_allow_html=True)

    # 3. INTERACTIVE TABS
    tab_dashboard, tab_details, tab_charts, tab_exports, tab_errors = st.tabs([
        "📋 Recruiter Dashboard Table", 
        "🔍 Candidate Skill Gap Inspector", 
        "📈 Visualizations & Analytics", 
        "📥 Export Reports", 
        "⚠️ Parser Diagnostics"
    ])
    
    with tab_dashboard:
        st.subheader("Candidate Rankings")
        
        if not filtered_data:
            st.info("No candidates match your sidebar filter settings. Try adjusting the search text, score threshold, or statuses.")
        else:
            # We map variables to a DataFrame and use Streamlit's new premium st.dataframe configs
            display_rows = []
            for item in filtered_data:
                display_rows.append({
                    "Rank": item["rank"],
                    "Candidate Name": item["name"],
                    "Resume Filename": item["filename"],
                    "Match Score": item["score"] / 100.0, # ProgressColumn expects value between 0.0 and 1.0
                    "Status": item["status"],
                    "Matched Skills": ", ".join(item["matched_skills"]),
                    "Missing Skills": ", ".join(item["missing_skills"])
                })
            
            df_display = pd.DataFrame(display_rows)
            
            # Interactive styling of columns
            st.dataframe(
                df_display,
                column_config={
                    "Rank": st.column_config.TextColumn("Rank", width="small"),
                    "Candidate Name": st.column_config.TextColumn("Candidate Name", width="medium"),
                    "Resume Filename": st.column_config.TextColumn("Resume File", width="medium"),
                    "Match Score": st.column_config.ProgressColumn("Match Score", help="TF-IDF Cosine Similarity percentage", format="%.2f%%", min_value=0.0, max_value=1.0),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Matched Skills": st.column_config.TextColumn("Matched Skills", width="large"),
                    "Missing Skills": st.column_config.TextColumn("Missing Skills", width="large"),
                },
                hide_index=True,
                width="stretch"
            )
            
    with tab_details:
        st.subheader("Detailed Candidate Profile & Skill Gap Analysis")
        
        if not st.session_state.rankings:
            st.write("No candidate evaluations available.")
        else:
            # Dropdown selection of candidates
            candidate_names = [f"{c['name']} ({c['filename']})" for c in st.session_state.rankings]
            selected_cand_idx = st.selectbox("Select Candidate to Inspect:", range(len(candidate_names)), format_func=lambda x: candidate_names[x])
            
            cand = st.session_state.rankings[selected_cand_idx]
            
            # Drill down UI
            det_col1, det_col2 = st.columns([1, 2], gap="large")
            
            with det_col1:
                # Radial Gauges/Scores
                st.markdown(f"### {cand['name']}")
                st.markdown(f"**Resume File:** `{cand['filename']}`")
                
                # Format color based on status
                color_map = {
                    "Excellent": "#DEF7EC",
                    "Good": "#E1EFFE",
                    "Average": "#FEF08A",
                    "Needs Improvement": "#FDE8E8"
                }
                text_color_map = {
                    "Excellent": "#03543F",
                    "Good": "#1E429F",
                    "Average": "#713F12",
                    "Needs Improvement": "#9B1C1C"
                }
                
                status_color = color_map.get(cand["status"], "#FFFFFF")
                status_text_color = text_color_map.get(cand["status"], "#000000")
                
                st.markdown(f"""
                    <div style="background-color: {status_color}; border-radius: 8px; padding: 1rem; border: 1px solid #E2E8F0; text-align: center; margin-bottom: 1.5rem;">
                        <h4 style="margin:0; color: {status_text_color}; font-size: 0.9rem; text-transform: uppercase;">Evaluation Status</h4>
                        <h2 style="margin: 0.2rem 0; color: {status_text_color}; font-size: 2.2rem; font-weight: 800;">{cand['status']}</h2>
                        <h3 style="margin:0; color: #4A5568; font-size: 1.25rem;">Score: {cand['score']}%</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # Score bar
                st.write("Match Percentage Gauge:")
                st.progress(cand["score"]/100.0)
                
            with det_col2:
                st.markdown("### Skill Analysis")
                
                # Matched Skills
                st.markdown("#### ✅ Matched Skills (Requested & Found)")
                if cand["matched_skills"]:
                    badges = "".join([f'<span class="skill-badge badge-matched">{s}</span>' for s in cand["matched_skills"]])
                    st.markdown(badges, unsafe_allow_html=True)
                else:
                    st.info("No matching skills identified.")
                    
                # Missing Skills
                st.markdown("#### ❌ Missing Skills (Requested in JD, Not in Resume)")
                if cand["missing_skills"]:
                    badges = "".join([f'<span class="skill-badge badge-missing">{s}</span>' for s in cand["missing_skills"]])
                    st.markdown(badges, unsafe_allow_html=True)
                else:
                    st.success("No missing skills! Excellent match for job description.")
                    
                # Additional Skills
                st.markdown("#### ➕ Additional Skills (In Resume, Not Requested in JD)")
                if cand["additional_skills"]:
                    badges = "".join([f'<span class="skill-badge badge-additional">{s}</span>' for s in cand["additional_skills"]])
                    st.markdown(badges, unsafe_allow_html=True)
                else:
                    st.info("No additional skills detected.")
            
            st.markdown("---")
            with st.expander("📄 Preview Extracted Resume Text"):
                st.text_area("Extracted Plain Text:", value=cand["text"], height=300, disabled=True)
                
    with tab_charts:
        st.subheader("Analytics & Visualizations")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # 1. Match Score Bar Chart
            st.markdown("#### Candidate Match Scores")
            bar_df = pd.DataFrame(st.session_state.rankings)
            fig_bar = px.bar(
                bar_df, 
                x="score", 
                y="name", 
                orientation="h",
                text="score",
                labels={"score": "Match Score (%)", "name": "Candidate Name"},
                color="score",
                color_continuous_scale="Blues",
                title="Match Score Comparison (Highest to Lowest)"
            )
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=400, margin=dict(l=20, r=20, t=40, b=20))
            fig_bar.update_traces(texttemplate='%{text}%', textposition='outside')
            st.plotly_chart(fig_bar, width="stretch")
            
        with chart_col2:
            # 2. Status Donut Chart
            st.markdown("#### Candidate Status Breakdown")
            status_counts = bar_df["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            
            # Map statuses to standard recruitment colors
            color_discrete_map = {
                "Excellent": "#22C55E",
                "Good": "#3B82F6",
                "Average": "#EAB308",
                "Needs Improvement": "#EF4444"
            }
            
            fig_pie = px.pie(
                status_counts, 
                values="Count", 
                names="Status", 
                hole=0.4,
                color="Status",
                color_discrete_map=color_discrete_map,
                title="Evaluation Status Breakdown"
            )
            fig_pie.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_pie, width="stretch")
            
        st.markdown("---")
        
        # 3. Common Skills Frequency distribution chart
        st.markdown("#### Common Skills Distribution")
        all_matched_skills = []
        for c in st.session_state.rankings:
            all_matched_skills.extend(c["matched_skills"])
            
        if all_matched_skills:
            skill_counts = pd.Series(all_matched_skills).value_counts().reset_index()
            skill_counts.columns = ["Skill", "Frequency"]
            
            fig_skills = px.bar(
                skill_counts,
                x="Skill",
                y="Frequency",
                text="Frequency",
                labels={"Skill": "Skill Name", "Frequency": "Count of Candidates"},
                title="Which requested skills are most common among candidates?",
                color="Frequency",
                color_continuous_scale="Viridis"
            )
            fig_skills.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_skills, width="stretch")
        else:
            st.info("No matching skills found across any candidates to visualize.")

    with tab_exports:
        st.subheader("Export Evaluation Reports")
        st.write("Generate and download candidate rankings, scores, and skills analysis in CSV or Excel format.")
        
        csv_data = export_to_csv(st.session_state.rankings)
        excel_data = export_to_excel(st.session_state.rankings)
        
        exp_col1, exp_col2 = st.columns(2)
        
        with exp_col1:
            st.markdown("""
                <div style="background-color: white; border-radius: 8px; padding: 1.5rem; border: 1px solid #E2E8F0; text-align: center;">
                    <h3>📄 Export as CSV</h3>
                    <p style="color: #64748B; font-size: 0.9rem;">Clean, comma-separated format. Best for loading into other ATS tools, databases, or writing scripts.</p>
                </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label="📥 Download CSV Report",
                data=csv_data,
                file_name="ATS_Candidate_Ranking_Report.csv",
                mime="text/csv",
                width="stretch"
            )
            
        with exp_col2:
            st.markdown("""
                <div style="background-color: white; border-radius: 8px; padding: 1.5rem; border: 1px solid #E2E8F0; text-align: center;">
                    <h3>📊 Export as Excel (XLSX)</h3>
                    <p style="color: #64748B; font-size: 0.9rem;">Formatted spreadsheet with sheet worksheets, auto-adjusted column widths, and tabular headers.</p>
                </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label="📥 Download Excel Report",
                data=excel_data,
                file_name="ATS_Candidate_Ranking_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )
            
    with tab_errors:
        st.subheader("Parser Diagnostics & Errors")
        st.write("Review diagnostics for any PDF files that failed to read or parse.")
        
        if not st.session_state.failures:
            st.success("✅ All uploaded PDF files were successfully parsed! No diagnostics errors.")
        else:
            st.warning(f"⚠️ {len(st.session_state.failures)} file(s) failed during parser extraction:")
            
            fail_df = pd.DataFrame(st.session_state.failures)
            fail_df.columns = ["Filename", "Error Message Details"]
            
            st.table(fail_df)
            st.markdown("""
                > **Tip for Recruiters:** 
                > - **Scanned / Image-Only PDFs:** The parser is text-based. If a resume is scanned (image only), it will contain no selectable text. Ensure applicants submit text-based PDFs.
                > - **Corrupted PDFs:** Ensure files are not corrupted and open properly in standard PDF viewers (like Adobe Acrobat or Google Chrome).
            """)
else:
    # Guidelines for when no analysis has been run
    st.info("💡 To begin screening, paste a job description on the left, upload candidate PDF resumes on the right, and click the **Analyze & Rank Resumes** button.")
