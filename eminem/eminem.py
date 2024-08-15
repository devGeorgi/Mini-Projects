import pdfplumber
import re

# Step 1: Extract Data from PDF
def extract_songs_from_pdf(pdf_path, albums):
    # Pattern to match song names followed by view counts
    pattern = re.compile(r'^\d+\s+(.*?)\s+(\d[\d,]*)\s+\d+')

    extracted_songs = []
    found_songs = set()  # To keep track of songs that have already been found
    matched_songs = []
    unmatched_songs = []

    song_list_started = False  # Flag to determine when the actual song list starts

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                for line in lines:
                    # Skip lines until the actual song list starts (indicated by the presence of the first song number)
                    if not song_list_started:
                        if re.match(r'^\d+\s+', line):  # Detects the start of the song list by matching a line that starts with a number
                            song_list_started = True

                    if song_list_started:
                        match = pattern.match(line)
                        if match:
                            song_name = match.group(1).strip()
                            view_count = int(match.group(2).replace(",", ""))

                            # Check if the song is in any of the albums and hasn't been found before
                            song_matched = False
                            for album, songs in albums.items():
                                if song_name.lower() in [song.lower() for song in songs] and song_name.lower() not in found_songs:
                                    extracted_songs.append((song_name, view_count))
                                    found_songs.add(song_name.lower())
                                    matched_songs.append(song_name)
                                    song_matched = True
                                    break  # Stop searching this song once found
                            
                            if not song_matched:
                                unmatched_songs.append(song_name)
    
    return extracted_songs, matched_songs, unmatched_songs

# Step 2: Map Songs to Albums
def map_songs_to_albums(extracted_songs, albums):
    album_views = {album: 0 for album in albums.keys()}
    
    for song_name, view_count in extracted_songs:
        for album, songs in albums.items():
            if song_name.lower() in [song.lower() for song in songs]:
                album_views[album] += view_count
                break
    
    return album_views

# Step 3: Rank Albums by Total Views
def rank_albums(album_views):
    return sorted(album_views.items(), key=lambda item: item[1], reverse=True)

# Defining the albums and their songs
albums = {
    "The Slim Shady LP": [
        "My Name Is", "Guilty Conscience", "Brain Damage", "If I Had", "'97 Bonnie & Clyde", 
        "Role Model", "My Fault", "Cum On Everybody", "Rock Bottom", "Just Don't Give A Fuck", 
        "As The World Turns", "I'm Shady", "Bad Meets Evil", "Still Don't Give A Fuck"
    ],
    "The Marshall Mathers LP": [
        "Kill You", "Stan", "Who Knew", "The Way I Am", "The Real Slim Shady", "Remember Me?", 
        "I'm Back", "Marshall Mathers", "Drug Ballad", "Amityville", "Bitch Please II", "Kim", 
        "Under The Influence", "Criminal"
    ],
    "The Eminem Show": [
        "White America", "Business", "Cleanin' Out My Closet", "Square Dance", "Soldier", 
        "Say Goodbye Hollywood", "Drips", "Without Me", "Sing For The Moment", "Superman", 
        "Hailie's Song", "When The Music Stops", "Say What You Say", "Till I Collapse", 
        "My Dad's Gone Crazy"
    ],
    "Encore": [
        "Evil Deeds", "Never Enough", "Yellow Brick Road", "Like Toy Soldiers", "Mosh", 
        "Puke", "My 1st Single", "Rain Man", "Big Weenie", "Just Lose It", "Ass Like That", 
        "Spend Some Time", "Mockingbird", "Crazy In Love", "One Shot 2 Shot", "Encore/Curtains Down"
    ],
    "Relapse": [
        "3 a.m.", "My Mom", "Insane", "Bagpipes From Baghdad", "Hello", 
        "Same Song & Dance", "We Made You", "Medicine Ball", "Stay Wide Awake", "Old Time's Sake", 
        "Must Be The Ganja", "Deja Vu", "Beautiful", "Crack A Bottle", "Underground"
    ],
    "Recovery": [
        "Cold Wind Blows", "Talkin’ 2 Myself", "On Fire", "Won't Back Down", "W.T.P.", 
        "Going Through Changes", "Not Afraid", "Seduction", "No Love", "Space Bound", 
        "Cinderella Man", "25 To Life", "So Bad", "Almost Famous", "Love The Way You Lie", 
        "You’re Never Over", "Untitled"
    ],
    "The Marshall Mathers LP2": [
        "Bad Guy", "Rhyme Or Reason", "So Much Better", "Survival", "Legacy", 
        "Asshole", "Berzerk", "Rap God", "Brainless", "Stronger Than I Was", 
        "The Monster", "So Far...", "Love Game", "Headlights"
    ],
    "Revival": [
        "Walk On Water (feat. Beyoncé)", "Believe", "Chloraseptic (feat. Phresher)", 
        "Untouchable", "River (feat. Ed Sheeran)", "Remind Me", "Revival (Interlude)", 
        "Like Home (feat. Alicia Keys)", "Bad Husband (feat. X Ambassadors)", 
        "Tragic Endings (feat. Skylar Grey)", "Framed", "Nowhere Fast (feat. Kehlani)", 
        "Heat", "Offended", "Need Me (feat. Pink)", "In Your Head", "Castle", "Arose"
    ],
    "Kamikaze": [
        "The Ringer", "Greatest", "Lucky You (feat. Joyner Lucas)", "Normal", 
        "Stepping Stone", "Not Alike (feat. Royce Da 5'9)", "Kamikaze", "Fall", 
        "Nice Guy (with Jessie Reyez)", "Good Guy (feat. Jessie Reyez)", 
        "Venom - Music From The Motion Picture"
    ],
    "Music To Be Murdered By": [
        "Unaccommodating (feat. Young M.A)", "You Gon’ Learn", 
        "Those Kinda Nights (feat. Ed Sheeran)", "In Too Deep", "Godzilla (feat. Juice WRLD)", 
        "Darkness", "Leaving Heaven (feat. Skylar Grey)", "Yah Yah", "Stepdad", 
        "Marsh", "Never Love Again", "Little Engine", "Lock It Up (feat. Anderson .Paak)", 
        "Farewell", "No Regrets (feat. Don Toliver)", "I Will"
    ],
    "Music To Be Murdered By - Side B": [
        "Black Magic (feat. Skylar Grey)", "Alfred’s Theme", "Tone Deaf", 
        "Book of Rhymes (feat. DJ Premier)", "Favorite Bitch (feat. Ty Dolla $ign)", 
        "Guns Blazing (feat. Dr. Dre & Sly Pyper)", "Gnat", "Higher", 
        "These Demons (feat. MAJ)", "She Loves Me", "Killer", "Zeus (feat. White Gold)", 
        "Discombobulated"
    ],
    "The Death Of Slim Shady": [
        "Renaissance", "Habits", "Brand New Dance", "Evil", "Lucifer", 
        "Antichrist", "Fuel", "Road Rage", "Houdini", "Guilty Conscience 2", 
        "Head Honcho", "Temporary", "Bad One", "Tobey (feat. Big Sean and BabyTron)", 
        "Somebody Save Me"
    ]
}

# Path to the PDF file (adjust the path according to your setup)
pdf_path = 'eminem/spotify_songs.pdf'

# Extract songs and views from the PDF
extracted_songs, matched_songs, unmatched_songs = extract_songs_from_pdf(pdf_path, albums)

# Map songs to albums and calculate total views
album_views = map_songs_to_albums(extracted_songs, albums)

# Rank the albums by total views
ranked_albums = rank_albums(album_views)

# Display the ranked albums
for rank, (album, views) in enumerate(ranked_albums, 1):
    print(f"{rank}. {album}: {views} views")

# Print the summary of found and not found songs
print("\nSummary:")
print(f"Total songs found: {len(matched_songs)}")
print(f"Total songs not found: {len(unmatched_songs)}")

if unmatched_songs:
    print("\nSongs not matched:")
    for song in unmatched_songs:
        print(f"- {song}")
