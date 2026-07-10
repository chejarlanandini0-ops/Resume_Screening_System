# AI-Powered Resume Screening and Candidate Ranking System

An AI-driven Applicant Tracking System (ATS) dashboard designed for recruiters to automate screening, extract technical and soft skills, map candidate skill gaps, rank applicants objectively, and visualize statistics of recruitment campaigns.

Built with **Python**, **Streamlit**, **scikit-learn**, **Pandas**, **PyPDF2**, and **Plotly**.

---

## 🌟 Key Features

1. **Recruiter Dashboard**: Displays high-level KPIs including total resumes uploaded, shortlisted candidate counts (scores &ge; 75%), highest, lowest, and average matching scores, and the name of the top-ranked candidate.
2. **Text Parsing & Cleansing**: Extracts raw text from PDF files using `PyPDF2` and normalizes whitespace/newlines.
3. **Smart Name Extraction**: Employs a multi-step heuristic parser that filters out contact details (emails, phone numbers, URLs) and looks at early resume lines to determine candidate names. Falls back to a formatted version of the file name if no name is clearly detected.
4. **AI Match Engine**: Calculates TF-IDF vectors for the job description and candidate resumes, computing a similarity percentage using **Cosine Similarity**.
5. **Categorized Candidate Ranking**: Ranks candidates from highest to lowest score, awards medals (🥇, 🥈, 🥉) to the top three, and labels candidates with status badges:
   * **Excellent** (90–100%)
   * **Good** (75–89%)
   * **Average** (60–74%)
   * **Needs Improvement** (Below 60%)
6. **Detailed Skill Gap Analysis**: Maps candidate skills against the job description to show:
   * **Matched Skills** (Green badges)
   * **Missing Skills** (Red badges)
   * **Additional Skills** (Blue badges)
7. **Interactive Filters**: Refine the Recruiter Table in real-time by searching for candidate names, setting a minimum score threshold, selecting specific statuses, or sorting.
8. **Campaign Visualizations**: Provides rich interactive Plotly charts showing match score distributions, candidate evaluation statuses, and a frequency breakdown of skills across the applicant pool.
9. **Dual Format Report Export**: Download candidate tables as raw **CSV** files or professionally-styled **Excel** sheets (with auto-fitting column dimensions).
10. **Error and Duplicate Handling**: Detects duplicate file uploads and handles scanned or corrupted PDFs gracefully, showing detailed error descriptions in a diagnostic tab.

---

## 📁 Project Structure

```
AI_Resume_Screening/
│── app.py                  # Streamlit application UI, dashboard, layouts, charts, and exports
│── resume_parser.py        # PDF text extractor and heuristic name finder
│── skill_extractor.py      # Predefined skills list and keyword extractor (with boundary safety)
│── ranking.py              # TF-IDF Vectorization and Cosine Similarity evaluation module
│── utils.py                # Exporter helpers (Excel/CSV) and sample JDs
│── generate_samples.py     # Script to generate realistic mock PDF resumes for instant testing
│── requirements.txt        # Project dependencies (streamlit, pandas, PyPDF2, etc.)
│── README.md               # User guide & documentation (this file)
│── sample_resumes/         # Local folder storing generated sample resumes
```

---

## ⚙️ Installation & Setup

Follow these steps to run the application locally:

### 1. Prerequisite Check
Ensure you have **Python 3.8+** installed on your system.

### 2. Clone or Copy the Repository
Place the folder `AI_Resume_Screening/` onto your computer. Open a terminal or PowerShell in that directory.

### 3. Create a Virtual Environment
Create an isolated environment to manage dependencies:
```bash
# On Windows (PowerShell)
python -m venv .venv

# On macOS/Linux
python3 -m venv .venv
```

### 4. Activate the Virtual Environment
```bash
# On Windows (PowerShell)
.venv\Scripts\Activate.ps1

# On Windows (Command Prompt)
.venv\Scripts\activate.bat

# On macOS/Linux
source .venv/bin/activate
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

### 6. Generate Sample Resumes (Optional but Recommended)
Run the programmatic resume generator script to automatically populate your `sample_resumes/` folder with 5 realistic candidate resumes, 1 corrupted PDF, and 1 scanned/empty PDF for immediate testing:
```bash
python generate_samples.py
```

---

## 🚀 Running the Application

Launch the Streamlit web dashboard:
```bash
streamlit run app.py
```
A browser tab should open automatically to `http://localhost:8501`. If it does not, copy the link from your terminal.

---

## 💡 How it Works Under the Hood

1. **Text Cleansing**: Resumes contain varied text patterns. The parsing module extracts raw text and strips out formatting anomalies, non-standard spaces, and duplicate blank lines.
2. **Skill Boundary Matching**: Regular expressions are used to match skills like `C++`, `C#`, and `.NET` without running into boundary failures. Alphanumeric skills (e.g. `Go`, `Git`, `Java`) are matched using strict word boundaries to avoid false positives (e.g., preventing "Go" from matching inside "government").
3. **TF-IDF Vectorization**: Streamlit loads the job description and all resumes. We feed this combined text corpus into scikit-learn's `TfidfVectorizer`, converting text into vector representations of word frequencies.
4. **Cosine Similarity**: Cosine similarity is computed between the job description vector and each resume vector, which measures the angle between the documents. This returns a score from `0.0` to `1.0` representing overlap independent of document length, which we scale to `0%` to `100%`.
