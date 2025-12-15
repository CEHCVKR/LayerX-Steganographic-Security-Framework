import sys
import os

try:
    import fitz  # PyMuPDF
    doc = fitz.open('TEAM_08_Abstract.pdf')
    text = ""
    for page in doc:
        text += page.get_text()
    print(text)
except ImportError:
    try:
        import PyPDF2
        with open('TEAM_08_Abstract.pdf', 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        print(text)
    except ImportError:
        print("Please install PyMuPDF: pip install pymupdf")
        print("Or install PyPDF2: pip install PyPDF2")