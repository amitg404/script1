from flask import Flask, request, jsonify
from flask_cors import CORS 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import os
import time

app = Flask(__name__)
CORS(app) 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_song():
    data = request.get_json()
    song = data.get('song')
    
    if not song:
        return jsonify({"error": "Song name is required!"}), 400
    
    try:
        # Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_driver_path = "B:\College work\Projects\youtube_song_download\chromedriver-win64\chromedriver.exe"  # Update path if needed
        
        # Start Chrome Driver
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # YouTube Search
        driver.get('https://www.youtube.com')
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "search_query"))
        )
        search_box.send_keys(song)
        search_box.send_keys(Keys.RETURN)

        # Click first video
        first_video = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "video-title"))
        )
        first_video.click()

        # Get video URL
        WebDriverWait(driver, 10).until(EC.url_contains("watch"))
        video_url = driver.current_url
        driver.quit()

        # Download with yt-dlp
        output_folder = r"./downloads"
        os.makedirs(output_folder, exist_ok=True)
        subprocess.run([
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "-o", os.path.join(output_folder, "%(title)s.%(ext)s"),
            video_url
        ])

        return jsonify({"message": "Download complete!", "video_url": video_url})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
