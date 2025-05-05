# --- START OF REVISED FILE pdf_to_txt.py ---

import pdfplumber
import re
import os

# --- Combined PDF processing and rank-space correction ---
def pdf_to_formatted_txt(pdf_path, output_txt_path, skip_lines=11):
    """
    Converts PDF to a text file, skipping initial lines AND
    inserting a space after the expected rank number if it's missing.
    Writes directly to the final output file.
    """
    expected_rank = 1
    line_counter = 0
    warnings = 0
    lines_written = 0

    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_txt_path)
        if output_dir and not os.path.exists(output_dir):
             os.makedirs(output_dir)
             print(f"Created directory: {output_dir}")

        # Open the PDF file and the final output text file
        with pdfplumber.open(pdf_path) as pdf, \
             open(output_txt_path, 'w', encoding='utf-8') as text_file:

            print(f"Processing '{pdf_path}' to create '{output_txt_path}'...")

            first_line_written = False # To handle skipping leading blanks after header

            # Loop through each page in the PDF
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:  # Ensure the page has text
                    raw_lines = page_text.splitlines()

                    # Process each line from the page
                    for line in raw_lines:
                        line_counter += 1

                        # Skip header lines
                        if line_counter <= skip_lines:
                            continue

                        # --- Start processing lines intended for the file ---
                        original_line = line # Keep for potential warnings
                        line = line.strip() # Work with the stripped version for logic

                        # Skip blank lines that might appear immediately after the header
                        if not line and not first_line_written:
                            continue

                        # Keep blank lines that appear *within* the song list
                        if not line and first_line_written:
                             text_file.write("\n")
                             # lines_written += 1 # Don't count blank lines? Or do? Let's not.
                             continue

                        # --- Apply Preprocessing Logic (Adding Space) ---
                        rank_str = str(expected_rank)
                        processed_line = None # Flag / placeholder for the line to write

                        # Check if the line starts with the expected rank number
                        if line.startswith(rank_str):
                            # Check if space is missing right after the rank
                            if len(line) > len(rank_str) and not line[len(rank_str)].isspace():
                                # Insert the space
                                processed_line = rank_str + " " + line[len(rank_str):]
                                # print(f"Debug: Fixed line {line_counter}: '{line}' -> '{processed_line}'") # Optional
                            else:
                                # Line already has space or is just the rank number
                                processed_line = line # Use the (already stripped) line

                            # Increment rank ONLY if we found the expected line
                            expected_rank += 1
                        else:
                            # Line does NOT start with the expected rank.
                            # This could be footer text, page break artifact, or unexpected format.
                            # Write the original non-stripped line to preserve potential formatting.
                            processed_line = original_line # Revert to the original line with leading/trailing spaces
                            print(f"Warning: Line {line_counter} (Expected rank {expected_rank}) did not match: '{original_line[:80]}...'. Writing original.")
                            warnings += 1
                            # Do not increment expected_rank here

                        # --- Write the determined line to the file ---
                        if processed_line is not None:
                            text_file.write(processed_line + "\n")
                            lines_written += 1
                            first_line_written = True # Mark that we've started writing content

        print(f"Formatted TXT file '{output_txt_path}' created successfully.")
        print(f"Total lines processed (after skip): {line_counter - skip_lines}")
        print(f"Lines written to file: {lines_written}")
        if warnings > 0:
            print(f"Encountered {warnings} warning(s) during processing (lines not starting with expected rank).")
        return True # Indicate success

    except FileNotFoundError:
        print(f"Error: PDF file not found at '{pdf_path}'")
        return False
    except Exception as e:
        print(f"An error occurred during PDF processing and formatting: {e}")
        return False

# --- Parsing function remains the same ---
def parse_songs_from_txt(txt_path):
    """
    Parses the formatted TXT file (spotify_songs.txt) to extract rank,
    song name, and streams. Assumes rank and song name are separated by a space.
    """
    songs = []
    if not os.path.exists(txt_path):
        print(f"Error: Text file not found at '{txt_path}'. Run pdf_to_formatted_txt first.")
        return songs

    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            print(f"Starting parsing of '{txt_path}'...")
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue

                # Regex remains the same as it expects "Rank Space Title ... Streams"
                match = re.match(r'^(\d+)\s+(.*?)\s+([\d,]+)(?:\s+[\d,]+)?$', line)

                if match:
                    rank = int(match.group(1))
                    song_name = match.group(2).strip()
                    # Handle potential '*' prefix
                    if song_name.startswith('* '):
                         song_name = song_name[2:].strip()
                    elif song_name.startswith('*'):
                         song_name = song_name[1:].strip()

                    streams = match.group(3).strip()
                    songs.append({'rank': rank, 'song_name': song_name, 'streams': streams})
                else:
                    # This warning might still be useful if the combined function wrote weird lines
                    print(f"Warning: Could not parse line {line_num} in final file: '{line[:80]}...'")

    except Exception as e:
        print(f"An error occurred during TXT parsing: {e}")

    print(f"Successfully parsed {len(songs)} songs from '{txt_path}'.")
    return songs

# --- Main Execution Logic ---

# Define file paths
pdf_path = 'Ranking Eminem Songs/spotify_songs.pdf'
# Define the *single* final output text file path
final_txt_path = 'Ranking Eminem Songs/spotify_songs.txt'

# 1. Convert PDF directly to the final formatted Text file
# Adjust skip_lines based on your PDF's header/footer size
if pdf_to_formatted_txt(pdf_path, final_txt_path, skip_lines=11):

    # 2. Parse the final text file
    extracted_songs = parse_songs_from_txt(final_txt_path)

    # 3. Print the extracted songs (optional)
    if extracted_songs:
        print("\n--- Extracted Songs ---")
        for song in extracted_songs[:25]: # Print first 25 songs
            print(f"Rank: {song['rank']}, Name: {song['song_name']}, Streams: {song['streams']}")
        if len(extracted_songs) > 25:
            print(f"... and {len(extracted_songs) - 25} more songs.")
    else:
        print("No songs were extracted.")

# --- END OF REVISED FILE ---