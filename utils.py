import io
import pandas as pd

SAMPLE_JOB_DESCRIPTIONS = {
    "Python / Full-Stack Engineer": (
        "Job Title: Python / Full-Stack Engineer\n\n"
        "Job Description:\n"
        "We are looking for a skilled Python / Full-Stack Developer to join our growing engineering team. "
        "In this role, you will design, build, and maintain efficient, reusable, and reliable Python code "
        "for our backend APIs, and develop clean, interactive interfaces on the frontend. "
        "You will collaborate closely with product managers and other developers to build new features and optimize performance.\n\n"
        "Required Technical Skills:\n"
        "- Programming Languages: Python, JavaScript, HTML, CSS\n"
        "- Backend Frameworks: Django, Flask, REST API\n"
        "- Frontend Technologies: React, Bootstrap\n"
        "- Databases: SQL, PostgreSQL, MySQL\n"
        "- DevOps & Tools: Git, GitHub, Docker, AWS\n\n"
        "Soft Skills & Competencies:\n"
        "- Communication, Problem Solving, Teamwork, and Time Management.\n"
        "- Ability to work in an Agile environment using Scrum methodologies.\n\n"
        "Responsibilities:\n"
        "- Develop backend logic and integrate with frontend UI elements.\n"
        "- Create secure REST APIs and connect databases.\n"
        "- Troubleshoot, debug, and optimize application performance.\n"
        "- Participate in code reviews and support continuous integration (CI/CD) pipelines."
    ),
    
    "Data Scientist / AI Engineer": (
        "Job Title: Data Scientist / AI Engineer\n\n"
        "Job Description:\n"
        "We are seeking an experienced Data Scientist / AI Engineer to help us design and implement intelligent systems. "
        "You will analyze complex datasets, build predictive machine learning models, and deploy deep learning algorithms. "
        "You should have strong Python scripting skills, a solid understanding of statistical models, and experience working "
        "with large-scale data systems. You will work with cross-functional teams to translate business problems into data-driven solutions.\n\n"
        "Required Technical Skills:\n"
        "- Languages & Core Libraries: Python, R, SQL, NumPy, Pandas\n"
        "- AI & Machine Learning: Machine Learning, Deep Learning, Artificial Intelligence, Data Science, Scikit-learn, TensorFlow, PyTorch\n"
        "- Data Visualization: Power BI, Tableau, Excel\n"
        "- Cloud & DevOps: Git, GitHub, Docker, Kubernetes, Azure, AWS\n\n"
        "Soft Skills & Competencies:\n"
        "- Leadership, Communication, Problem Solving, and Critical Thinking.\n"
        "- Ability to communicate complex technical concepts to non-technical stakeholders.\n\n"
        "Responsibilities:\n"
        "- Preprocess structured and unstructured data, performing exploratory data analysis (EDA).\n"
        "- Train, evaluate, and fine-tune machine learning and deep learning models.\n"
        "- Deploy models as APIs and monitor their performance in production.\n"
        "- Collaborate with business stakeholders to discover trends and insights."
    ),
    
    "Product Manager": (
        "Job Title: Product Manager\n\n"
        "Job Description:\n"
        "We are looking for a product manager to lead the strategy, roadmap, and feature definition for our software products. "
        "You will coordinate with engineering, design, marketing, and sales to launch high-impact products. "
        "You will gather user feedback, define product requirements, and analyze product performance using metrics.\n\n"
        "Required Technical Skills & Tools:\n"
        "- General Tech Knowledge: SQL, Git, Excel, Jira, Scrum, Agile\n"
        "- Business Intelligence: Power BI, Tableau, Data Analysis\n\n"
        "Soft Skills & Competencies:\n"
        "- Leadership, Communication, Teamwork, Presentation, Time Management, Negotiation, and Decision Making.\n"
        "- High emotional intelligence and adaptability.\n\n"
        "Responsibilities:\n"
        "- Define product vision, strategy, and roadmap based on market research.\n"
        "- Write detailed product requirement documents (PRDs) and user stories.\n"
        "- Prioritize engineering backlogs and oversee sprints using Jira.\n"
        "- Present product updates to stakeholders and gather user feedback."
    )
}

def export_to_csv(data: list) -> str:
    """
    Exports candidate ranking list to CSV format.
    """
    if not data:
        return ""
        
    export_data = []
    for item in data:
        export_data.append({
            "Rank": item.get("rank_number"),
            "Candidate Name": item.get("name"),
            "Resume File": item.get("filename"),
            "Match Score (%)": item.get("score"),
            "Status": item.get("status"),
            "Matched Skills": ", ".join(item.get("matched_skills", [])),
            "Missing Skills": ", ".join(item.get("missing_skills", [])),
            "Additional Skills": ", ".join(item.get("additional_skills", []))
        })
    df = pd.DataFrame(export_data)
    return df.to_csv(index=False)

def export_to_excel(data: list) -> bytes:
    """
    Exports candidate ranking list to Excel format as a bytes object.
    """
    if not data:
        return b""
        
    export_data = []
    for item in data:
        export_data.append({
            "Rank": item.get("rank_number"),
            "Candidate Name": item.get("name"),
            "Resume File": item.get("filename"),
            "Match Score (%)": item.get("score"),
            "Status": item.get("status"),
            "Matched Skills": ", ".join(item.get("matched_skills", [])),
            "Missing Skills": ", ".join(item.get("missing_skills", [])),
            "Additional Skills": ", ".join(item.get("additional_skills", []))
        })
    df = pd.DataFrame(export_data)
    
    # Save to binary stream
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='ATS Rankings')
        
        # Access the openpyxl workbook and worksheet to do formatting if desired
        workbook = writer.book
        worksheet = writer.sheets['ATS Rankings']
        
        # Simple auto-adjust columns width
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 10)
            
    return output.getvalue()
