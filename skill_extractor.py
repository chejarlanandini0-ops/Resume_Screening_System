import re

# Comprehensive list of standard technical and soft skills
DEFAULT_SKILLS = [
    # Programming Languages
    "Python", "Java", "C", "C++", "C#", "Ruby", "Go", "Rust", "Swift", "Kotlin", "PHP", 
    "JavaScript", "TypeScript", "R", "MATLAB", "Perl", "Scala", "Dart", "Haskell",
    
    # Web & Application Development
    "HTML", "CSS", "React", "Angular", "Vue", "Node.js", "Spring Boot", "Django", "Flask", 
    "Express", "ASP.NET", "Ruby on Rails", "jQuery", "Svelte", "Next.js", "Bootstrap", 
    "Tailwind", "TailwindCSS", "FastAPI", "GraphQL", "REST API", "Microservices",
    
    # Databases & Big Data
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "SQLite", "Cassandra", 
    "Neo4j", "MariaDB", "Elasticsearch", "Firebase", "DynamoDB", "Pandas", "NumPy", 
    "Spark", "Hadoop", "Hive", "Kafka", "Data Warehousing",
    
    # AI / ML / Data Science
    "Machine Learning", "Deep Learning", "Artificial Intelligence", "Data Science", 
    "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "NLP", "Natural Language Processing", 
    "Computer Vision", "LLMs", "Generative AI", "Data Analysis", "Statistics",
    "OpenCV", "Reinforcement Learning", "Neural Networks",
    
    # Cloud & DevOps & Tools
    "Git", "GitHub", "GitLab", "Docker", "Kubernetes", "AWS", "Azure", "GCP", 
    "Google Cloud Platform", "Jenkins", "Terraform", "Ansible", "CI/CD", "Linux", 
    "Unix", "Power BI", "Excel", "Tableau", "Jira", "Confluence", "Agile", "Scrum",
    
    # Soft Skills
    "Communication", "Leadership", "Teamwork", "Problem Solving", "Time Management", 
    "Critical Thinking", "Project Management", "Negotiation", "Presentation", 
    "Adaptability", "Collaboration", "Creativity", "Emotional Intelligence", 
    "Conflict Resolution", "Decision Making", "Active Listening", "Work Ethic"
]

def get_skill_pattern(skill: str) -> str:
    """
    Creates a regular expression pattern for a skill, handling boundaries correctly
    even for special characters (like C++, C#, Node.js, .NET).
    """
    # Escape special characters
    escaped = re.escape(skill)
    
    # Determine boundaries based on starting and ending characters of the skill
    # If the skill starts with a word character, use word boundary '\b', otherwise verify it's preceded by whitespace, punctuation, or start of string
    start_boundary = r'\b' if re.match(r'^\w', skill) else r'(?:\s|[.,;!?()"\']|^)'
    
    # If the skill ends with a word character, use word boundary '\b', otherwise verify it's followed by whitespace, punctuation, or end of string
    end_boundary = r'\b' if re.match(r'\w$', skill) else r'(?:\s|[.,;!?()"\']|$)'
    
    return rf'{start_boundary}{escaped}{end_boundary}'

def extract_skills_from_text(text: str, skills_list: list = None) -> set:
    """
    Extracts skills from text using case-insensitive keyword matching with boundary checking.
    
    Args:
        text (str): The text to extract skills from.
        skills_list (list, optional): Custom list of skills. Defaults to DEFAULT_SKILLS.
        
    Returns:
        set: A set of matched skills (in their original case from the skills list).
    """
    if not text:
        return set()
        
    if skills_list is None:
        skills_list = DEFAULT_SKILLS
        
    matched_skills = set()
    
    # We clean the text slightly to make spacing uniform, but keep punctuation for boundaries
    cleaned_text = re.sub(r'\s+', ' ', text)
    
    for skill in skills_list:
        pattern = get_skill_pattern(skill)
        # Search using case-insensitive regex
        if re.search(pattern, cleaned_text, re.IGNORECASE):
            matched_skills.add(skill)
            
    return matched_skills

def analyze_skills(resume_skills: set, jd_skills: set) -> dict:
    """
    Compares resume skills against job description skills and returns:
    - Matched Skills: Skills requested in the JD and present in the resume.
    - Missing Skills: Skills requested in the JD but not present in the resume.
    - Additional Skills: Skills present in the resume but not requested in the JD.
    
    Args:
        resume_skills (set): Skills found in the resume.
        jd_skills (set): Skills found in the job description.
        
    Returns:
        dict: Lists of matched, missing, and additional skills.
    """
    matched = resume_skills.intersection(jd_skills)
    missing = jd_skills.difference(resume_skills)
    additional = resume_skills.difference(jd_skills)
    
    return {
        "matched": sorted(list(matched)),
        "missing": sorted(list(missing)),
        "additional": sorted(list(additional))
    }
