import re
import os
import PyPDF2

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts and cleans text from a PDF file object or file path.
    
    Args:
        pdf_file: File path or file-like object representing the PDF.
        
    Returns:
        str: Extracted and cleaned text.
        
    Raises:
        ValueError: If the PDF is corrupted or empty.
    """
    text_content = []
    try:
        # Check if pdf_file is a path or file-like object
        reader = PyPDF2.PdfReader(pdf_file)
        
        # Check for encryption or empty pages
        if len(reader.pages) == 0:
            raise ValueError("The PDF file contains no pages.")
            
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
                
        full_text = "\n".join(text_content)
        
        if not full_text.strip():
            raise ValueError("No text could be extracted from the PDF pages. It might be scanned or image-only.")
            
        return clean_text(full_text)
        
    except Exception as e:
        # Wrap any PyPDF2 or other errors in a descriptive ValueError
        raise ValueError(f"Error parsing PDF file: {str(e)}")

def clean_text(text: str) -> str:
    """
    Cleans raw text by removing excessive whitespace, normalizing newlines, and filtering out non-printable characters.
    """
    if not text:
        return ""
    
    # Replace non-breaking spaces and zero-width spaces
    text = text.replace('\xa0', ' ').replace('\u200b', '')
    
    # Normalize newlines
    text = re.sub(r'\r\n|\r', '\n', text)
    
    # Replace multiple consecutive spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Replace 3 or more consecutive newlines with 2 newlines (preserve paragraphs)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def extract_name(text: str, filename: str) -> str:
    """
    Extracts the candidate's name from the resume text using heuristic rules.
    Falls back to the filename (properly formatted) if no name is detected in the text.
    
    Args:
        text (str): Cleaned resume text.
        filename (str): Original filename of the resume.
        
    Returns:
        str: Candidate name.
    """
    # 1. Clean the filename to establish a good fallback
    fallback_name = os.path.basename(filename)
    # Remove extension
    fallback_name = os.path.splitext(fallback_name)[0]
    # Replace hyphens, underscores, dots, and encoded spaces with spaces
    fallback_name = re.sub(r'[-_.]|%20', ' ', fallback_name)
    # Remove words like resume, cv, portfolio, profile, etc.
    fallback_name = re.sub(r'(?i)\b(resume|cv|portfolio|profile|latest|cv_resume|copy|draft|v\d+)\b', '', fallback_name)
    # Clean up whitespace
    fallback_name = re.sub(r'\s+', ' ', fallback_name).strip()
    # Title case the name
    fallback_name = fallback_name.title() if fallback_name else "Unknown Candidate"

    # If the text is empty, return the fallback name immediately
    if not text:
        return fallback_name

    # 2. Heuristics to find name in the text
    # Split text into lines and clean them
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Patterns to exclude lines
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pattern = r'\+?\d[\d\-\s\(\)]{8,}\d'
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+|linkedin\.com/in/[^\s]+|github\.com/[^\s]+)'
    
    # Check first 6 lines
    for line in lines[:6]:
        # Skip if contains contact info
        if re.search(email_pattern, line) or re.search(phone_pattern, line) or re.search(url_pattern, line):
            continue
            
        # Skip if contains typical headers, keywords or section titles
        lower_line = line.lower()
        ignore_keywords = [
            "resume", "curriculum", "vitae", "summary", "profile", "contact", 
            "experience", "education", "skills", "address", "phone", "email", 
            "page", "objective", "about", "github", "linkedin", "developer",
            "engineer", "designer", "specialist", "professional", "certified"
        ]
        if any(keyword in lower_line for keyword in ignore_keywords):
            continue
            
        # A name line should typically:
        # - Be 2 to 4 words
        # - Contain only letters, spaces, dots, or hyphens
        # - Have title case (e.g. John Doe, Sarah J. Connor)
        words = line.split()
        if 2 <= len(words) <= 4:
            # Check characters (letters, spaces, dots, hyphens only)
            if re.match(r'^[a-zA-Z\s.-]+$', line):
                # Check if most words start with capital letters
                cap_words = [w for w in words if w[0].isupper() or w[0] in '.-']
                if len(cap_words) >= len(words) - 1: # allow one non-cap word (like 'von', 'de', 'du', 'and', 'the')
                    # Standardize whitespace and return
                    return re.sub(r'\s+', ' ', line).strip().title()
                    
    # Return the fallback filename-derived name if text heuristics failed
    return fallback_name
