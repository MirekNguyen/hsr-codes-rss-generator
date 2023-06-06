import re
import sys
from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

timezone = pytz.timezone("Europe/Prague")

# Send a GET request to the website
url = "https://honkai-star-rail.fandom.com/wiki/Redemption_Code"
response = requests.get(url)

# Find the tbody element
soup = BeautifulSoup(response.content, "html.parser")
tables = soup.find_all("table")

target_table = None
for table in tables:
    # Find the previous sibling <h2> element of the table
    title_element = table.find_previous_sibling("h2").find(id="Active_Codes")
    if title_element and title_element.get_text() == "Active Codes":
        target_table = table
        break

# Extract data from tbody and convert it to a JSON object
data = []
if not target_table or not target_table.find("tbody"):
    print("Target table could not be found")
    exit(1)
tbody = target_table.find("tbody")
for row in tbody.find_all("tr"):
    row_data = []
    for cell in row.find_all("td"):
        row_data.append(cell.text.strip())
    if row_data:
        data.append(row_data)
# Generate feed
fg = FeedGenerator()
fg.id("https://mirekng.com/rss/genshin-codes.xml")
fg.title("Genshin codes")
fg.subtitle("Genshin codes")
fg.link(href="https://mirekng.com", rel="self")
fg.language("en")
for item in reversed(data):
    fe = fg.add_entry()
    fe.id(item[0])
    fe.title(item[0] + " | " + item[3])
    fe.link(href="https://hsr.hoyoverse.com/gift?code=" +
            item[0], replace=True)
    match = re.search(r"\d{4}-\d{2}-\d{2}", item[3])
    if match:
        date_string = match.group()
        pubDate = datetime.strptime(date_string, "%Y-%m-%d")
    else:
        pubDate = datetime.now()
    fe.description(item[3])
    fe.pubDate(timezone.localize(pubDate))
rssfeed = fg.rss_str(pretty=True)
fg.rss_file(sys.argv[len(sys.argv) - 1])
