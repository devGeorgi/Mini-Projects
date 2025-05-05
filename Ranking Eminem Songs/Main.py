# --- START OF REVISED FILE Main.py ---

import re
import os # Import os for file check
import collections # Import collections for Counter

# --- Function Definitions ---

def extract_songs_from_txt(txt_path):
    """
    Extracts songs and streams from the formatted TXT file.
    Handles optional '*' prefix and optional second number at the end.
    Performs cleaning on the song names.
    """
    # Revised Regex:
    # ^(\d+)     # Rank at start
    # \s+       # Space(s) after rank
    # \*?\s*    # Optional '*' and optional space(s) after it
    # (.*?)     # Non-greedily capture song title
    # \s+       # Space(s) before main streams number
    # ([\d,]+)  # Capture main streams number (digits and commas)
    # (?:\s+[\d,]+)? # Optional non-capturing group for potential second number
    # $         # End of line
    pattern = re.compile(r'^(\d+)\s+\*?\s*(.*?)\s+([\d,]+)(?:\s+[\d,]+)?$')
    extracted_songs = []
    lines_matched = 0
    lines_read = 0

    if not os.path.exists(txt_path):
        print(f"Error: Input file not found at '{txt_path}'")
        return extracted_songs # Return empty list

    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            for line in file:
                lines_read += 1
                line = line.strip() # Clean leading/trailing whitespace first
                if not line:
                    continue # Skip empty lines

                match = pattern.match(line)
                if match:
                    lines_matched += 1
                    # rank = match.group(1) # Rank not needed here, but captured
                    song_name = match.group(2).strip() # The raw song name part
                    stream_count_str = match.group(3)

                    # --- Robust Cleaning ---
                    clean_song_name = song_name # Start with the raw matched name
                    clean_song_name = re.sub(r'\(feat\.[^)]+\)', '', clean_song_name, flags=re.IGNORECASE).strip()
                    clean_song_name = re.sub(r'\(with\s[^)]+\)', '', clean_song_name, flags=re.IGNORECASE).strip()
                    # Handle specific known suffixes BEFORE general parenthesis removal
                    clean_song_name = re.sub(r'\s-\sMusic From.*$', '', clean_song_name, flags=re.IGNORECASE).strip()
                    clean_song_name = re.sub(r'\s-\sFrom.*$', '', clean_song_name, flags=re.IGNORECASE).strip()
                    clean_song_name = re.sub(r'\s-\s.*Remix.*$', '', clean_song_name, flags=re.IGNORECASE).strip()
                    clean_song_name = re.sub(r'\s-\s.*Version.*$', '', clean_song_name, flags=re.IGNORECASE).strip()
                    clean_song_name = re.sub(r'\s-\s.*Edit.*$', '', clean_song_name, flags=re.IGNORECASE).strip()
                    clean_song_name = re.sub(r'\s-\sPt\.\s*\d+$', '', clean_song_name, flags=re.IGNORECASE).strip() # Handle - Pt. X
                    # Remove trailing parens generally (e.g., (Live), (Demo))
                    clean_song_name = re.sub(r'\s\([^)]*\)$', '', clean_song_name).strip()
                    # Remove specific known parenthetical additions if needed (example)
                    # clean_song_name = re.sub(r'\s\(Radio Version\)$', '', clean_song_name, flags=re.IGNORECASE).strip()
                    # Normalize apostrophes last
                    clean_song_name = clean_song_name.replace("’", "'")
                    # --- End Cleaning ---

                    try:
                        stream_count = int(stream_count_str.replace(",", ""))
                        # Store: original name, cleaned name, stream count
                        extracted_songs.append((song_name, clean_song_name, stream_count))
                    except ValueError:
                        print(f"Warning: Could not convert stream count '{stream_count_str}' to int for line: '{line}'")

                else: # DEBUG: Print lines that didn't match the revised regex
                    print(f"Warning: Regex did not match line: '{line}'")

    except Exception as e:
        print(f"An error occurred during file reading or processing in extract_songs_from_txt: {e}")

    print(f"\nRead {lines_read} lines from '{txt_path}'. Matched {lines_matched} song lines with regex.")
    return extracted_songs


def apply_cleaning_to_defined_songs(song_list):
    """Applies the same cleaning logic used for extracted songs to a list of defined songs."""
    cleaned_set = set()
    for s in song_list:
        # Apply SIMILAR cleaning logic as in extract_songs_from_txt
        album_song_clean = s # Start with original defined name
        album_song_clean = re.sub(r'\(feat\.[^)]+\)', '', album_song_clean, flags=re.IGNORECASE).strip()
        album_song_clean = re.sub(r'\(with\s[^)]+\)', '', album_song_clean, flags=re.IGNORECASE).strip()
        album_song_clean = re.sub(r'\s-\sMusic From.*$', '', album_song_clean, flags=re.IGNORECASE).strip()
        album_song_clean = re.sub(r'\s-\sFrom.*$', '', album_song_clean, flags=re.IGNORECASE).strip()
        album_song_clean = re.sub(r'\s-\s.*Remix.*$', '', album_song_clean, flags=re.IGNORECASE).strip()
        album_song_clean = re.sub(r'\s-\s.*Version.*$', '', album_song_clean, flags=re.IGNORECASE).strip()
        album_song_clean = re.sub(r'\s-\s.*Edit.*$', '', album_song_clean, flags=re.IGNORECASE).strip()
        album_song_clean = re.sub(r'\s-\sPt\.\s*\d+$', '', album_song_clean, flags=re.IGNORECASE).strip()
        album_song_clean = re.sub(r'\s\([^)]*\)$', '', album_song_clean).strip()
        album_song_clean = album_song_clean.replace("’", "'") # Normalize apostrophes
        cleaned_set.add(album_song_clean.lower()) # Store cleaned and lowercased
    return cleaned_set


def map_songs_to_albums(extracted_songs, defined_albums):
    """
    Maps extracted songs to defined albums using cleaned names.
    Calculates total streams and identifies matched/unmatched songs.
    """
    album_data = {album: {'total_streams': 0, 'matched_songs': []} for album in defined_albums.keys()}
    unmatched_songs = []
    song_match_details = [] # For debugging match process
    processed_original_spotify_names = set() # Avoid processing same spotify line twice

    # --- Pre-clean defined album song names once ---
    cleaned_defined_albums = {}
    for album, songs in defined_albums.items():
        cleaned_defined_albums[album] = apply_cleaning_to_defined_songs(songs)
    # --- End Pre-cleaning ---

    print(f"Attempting to map {len(extracted_songs)} extracted songs...")
    match_count = 0

    # Iterate through songs extracted from the TXT file
    for original_spotify_name, cleaned_spotify_name, stream_count in extracted_songs:

        # Skip if this exact original spotify name string has already been matched to an album
        if original_spotify_name in processed_original_spotify_names:
            # song_match_details.append(f"DEBUG: SKIP (already processed original name): '{original_spotify_name}'")
            continue

        matched_to_album = False
        cleaned_spotify_name_lower = cleaned_spotify_name.lower() # Normalize for matching

        # Check against each album's cleaned song list
        for album, cleaned_defined_songs_set in cleaned_defined_albums.items():
            if cleaned_spotify_name_lower in cleaned_defined_songs_set:
                album_data[album]['total_streams'] += stream_count
                # Store original name and streams for potential later inspection
                album_data[album]['matched_songs'].append((original_spotify_name, stream_count))
                # song_match_details.append(f"MATCH: '{cleaned_spotify_name_lower}' (from '{original_spotify_name}') -> Album '{album}'")
                processed_original_spotify_names.add(original_spotify_name) # Mark as processed
                matched_to_album = True
                match_count += 1
                break # IMPORTANT: Assign song to the first album it matches

        if not matched_to_album:
            # Add to unmatched list only if it wasn't processed/matched at all
            unmatched_songs.append((original_spotify_name, cleaned_spotify_name, stream_count))
            # song_match_details.append(f"NO MATCH: '{cleaned_spotify_name_lower}' (from '{original_spotify_name}')")

    # Print some matching details for debugging (optional)
    # print("\n--- Song Matching Details ---")
    # for detail in song_match_details:
    #      print(detail)
    # print("--- End Matching Details ---")

    print(f"Successfully matched {match_count} songs to albums.")
    return album_data, unmatched_songs


def rank_albums_by_average_streams(album_data, defined_albums):
    """Calculates average streams per song (based on defined count) and ranks albums."""
    album_avg_streams = {}
    print("\n--- Calculating Average Streams ---")
    for album, data in album_data.items():
        # Get the number of songs originally defined for this album
        defined_song_list = defined_albums.get(album, [])
        num_songs_in_album_def = len(defined_song_list)
        num_matched_songs = len(data['matched_songs'])
        total_matched_streams = data['total_streams']

        if num_songs_in_album_def > 0:
            # Calculate average based on TOTAL matched streams / number of songs DEFINED for the album
            average_streams = total_matched_streams / num_songs_in_album_def
            album_avg_streams[album] = average_streams
            print(f"AvgCalc: '{album}' - Matched {num_matched_songs}/{num_songs_in_album_def} songs. Avg = {total_matched_streams:,} / {num_songs_in_album_def} = {int(average_streams):,}")
        else:
            album_avg_streams[album] = 0
            print(f"AvgCalc: '{album}' has 0 songs defined or wasn't found in defined_albums dict. Matched {num_matched_songs} songs. Setting Avg to 0.")

    # Sort albums by average streams, highest first
    return sorted(album_avg_streams.items(), key=lambda item: item[1], reverse=True)


def identify_doubled_and_missing_songs(album_data, defined_albums):
    """Identifies songs defined but not matched, and songs matched multiple times to the same album."""
    album_song_issues = {}
    print("\n--- Identifying Missing/Doubled Songs ---")

    # Pre-clean all defined songs for efficient lookup later
    cleaned_defined_albums = {}
    for album, songs in defined_albums.items():
        cleaned_defined_albums[album] = apply_cleaning_to_defined_songs(songs)

    for album, data in album_data.items():
        doubled_in_match = []
        missing_from_match = []

        # Get the set of cleaned, lowercased defined songs for this album
        defined_cleaned_set = cleaned_defined_albums.get(album, set())

        # --- Simpler way to get cleaned matched names ---
        matched_cleaned_list_simple = []
        for original_matched_name, _ in data['matched_songs']:
             # Re-apply cleaning to the *original* matched name to ensure consistency
             temp_cleaned = original_matched_name
             temp_cleaned = re.sub(r'\(feat\.[^)]+\)', '', temp_cleaned, flags=re.IGNORECASE).strip()
             temp_cleaned = re.sub(r'\(with\s[^)]+\)', '', temp_cleaned, flags=re.IGNORECASE).strip()
             temp_cleaned = re.sub(r'\s-\sMusic From.*$', '', temp_cleaned, flags=re.IGNORECASE).strip()
             temp_cleaned = re.sub(r'\s-\sFrom.*$', '', temp_cleaned, flags=re.IGNORECASE).strip()
             temp_cleaned = re.sub(r'\s-\s.*Remix.*$', '', temp_cleaned, flags=re.IGNORECASE).strip()
             temp_cleaned = re.sub(r'\s-\s.*Version.*$', '', temp_cleaned, flags=re.IGNORECASE).strip()
             temp_cleaned = re.sub(r'\s-\s.*Edit.*$', '', temp_cleaned, flags=re.IGNORECASE).strip()
             temp_cleaned = re.sub(r'\s-\sPt\.\s*\d+$', '', temp_cleaned, flags=re.IGNORECASE).strip()
             temp_cleaned = re.sub(r'\s\([^)]*\)$', '', temp_cleaned).strip()
             temp_cleaned = temp_cleaned.replace("'", "'")
             matched_cleaned_list_simple.append(temp_cleaned.lower())
        # --- End Simpler Way ---

        matched_cleaned_set = set(matched_cleaned_list_simple)

        # Find missing songs: (Defined Cleaned Set) - (Matched Cleaned Set)
        missing_cleaned_names = defined_cleaned_set - matched_cleaned_set
        # Find the original defined names corresponding to the missing cleaned names
        original_defined_songs = defined_albums.get(album, [])
        missing_from_match = [
            orig_def_song for orig_def_song in original_defined_songs
            if apply_cleaning_to_defined_songs([orig_def_song]).pop() in missing_cleaned_names
        ]

        # Find doubled songs: Use Counter on the list of cleaned matched names
        # This identifies if multiple Spotify entries cleaned to the same name for this album
        matched_name_counts = collections.Counter(matched_cleaned_list_simple)
        doubled_cleaned_names = {name for name, count in matched_name_counts.items() if count > 1}
        # Find the original Spotify names that resulted in these doubled cleaned names
        doubled_in_match = []
        for orig_spotify_name, _ in data['matched_songs']:
            cleaned = re.sub(r'\(feat\.[^)]+\)', '', orig_spotify_name, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r'\(with\s[^)]+\)', '', cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r'\s-\sMusic From.*$', '', cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r'\s-\sFrom.*$', '', cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r'\s-\s.*Remix.*$', '', cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r'\s-\s.*Version.*$', '', cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r'\s-\s.*Edit.*$', '', cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r'\s-\sPt\.\s*\d+$', '', cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r'\s\([^)]*\)$', '', cleaned).strip()
            cleaned = cleaned.replace("'", "'").lower()
            if cleaned in doubled_cleaned_names:
                doubled_in_match.append(orig_spotify_name)

        if doubled_in_match or missing_from_match:
            album_song_issues[album] = {
                'doubled': sorted(list(set(doubled_in_match))), # Show unique original names that were doubled
                'missing': sorted(list(missing_from_match))   # Show original defined names that were missing
            }
            # Debug Print
            # print(f"Debug '{album}': DefinedClean={len(defined_cleaned_set)}, MatchedClean={len(matched_cleaned_set)}, MissingClean={len(missing_cleaned_names)}, DoubledClean={len(doubled_cleaned_names)}")
            # print(f"Debug '{album}': MissingOrig={len(missing_from_match)}, DoubledOrig={len(doubled_in_match)}")

    return album_song_issues

# --- End Function Definitions ---


# --- Main Execution ---

print("Starting Main Script...")

# Define the albums and their songs, there are no more albums and no more songs, don't touch!!!
defined_albums = {
    "The Slim Shady LP": [
        "My Name Is", "Guilty Conscience", "Brain Damage", "If I Had", "'97 Bonnie & Clyde","Role Model", "My Fault", "Cum On Everybody", "Rock Bottom", "Just Don't Give A Fuck","As The World Turns", "I'm Shady", "Bad Meets Evil", "Still Don't Give A Fuck"
    ],
    "The Marshall Mathers LP": [
        "Kill You", "Stan", "Who Knew", "The Way I Am", "The Real Slim Shady", "Remember Me?","I'm Back", "Marshall Mathers", "Drug Ballad", "Amityville", "Bitch Please II", "Kim","Under The Influence", "Criminal"
    ],
    "The Eminem Show": [
        "White America", "Business", "Cleanin' Out My Closet", "Square Dance", "Soldier","Say Goodbye Hollywood", "Drips", "Without Me", "Sing For The Moment", "Superman","Hailie's Song", "When The Music Stops", "Say What You Say", "Till I Collapse","My Dad's Gone Crazy"
    ],
    "Encore": [
        "Evil Deeds", "Never Enough", "Yellow Brick Road", "Like Toy Soldiers", "Mosh","Puke", "My 1st Single", "Rain Man", "Big Weenie", "Just Lose It", "Ass Like That","Spend Some Time", "Mockingbird", "Crazy In Love", "One Shot 2 Shot", "Encore/Curtains Down"
    ],
    "Relapse": [
        "3 a.m.", "My Mom", "Insane", "Bagpipes From Baghdad", "Hello","Same Song & Dance", "We Made You", "Medicine Ball", "Stay Wide Awake", "Old Time's Sake","Must Be The Ganja", "Deja Vu", "Beautiful", "Crack A Bottle", "Underground"
    ],
    "Recovery": [
        "Cold Wind Blows", "Talkin' To Myself", "On Fire", "Won't Back Down", "W.T.P.","Going Through Changes", "Not Afraid", "Seduction", "No Love", "Space Bound","Cinderella Man", "25 To Life", "So Bad", "Almost Famous", "Love The Way You Lie","You're Never Over", "Untitled" 
    ],
    "The Marshall Mathers LP2": [
        "Bad Guy", "Rhyme Or Reason", "So Much Better", "Survival", "Legacy","Asshole", "Berzerk", "Rap God", "Brainless", "Stronger Than I Was","The Monster", "So Far...", "Love Game", "Headlights", "Evil Twin" 
    ],
    "Revival": [
        "Walk On Water", "Believe", "Chloraseptic","Untouchable", "River","Remind Me", "Revival (Interlude)", "Like Home","Bad Husband","Tragic Endings","Framed", "Nowhere Fast","Heat", "Offended", "Need Me","In Your Head", "Castle", "Arose"
    ],
    "Kamikaze": [
        "The Ringer", "Greatest", "Lucky You","Normal", "Stepping Stone", "Not Alike","Kamikaze", "Fall", "Nice Guy","Good Guy","Venom - Music From The Motion Picture"
    ],
    "Music To Be Murdered By": [
        "Premonition - Intro","Unaccommodating", "You Gon' Learn","Those Kinda Nights", "In Too Deep", "Godzilla","Darkness", "Leaving Heaven", "Yah Yah","Stepdad","Marsh", "Never Love Again", "Little Engine", "Lock It Up","Farewell", "No Regrets", "I Will",
    ],
    "Music To Be Murdered By - Side B": [
        "Black Magic", "Alfred's Theme", "Tone Deaf","Book of Rhymes", "Favorite Bitch","Guns Blazing", "Gnat", "Higher","These Demons","She Loves Me", "Killer", "Zeus","Discombobulated"
    ],
    "The Death Of Slim Shady": [ 
        "Renaissance", "Habits", "Brand New Dance", "Evil", "Lucifer","Antichrist", "Fuel", "Road Rage", "Houdini", "Guilty Conscience 2", "Head Honcho", "Temporary", "Bad One", "Tobey","Somebody Save Me"
    ]
}

# --- File Path ---
txt_path = 'Ranking Eminem Songs/spotify_songs.txt'

# 1. Extract songs and streams from the TXT file
extracted_songs = extract_songs_from_txt(txt_path)

# Check if extraction yielded results before proceeding
if not extracted_songs:
    print("No songs were extracted. Exiting.")
else:
    # 2. Map extracted songs to albums
    # Pass the originally defined albums (with potentially mixed apostrophes is ok now)
    album_data, unmatched_songs = map_songs_to_albums(extracted_songs, defined_albums)

    # --- Output Results ---
    print(f"\n--- Match Summary ---")
    print(f"Total extracted songs processed: {len(extracted_songs)}")
    print(f"Total songs matched to an album: {sum(len(d['matched_songs']) for d in album_data.values())}")
    print(f"Total unmatched songs (not found in any album definition): {len(unmatched_songs)}")
    if unmatched_songs:
         print("\nSample of Unmatched Songs (Original Spotify Name | Cleaned Name):")
         # Sort unmatched by stream count desc?
         unmatched_songs.sort(key=lambda x: x[2], reverse=True)
         for orig, clean, streams in unmatched_songs[:20]: # Show top 20 unmatched by streams
              print(f"  - {orig} | {clean} ({streams:,})")
         if len(unmatched_songs) > 20:
              print(f"  ... and {len(unmatched_songs) - 20} more unmatched songs.")
    print("-" * 20)


    # 3. Identify doubled and missing songs per album
    # Pass the original defined_albums dictionary here
    album_song_issues = identify_doubled_and_missing_songs(album_data, defined_albums)

    # Print doubled and missing songs for each album
    print("\n--- Album Song Definition Issues (Compared to Matched Spotify List) ---")
    any_issues = False
    for album, issues in sorted(album_song_issues.items()):
        if issues['doubled'] or issues['missing']:
            any_issues = True
            print(f"\nAlbum: {album}")
            if issues['missing']:
                print(f"  Missing Songs ({len(issues['missing'])}): (Defined but not found in matched Spotify list)")
                for song in issues['missing']:
                    print(f"    - {song}")
            if issues['doubled']:
                print(f"  Doubled Songs ({len(issues['doubled'])}): (Spotify entries cleaning to the same name)")
                for song in issues['doubled']:
                    print(f"    - {song}") # These are original Spotify names
    if not any_issues:
        print("No missing or doubled songs detected based on current definitions and matching.")
    print("--- End Album Song Issues ---\n")


    # 4. Rank the albums by average streams per song
    # Pass the original defined_albums dictionary here
    ranked_albums_avg = rank_albums_by_average_streams(album_data, defined_albums)

    # Output the ranked albums by average streams per song
    print("\n--- Albums Ranked by Average Streams Per Defined Song ---")
    for i, (album, avg_streams) in enumerate(ranked_albums_avg, 1):
        print(f"{i}. {album}: {int(avg_streams):,} average streams per song")
    print("-" * 20)


    # 5. Also output the total streams per album
    print("\n--- Albums Ranked by Total Matched Streams ---")
    # Sort by total streams found for the album
    sorted_by_total = sorted(album_data.items(), key=lambda x: x[1]['total_streams'], reverse=True)
    for i, (album, data) in enumerate(sorted_by_total, 1):
        # Only print albums that had streams matched
        if data['total_streams'] > 0:
            num_matched = len(data['matched_songs'])
            num_defined = len(defined_albums.get(album, []))
            print(f"{i}. {album}: {data['total_streams']:,} total streams (Matched {num_matched}/{num_defined} songs)")
            # Optional: Print matched songs per album (can be very long)
            # if num_matched > 0:
            #     print("    Matched songs:")
            #     for song, streams in sorted(data['matched_songs'], key=lambda x: x[1], reverse=True)[:5]: # Show top 5 matched
            #         print(f"      - {song}: {streams:,} streams")
            #     if num_matched > 5: print("      ...")
    print("-" * 20)

print("\nMain Script Finished.")

# --- END OF REVISED FILE Main.py ---