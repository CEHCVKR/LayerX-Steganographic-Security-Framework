import fitz  # PyMuPDF

# Open the PDF
pdf_document = fitz.open("TEAM_08_Abstract.pdf")

# Extract text from all pages
full_text = ""
for page_num in range(len(pdf_document)):
    page = pdf_document.load_page(page_num)
    full_text += page.get_text()

pdf_document.close()

print(full_text)