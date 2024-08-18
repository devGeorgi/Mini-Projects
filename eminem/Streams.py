import re

# Step 1: Extract Songs and Streams from TXT
def extract_songs_from_txt(txt_path):
    pattern = re.compile(r'^(\d+)\s+(.*?)\s+(\d[\d,]*)\s+\d+')  # Regex to match the format in the text file
    extracted_songs = []

    with open(txt_path, 'r') as file:
        for line in file:
            match = pattern.match(line)
            if match:
                song_name = match.group(2).strip()
                stream_count = int(match.group(3).replace(",", ""))
                extracted_songs.append((song_name, stream_count))
    
    return extracted_songs

# Step 2: Map Songs to Albums and Calculate Total Streams
def map_songs_to_albums(extracted_songs, albums):
    album_data = {album: {'total_streams': 0} for album in albums.keys()}

    for song_name, stream_count in extracted_songs:
        for album, songs in albums.items():
            if song_name.lower() in [song.lower() for song in songs]:
                album_data[album]['total_streams'] += stream_count
                break
    
    return album_data

# Step 3: Rank Albums by Total Streams
def rank_albums_by_total_streams(album_data):
    return sorted(album_data.items(), key=lambda item: item[1]['total_streams'], reverse=True)

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

# Path to the TXT file 
txt_path = 'eminem/streams.txt'

# Extract songs and streams from the TXT file
extracted_songs = extract_songs_from_txt(txt_path)

# Map extracted songs to albums and calculate the total streams per album
album_data = map_songs_to_albums(extracted_songs, albums)

# Rank the albums by total streams
ranked_albums = rank_albums_by_total_streams(album_data)

# Output the ranked albums by total streams
for album, data in ranked_albums:
    print(f"{album}: {data['total_streams']} streams")
