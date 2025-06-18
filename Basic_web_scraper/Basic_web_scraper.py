import requests
from bs4 import BeautifulSoup

# Send a request to the webpage
url = 'https://kworb.net/spotify/artist/7dGJo4pcD2V6oG8kP0tJRR_songs.html'
response = requests.get(url)

# Parse the page content with BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Locate the table by finding the appropriate <table> tag
tables = soup.find_all('table')

# Select the right table based on its position or content
if len(tables) >= 2 :
    table = tables[1]  # Assuming the second table is the one we need
else :
    print("Table not found")
    table = None

# Parse the table rows if the table was found
if table :
    rows = table.find_all('tr')[1:]  # Skip the header row
    
    # Extract the data and save it to a text file
    with open('4. Basic_web_scraper/songs_list.txt', 'w') as file :
        for index, row in enumerate(rows, start=1) :
            columns = row.find_all('td')
            song_title = columns[0].get_text(strip=True)
            streams = columns[1].get_text(strip=True)
            daily = columns[2].get_text(strip=True)
            
            # Write to the file
            file.write(f"{index}. Name: {song_title}, Streams: {streams}, Daily: {daily}\n")
else :
    print("No table was found.")
