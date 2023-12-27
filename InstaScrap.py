import instaloader
import datetime
import gspread
from google.oauth2.service_account import Credentials

##FIRST STEP: Scrap the instagram data##



loader = instaloader.Instaloader()
print(loader)
loader.login('natashajain2002@gmail.com', 'Aarin@002')
profile = instaloader.Profile.from_username(loader.context,
                                            'gt2028class')

start_date = datetime.datetime(2023, 12, 10)
posts = profile.get_posts()

with open('captions.txt', 'w', encoding='utf-8') as file:
    for post in profile.get_posts():
        if post.date_utc.replace(tzinfo=None) >= start_date:
            # Write the caption to the file
            file.write(post.caption + '\n')
            # Write the URL of the first image to the file
            if post.typename == 'GraphImage':
                file.write(f"Image URL: {post.url}\n\n")
            elif post.typename == 'GraphSidecar':
                # In case of a sidecar post, get the URL of the first image
                sidecar_node = next(post.get_sidecar_nodes())
                file.write(f"Image URL: {sidecar_node.display_url}\n\n")

## SECOND STEP: Add to the Google Sheets ##

# Define the Google Sheets API scope
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Load credentials for Google Sheets API
creds = Credentials.from_service_account_file('rush-sheet-autopopulate-1d315224044b.json', scopes=scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open("RushFall24").sheet1

# Read and process the captions from the text file
data = []
with open('captions.txt', 'r', encoding='utf-8') as file:
    biography = ""
    social_media = ""
    image_url = ""
    for line in file:
        if line.strip() == "":
            # End of a section, add to data and reset variables
            if biography and (social_media or image_url):
                data.append([biography.strip(), social_media.strip(), image_url.strip()])
                biography = ""
                social_media = ""
                image_url = ""
        elif line.startswith("Instagram:") or line.startswith("Snapchat:"):
            social_media += line.strip() + " "  # Append social media handles
        elif line.startswith("Image URL:"):
            image_url = line.strip().split("Image URL: ")[1]  # Extract image URL
        else:
            biography += line.strip() + " "  # Append biography text

# Batch update the Google Sheet (outside the loop)
sheet.update('A1', data)

print("Captions, social media handles, and image URLs updated successfully.")