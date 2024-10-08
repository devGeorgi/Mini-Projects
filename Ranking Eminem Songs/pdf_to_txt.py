import pdfplumber

def pdf_to_text(pdf_path, txt_path, skip_lines=11):
    # Open the PDF file using pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        # Open the text file in write mode
        with open(txt_path, 'w', encoding='utf-8') as text_file:
            # Initialize a line counter
            line_counter = 0
            
            # Loop through each page in the PDF
            for page in pdf.pages:
                # Extract the text for the page
                page_text = page.extract_text()
                if page_text:  # Ensure the page has text
                    # Split the text into lines
                    lines = page_text.splitlines()
                    
                    # Process each line
                    for line in lines:
                        line_counter += 1
                        if line_counter > skip_lines:  # Start writing when the songs start
                            text_file.write(line + "\n")

    print(f"txt file ready")

# 
pdf_path = 'Ranking Eminem Songs/spotify_songs.pdf'  # Path to the PDF file
txt_path = 'Ranking Eminem Songs/spotify_songs.txt'   # Path to the txt file

pdf_to_text(pdf_path, txt_path)
