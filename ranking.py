import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skill_extractor import extract_skills_from_text, analyze_skills

def calculate_match_scores(job_description: str, resumes: list) -> list:
    """
    Computes TF-IDF cosine similarity scores between the job description and multiple resumes,
    extracts/analyzes skills, assigns ranks, medals, and statuses.
    
    Args:
        job_description (str): The text of the job description.
        resumes (list): List of dicts, where each dict contains:
                        - "name": Candidate's name
                        - "filename": Resume filename
                        - "text": Cleaned resume text
                        
    Returns:
        list: Sorted list of candidate rankings with scores, statuses, and skill analyses.
    """
    if not job_description.strip() or not resumes:
        return []

    # 1. Extract skills from the job description
    jd_skills = extract_skills_from_text(job_description)

    # 2. Vectorize using TF-IDF
    # We combine job description and all resumes into one corpus for vectorization
    corpus = [job_description] + [r["text"] for r in resumes]
    
    vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except Exception:
        # Fallback if corpus is empty or has no words scikit-learn can extract
        return []

    # job_description is the first row
    jd_vector = tfidf_matrix[0:1]
    
    results = []
    
    # Compare each resume (row 1 to N) with the job description (row 0)
    for idx, resume in enumerate(resumes):
        resume_vector = tfidf_matrix[idx + 1 : idx + 2]
        
        # Calculate cosine similarity
        sim_score = cosine_similarity(jd_vector, resume_vector)[0][0]
        
        # Convert to percentage and round to 2 decimal places
        match_percentage = round(float(sim_score) * 100, 2)
        
        # Determine status based on score
        if match_percentage >= 90.0:
            status = "Excellent"
        elif match_percentage >= 75.0:
            status = "Good"
        elif match_percentage >= 60.0:
            status = "Average"
        else:
            status = "Needs Improvement"
            
        # Extract skills for this resume
        resume_skills = extract_skills_from_text(resume["text"])
        skill_analysis = analyze_skills(resume_skills, jd_skills)
        
        results.append({
            "name": resume["name"],
            "filename": resume["filename"],
            "score": match_percentage,
            "status": status,
            "matched_skills": skill_analysis["matched"],
            "missing_skills": skill_analysis["missing"],
            "additional_skills": skill_analysis["additional"],
            "text": resume["text"]
        })
        
    # 3. Sort by score in descending order
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # 4. Assign ranks and medals
    for rank_idx, item in enumerate(results):
        rank = rank_idx + 1
        item["rank_number"] = rank
        
        # Assign medals/rank formatting
        if rank == 1:
            item["rank"] = "🥇 Rank 1"
        elif rank == 2:
            item["rank"] = "🥈 Rank 2"
        elif rank == 3:
            item["rank"] = "🥉 Rank 3"
        else:
            item["rank"] = f"Rank {rank}"
            
    return results
