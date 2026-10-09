import sys
sys.path.insert(1, r'C:\Users\dinis\OneDrive\Ambiente de Trabalho\Social Media Bot')
from SocialBot import SocialBot
import os
import stackapi
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from stackapi import StackAPI
import random
import time
import re
import subprocess
from moviepy import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, video, concatenate_videoclips, clips_array, TextClip
from selenium import webdriver

trend_video_path = r"C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\Trend\video.mp4"
video_clip_path = r"C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\Trend\2.mp4"
audio_path = r"C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\Trend\audio.mp3"
font_path = r'C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\Rot\impact.ttf'
clip2_path = r"C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\Wiki\Frames\2s.mp4"
img_folder = r"C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\Wiki"
clip1_path = r"C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\Wiki\Frames\30s.mp4"
img = r"C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\Wiki\1.png"
img_path = r"C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\Wiki\meme.jpg"
rot_video_path = r"C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\Wiki\video.mp4"
video_path = r"C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\Wiki\Videos1\Test"
out_folder = r"C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\Wiki\Videos\Teste\out"
out_video_path = r"C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\Wiki\Videos\Teste\out\video.mp4"

def start_driver():
    options = webdriver.FirefoxOptions()
    #options.add_argument("-headless")
    options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    profile = webdriver.FirefoxProfile(r"C:\Users\dinis\AppData\Roaming\Mozilla\Firefox\Profiles\pel2nykw.default-release")
    options.profile = profile
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Firefox(options=options)
    
    
    return driver

driver = start_driver()

i = 0
while True:
    
    try:
        if i > 50:
            websites = ["api.stackexchange.com", "whatismyipaddress.com"]
            SocialBot.connect_vpn(websites, r"C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\index.txt", r"C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\VPN2", r"C:\Users\dinis\OneDrive\Ambiente de Trabalho\M-20251013T163859Z-1-001\M\wg0.conf", "wg0")
            i = 0
        
        SocialBot.create_info_video(driver, video_path, img_folder, clip1_path, img, clip2_path, font_path, out_folder, out_video_path)
        
        i += 1
    except:
        pass