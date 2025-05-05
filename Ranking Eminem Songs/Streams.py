import re

# Extracting songs and streams from txt
def extract_songs_from_txt(txt_path):
    pattern = re.compile(r'^(\d+)\s+(.*?)\s+(\d[\d,]*)\s+\d+')  # Regex to match the format in the text file
    extracted_songs = []

    with open(txt_path, 'r') as file:
        for line in file:
            match = pattern.match(line)
            if match:
                song_name = match.group(2).strip()
                # Remove features and anything in parentheses for better matching
                clean_song_name = re.sub(r'\(feat\..*?\)', '', song_name).strip()
                clean_song_name = re.sub(r'\(with.*?\)', '', clean_song_name).strip()
                clean_song_name = re.sub(r'\(.*?\)', '', clean_song_name).strip()
                
                stream_count = int(match.group(3).replace(",", ""))
                extracted_songs.append((song_name, clean_song_name, stream_count))
    
    return extracted_songs

# Map songs to albums and calculate total streams
def map_songs_to_albums(extracted_songs, albums):
    album_data = {album: {'total_streams': 0, 'matched_songs': []} for album in albums.keys()}
    unmatched_songs = []

    for song_name, clean_song_name, stream_count in extracted_songs:
        matched = False
        for album, songs in albums.items():
            # Clean up album song names too for better matching
            clean_album_songs = [re.sub(r'\(feat\..*?\)', '', s).strip() for s in songs]
            clean_album_songs = [re.sub(r'\(with.*?\)', '', s).strip() for s in clean_album_songs]
            clean_album_songs = [re.sub(r'\(.*?\)', '', s).strip() for s in clean_album_songs]
            
            # Check if the current song is in this album (case insensitive)
            if any(clean_song_name.lower() == album_song.lower() for album_song in clean_album_songs):
                album_data[album]['total_streams'] += stream_count
                album_data[album]['matched_songs'].append((song_name, stream_count))
                matched = True
                break
        
        if not matched:
            unmatched_songs.append((song_name, stream_count))
    
    return album_data, unmatched_songs

# Calculate average streams per song and rank albums
def rank_albums_by_average_streams(album_data, albums):
    album_avg_streams = {}
    for album, data in album_data.items():
        num_songs_in_album = len(albums[album])
        num_matched_songs = len(data['matched_songs'])
        
        if num_matched_songs > 0:  # Only calculate average if some songs were matched
            album_avg_streams[album] = data['total_streams'] / num_songs_in_album
            print(f"Matched {num_matched_songs}/{num_songs_in_album} songs for {album}")
        else:
            album_avg_streams[album] = 0
            print(f"No songs matched for {album}")
    
    return sorted(album_avg_streams.items(), key=lambda item: item[1], reverse=True)

# Define the albums and their songs
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
        "Cold Wind Blows", "Talkin' To Myself", "On Fire", "Won't Back Down", "W.T.P.", 
        "Going Through Changes", "Not Afraid", "Seduction", "No Love", "Space Bound", 
        "Cinderella Man", "25 To Life", "So Bad", "Almost Famous", "Love The Way You Lie", 
        "You're Never Over", "Untitled"
    ],
    "The Marshall Mathers LP2": [
        "Bad Guy", "Rhyme Or Reason", "So Much Better", "Survival", "Legacy", 
        "Asshole", "Berzerk", "Rap God", "Brainless", "Stronger Than I Was", 
        "The Monster", "So Far...", "Love Game", "Headlights"
    ],
    "Revival": [
        "Walk On Water", "Believe", "Chloraseptic (feat. Phresher)", 
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
        "Unaccommodating (feat. Young M.A)", "You Gon' Learn", 
        "Those Kinda Nights (feat. Ed Sheeran)", "In Too Deep", "Godzilla (feat. Juice WRLD)", 
        "Darkness", "Leaving Heaven (feat. Skylar Grey)", "Yah Yah", "Stepdad", 
        "Marsh", "Never Love Again", "Little Engine", "Lock It Up (feat. Anderson .Paak)", 
        "Farewell", "No Regrets (feat. Don Toliver)", "I Will"
    ],
    "Music To Be Murdered By - Side B": [
        "Black Magic (feat. Skylar Grey)", "Alfred's Theme", "Tone Deaf", 
        "Book of Rhymes (feat. DJ Premier)", "Favorite Bitch (feat. Ty Dolla $ign)", 
        "Guns Blazing (feat. Dr. Dre & Sly Pyper)", "Gnat", "Higher", 
        "These Demons (feat. MAJ)", "She Loves Me", "Killer", "Zeus (feat. White Gold)", 
        "Discombobulated"
    ],
    "The Death Of Slim Shady": [
        "Renaissance", "Habits", "Brand New Dance", "Evil", "Lucifer", 
        "Antichrist", "Fuel", "Road Rage", "Houdini", "Guilty Conscience II", 
        "Head Honcho", "Temporary", "Bad One", "Tobey (feat. Big Sean and BabyTron)", 
        "Somebody Save Me"
    ]
}

if __name__ == "__main__":
    # Path to the TXT file
    txt_path = 'C:\Github\Mini-Projects\Ranking Eminem Songs\spotify_songs.txt'
    
    # Extract songs and streams from the TXT file
    extracted_songs = extract_songs_from_txt(txt_path)
    print(f"Extracted {len(extracted_songs)} songs from the TXT file")
    
    # Map extracted songs to albums and calculate the total streams per album
    album_data, unmatched_songs = map_songs_to_albums(extracted_songs, albums)
    
    # Print some debug information
    print(f"\nTotal unmatched songs: {len(unmatched_songs)}")
    if len(unmatched_songs) > 0:
        print("First 10 unmatched songs:")
        for i, (song, streams) in enumerate(unmatched_songs[:10]):
            print(f"  {song}: {streams:,} streams")
    
    # Rank the albums by average streams per song
    ranked_albums = rank_albums_by_average_streams(album_data, albums)
    
    # Output the ranked albums by average streams per song
    print("\nAlbums ranked by average streams per song:")
    for album, avg_streams in ranked_albums:
        print(f"{album}: {int(avg_streams):,} average streams per song")
        
    # Also output the total streams per album
    print("\nTotal streams per album:")
    sorted_by_total = sorted(album_data.items(), key=lambda x: x[1]['total_streams'], reverse=True)
    for album, data in sorted_by_total:
        print(f"{album}: {data['total_streams']:,} total streams")
        
        # Print songs matched for debugging
        if len(data['matched_songs']) > 0:
            print("  Matched songs:")
            for song, streams in data['matched_songs']:
                print(f"    {song}: {streams:,} streams")
