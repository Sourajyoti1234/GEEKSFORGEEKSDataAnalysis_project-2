from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from pytube import YouTube
from googleapiclient.discovery import build
from pytube import YouTube
import re
from googleapiclient.discovery import build
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium.webdriver.chrome.service import Service
import pandas as pd
import matplotlib.pyplot as plt

api_key = 'AIzaSyBt5w7wJqWBvJDerPpOzNgYW_p_aj_Uazk'
end_date = datetime.utcnow()
start_date = end_date - relativedelta(months=6)
youtube_url='https://www.youtube.com'



def scroll_to_bottom(driver):
    old_position = 0
    new_position = None
    while new_position != old_position:
        old_position = driver.execute_script(
            ("return (window.pageYOffset !== undefined) ?"
             " window.pageYOffset : (document.documentElement ||"
             " document.body.parentNode || document.body);"))
        time.sleep(1)
        driver.execute_script(
            ("var scrollingElement = (document.scrollingElement ||"
             " document.body);scrollingElement.scrollTop ="
             " scrollingElement.scrollHeight;"))
        new_position = driver.execute_script(
            ("return (window.pageYOffset !== undefined) ?"
             " window.pageYOffset : (document.documentElement ||"
             " document.body.parentNode || document.body);"))
        




def get_published_time(video_url):
    try:
        video_id_match = re.search(r'(?<=v=)[^&]+', video_url)
        if video_id_match:
            video_id = video_id_match.group(0)
            youtube = build('youtube', 'v3', developerKey=api_key)
            video_response = youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            published_time_str = video_response['items'][0]['snippet']['publishedAt']
            published_time = datetime.strptime(published_time_str, '%Y-%m-%dT%H:%M:%SZ')
            return published_time
    except Exception as e:
        print(f"An error occurred while fetching published time: {e}")
        return None

def get_video_details(video_url):
    try:
        yt = YouTube(video_url)
        title = yt.title
        views = yt.views
        duration = yt.length
        publish_date = get_published_time(video_url)
        return title, views, duration, publish_date
    except Exception as e:
        print(f"An error occurred while fetching video details: {e}")
        return None, None, None, None

chrome_options = Options()
chrome_options.add_argument('--headless')
driver_path = ChromeDriverManager().install()
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

channel = 'https://www.youtube.com/@GeeksforGeeksVideos/videos'
driver.get(url=channel)
time.sleep(3)
scroll_to_bottom(driver)

page_source = driver.page_source
driver.quit()
soup = BeautifulSoup(page_source, 'html.parser')
titles = soup.find_all('a', id='video-title-link')

all_video_links = [ youtube_url + title.get('href') for title in titles]

video_titles = []
view_count = []
video_lengths = []
video_links = []
publish_dates=[]

for video_link in all_video_links:
    title, views, duration, publish_date = get_video_details(video_link)
    if start_date <= publish_date <= end_date:
        video_titles.append(title)
        view_count.append(views)
        video_lengths.append(duration)
        video_links.append(video_link)
        publish_dates.append(publish_date)

df = pd.DataFrame({
    'Video Title': video_titles,
    'Views': view_count,
    'Video Length': video_lengths,
    'Video Link': video_links,
    'Publish Date':publish_dates
})

print(f"Number of videos in the past 6 months: {df.shape[0]}")
# Task 3: Name the most viewed topics in the past 6 months
most_viewed_topics = df[df['Publish Date'] >= start_date].nlargest(5, 'Views')
print("Most Viewed Topics in the Past 6 Months:")
print(most_viewed_topics[['Video Title', 'Views']])

# Task 4: Name the topics with the highest video length
longest_videos = df[df['Publish Date'] >= start_date].nlargest(5, 'Video Length')
print("Topics with Highest Video Length in the Past 6 Months:")
print(longest_videos[['Video Title', 'Video Length']])

# Task 5: Comparison between views and video length using a graph
plt.figure(figsize=(10, 6))
plt.scatter(df['Views'], df['Video Length'], alpha=0.5)
plt.title("Comparison between Views and Video Length")
plt.xlabel("Views")
plt.ylabel("Video Length")
plt.grid(True)
plt.show()