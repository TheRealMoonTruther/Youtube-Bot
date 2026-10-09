#-------------#
#   IMPORTS   #
#-------------#

#System Imports
import time
import os
from os import walk
import re
import subprocess
import socket
import random
import requests
import json
import urllib
import shutil
import urllib.request
from bs4 import BeautifulSoup
from urllib.request import urlopen

#selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException, InvalidSessionIdException, WebDriverException
from selenium_recaptcha_solver import RecaptchaSolver

#Other Imports
from random_username.generate import generate_username
from gpt4all import GPT4All
from fake_useragent import UserAgent
import undetected_chromedriver as uc
import stackapi
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from stackapi import StackAPI
from moviepy import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, video, concatenate_videoclips, clips_array, TextClip
from moviepy.video.fx.Loop import Loop

class SocialBot:

    #-----------#
    #   PROXY   #
    #-----------#
    
    def inplace_change(temp_file, filename, old_string, new_string, temp_file_name):
        # Safely read the input filename using 'with'
        with open(filename) as f:
            s = f.read()

        # Safely write the changed content, if found in the file
        os.remove(temp_file)
        file = open(temp_file, "w")
        s = s.replace(old_string, new_string)
        file.truncate(0)
        file.write(s)

    def connect_vpn(websites, index_file, vpn_folder, temp_file, temp_file_name):    
        try: #Make Sure to quit Wireguard:
            command = '"C:\\Program Files\\WireGuard\\wireguard.exe" /uninstalltunnelservice %s' % (temp_file_name)
            proc = subprocess.Popen(command)
            subprocess.call("TASKKILL /f  /IM  wireguard.exe")
            time.sleep(5)
            #subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
            #time.sleep(5)
        except:
            pass
        
        #Get Website IP
        ip = ""
        o = 0
        for website in websites:
            o += 1
            ip += socket.gethostbyname(website)
            ip += "/24, "
            l = socket.gethostbyname(website).split(".")
            l[2] = int(l[2]) + 1
            temp = ""
            for i in range(len(l)):
                temp += str(l[i])
                if i < len(l) - 1:
                    temp += "."
            ip += temp
            ip += "/24, "
            l = socket.gethostbyname(website).split(".")
            l[2] = int(l[2]) - 1
            temp = ""
            for i in range(len(l)):
                temp += str(l[i])
                if i < len(l) - 1:
                    temp += "."
            ip += temp
            ip += "/24, "
        #remove Last ","
        a = [i for i, letter in enumerate(ip) if letter == ","]
        index = a[len(a)-1]
        ip = ip[:index] + ip[index+1:]
        
        #Get Index
        file = open(index_file, 'r')
        t = file.read() #read leaves file handle at the end of file
        if t == "":
            i = 0
        else:
            i = int(t)
        
        #Create List With OpenVPN Config Files
        f = []
        for (dirpath, dirnames, filenames) in walk(vpn_folder):
            f.extend(filenames)
            break
        if i >= len(f):
            i = 0
        
        #Get Config File Name
        config = f[int(i)]
        
        #Change Config File with Website Ip:
        file = "%s\\%s" % (vpn_folder, config)
        SocialBot.inplace_change(temp_file, file, "0.0.0.0/0", ip, temp_file_name)
        SocialBot.delete_string(temp_file, [", ::/0"])
        
        #Update Index File
        i += 1
        file = open(index_file, 'w')
        file.write(str(i))
        
        file = open(temp_file, 'r')
        #print(file.read())
        
        #Start Wireguard
        command = '"c:\\Program Files\\WireGuard\\wireguard.exe" /installtunnelservice "%s"' % (temp_file)
        proc = subprocess.Popen(command) 
  
    def get_recapcha_ips(timeout=10):

        url = "https://www.netify.ai/resources/applications/google-recaptcha"

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            return re.findall(
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
                response.text
            )

        except requests.exceptions.Timeout:
            print("[WARN] netify.ai timed out — skipping reCAPTCHA IP fetch")
            return []

        except requests.exceptions.RequestException as e:
            print(f"[WARN] netify.ai request failed — {e}")
            return []
  
    def get_recapcha_ips_1():
        #Used to get recapcha ip addresses for ip rotation      
        
        url = "https://www.netify.ai/resources/applications/google-recaptcha"
        
        response = requests.get(url)
        ip_addresses = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', response.text)
        
        return ip_addresses
        
    def proxy():
        ips = []
        urls = [
            "https://free-proxy-list.net/",
            "https://proxyscrape.com/free-proxy-list",
            "https://advanced.name/freeproxy",
            "https://www.spys.one/en/free-proxy-list/",
            "https://hide.mn/en/proxy-list/",
            "https://geonode.com/free-proxy-list"
        ]
        
        pattern = re.compile(r'\b(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)'
                         r'(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}'
                         r'(?::\d{1,5})?\b')
        
        for url in urls:
            proxyList = requests.get(url)
            soup = BeautifulSoup(proxyList.text,'lxml')
            
            ips += pattern.findall(soup.get_text()) 
        
        end = 0
        while end == 0:
            proxy = random.choice(ips)
            try:
                proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
                response = requests.get("https://www.google.com/", proxies=proxies, timeout=2)
                end = 1
            except requests.exceptions.ProxyError:
                print(f"❌ Proxy error: {proxy}")
            except requests.exceptions.ConnectTimeout:
                print(f"❌ Timeout: {proxy}")
            except requests.exceptions.ConnectionError:
                print(f"❌ Connection failed: {proxy}")
            except Exception as e:
                print(f"❌ Other error ({proxy}): {e}")
                
        return proxy
   
    #-------------------#
    #   GENERAL TOOLS   #
    #-------------------#
    
    def text_to_video(text, t, clip_path, font_path, duration, font_size):
        
        clip = VideoFileClip(clip_path, audio=False).with_duration(duration)
        txt_clip = TextClip(font_path, text, size=(1920, 1080), text_align='center', font_size=font_size, method="caption")
        txt_clip = txt_clip.with_position('center').with_duration(duration)
        video = CompositeVideoClip([clip, txt_clip])
        
        #Calculate Timestamp
        t += duration

        a = [video, t]
        return a

    def txt_to_img(t, i, img_folder, font_path):
    
        im = Image.new("RGB", (1920, 1080), "#fff")
        box = ((0, 0, 1920, 1080))
        draw = ImageDraw.Draw(im)
        #draw.rectangle(box, outline="#000")

        text = t
        font_size = 100
        size = None
        while (size is None or size[0] > box[2] - box[0] or size[1] > box[3] - box[1]) and font_size > 0:
            font = ImageFont.truetype(font_path, font_size)
            #size = font.getsize_multiline(text)
            dummy_img = Image.new("RGB", (1, 1))
            draw = ImageDraw.Draw(dummy_img)
            bbox = draw.multiline_textbbox((0, 0), text, font=font)
            size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
            font_size -= 1
        draw.multiline_text((box[0], box[1]), text, "#000", font)
        path = img_folder + str(i) + ".png"
        im.save(path)

    #----------------------------#
    #   YOUTUBE CREATION TOOLS   #
    #----------------------------#

    def stackapi():
        #Retrieve The Text From Stack Overflow:
        SITE = StackAPI('stackoverflow')
        SITE.max_pages=1
        SITE.page_size=100
        
        #Create Anwsers
        time1 = random.randrange(1262304000, 1696118400)
        time2 = random.randrange(time1, 1696118400)
        question = SITE.fetch('questions', Key='4qArFpyh*TIw4)Man)R)7Q((', client_id=29098, fromdate=time1, todate=time2, max=1, pagesize=1, max_pages=1, sort='votes', filter='!9YdnSIN*P') #filter='quota_max'
        
        return question
        
    def trend_script():
        # GET TREND #
        pytrend = TrendReq(hl='en-US', tz=360)
        print(pytrend)
        trends = pytrend.trending_searches()

        rand1=random.Random()
        num = rand1.randint(0, len(trends[0]))

        print("\nTrend: " + trends[0][num])
        
        return trends[0][num]

    def decide_topic():
        #Decide Topic Randomly:
        topics = ["programming", "python", "web Development", "html", "Computers", "Viruses", "Hacking", "Gamming"]
        rand1=random.Random()
        num = rand1.randint(0, len(topics))
        topic = topics[num - 1]
        print("\nQuiz Topic: " + topic)
        
        return topic

    def create_video_trend(script, audio_path, video_clip_path, trend_video_path):
        #Text to Speech:
        language = 'en' 
        myobjAnwser = gTTS(text=script, lang=language, slow=False)
        myobjAnwser.save(audio_path)
        print("\nAudio Created")    
            
        clip = VideoFileClip(video_clip_path)
        audioclip = AudioFileClip(audio_path)
        duration = audioclip.duration
        videoclip = clip.subclipped(0, duration)

        new_audioclip = CompositeAudioClip([audioclip])
        videoclip.audio = new_audioclip
        videoclip.write_videofile(trend_video_path, threads=4, logger=None, ffmpeg_params=['-crf','18', '-aspect', '9:16'])

    def create_youtube_quiz(driver):
            topic = SocialBot.decide_topic()

            text = SocialBot.ai_chat("short quiz about " + topic + " with 3 fake anwsers and one real one. Include 1 question and 4 answers (for a total of FIVE senteces) seperated by the symbol |, have the question be first and the real anwser be second, include only the question and anwers and nothing else")
            
            print("\nText: " + text)
            words = text.split()
            t2 = text.split("|")
            print("\nQuiz: " + str(t2))
            
            # if text == "" or len(t2) > 5:
                # continue
            
            #Seperate Question and Anwsers:
            question = t2[0]
            real = t2[1]
            fake1 = t2[2]
            fake2 = t2[3]
            fake3 = t2[4]
            
            #Decide order of anwsers randomly
            a1 = ""
            a2 = ""
            a3 = ""
            a4 = ""
            rand=random.Random()
            n = rand.randint(1, 4)
            
            if n == 1:
                a1 = real
                a2 = fake1
                a3 = fake2
                a4 = fake3
                print("\nQuiz Order 1")
            if n == 2:
                a1 = fake1
                a2 = real
                a3 = fake2
                a4 = fake3
                print("\nQuiz Order 2")
            if n == 3:
                a1 = fake1
                a2 = fake2
                a3 = real
                a4 = fake3
                print("\nQuiz Order 2")
            if n == 4:
                a1 = fake1
                a2 = fake2
                a3 = fake3
                a4 = real
                print("\nQuiz Order 2")
            
            SocialBot.upload_quiz(driver, question, a1, a2, a3, a4, n)

    def create_youtube_meme(driver, img_path):
            text = SocialBot.ai_chat("Random short caption for a meme about Programming that you never told before, include only the caption and nothing else")
                
            # if text == "":
                # continue
                
            #Divide Caption to Fit Image
            i = 0
            t = ""
            words = text.split()
            for word in words:
                t += word + " "
                i += 1
                if i == 4:
                    i = 0
                    t += "\n"

            print("\nMeme Captcion: " + str(t))

            #Decide Wich Image to Use Randomy
            n = random.randrange(1,10)
            print("\nMeme Image " + str(n))
             
            #Delete Previous meme:
            try:
                os.remove(img_path) 
                print("\nMeme Deleted")
            except:
                print("\nMeme Delete Failed")
                pass
            
            # Open an Image
            path = img_path + ".jpg"
            print("\nMeme Image Opened")
             
            # Call draw Method to add 2D graphics in an image
            I1 = ImageDraw.Draw(img)

            # Add Text to an image
            font = ImageFont.truetype("impact.ttf", 125)
            I1.text((1500, 1500), t, (255, 255, 255), font, None, 5, "left")
            print("\nMeme Text Added")
             
            # Save the edited image
            img.save(img_path)
            print("\nMeme Saved")
            
            SocialBot.upload_img(driver, img_path)

    def create_youtube_trend(driver):
            trend1 = SocialBot.trend_script()

            script = SocialBot.ai_chat(trend1)
            # if script == "":
                # print("\nScript Empty")
                # continue

            SocialBot.create_video_trend(script)
            
            SocialBot.upload_video(driver, trend1, script)
    
    def create_info_video(driver, video_path, img_folder, clip1_path, img, clip2_path, font_path, out_folder, out_video_path):    
        
        t = 0
        
        #Delete Previous Folder:
        if os.path.exists(video_path):
            shutil.rmtree(video_path) 
            print("\nVideo Deleted")
            
        #Retrieve The Text From Stack Overflow:
        s = 0
        k = 0
        while s == 0 and k < 10:
            try:
                SITE = StackAPI('stackoverflow')
                s = 1
            except:
                k += 1
                
        SITE.max_pages=1
        SITE.page_size=100
        
        #Create Anwsers
        time1 = random.randrange(1262304000, 1696118400)
        time2 = random.randrange(time1, 1696118400)
        question = SITE.fetch('questions', Key='4qArFpyh*TIw4)Man)R)7Q((', client_id=29098, fromdate=time1, todate=time2, max=1, pagesize=1, max_pages=1, sort='votes', filter='!9YdnSIN*P')
        
        #Only proceed if the question has at least one anwser
        quest = []
        cont = 0
        for n in question['items']:
            quest = n
            if quest["is_answered"] == False:
                cont = 1
            
        if cont == 1:
            exit
            
        #Make Sure Title Isn't to long for youtube
        titleQuest = quest['title']
        titleQuest = titleQuest[0:100]
            
        #Get Question Text and anwsers
        question = quest['body']
        question_id = quest['question_id']
        top_answer = SITE.fetch('questions/' + str(question_id) + '/answers', order = 'desc', sort='votes', filter='withbody')
        
        #Format the Question Title:
        titleQuest2 = re.sub(r'\<a.+>', '', titleQuest)
        titleQuest2 = titleQuest2.replace('`', '"')
        question2 = re.sub(r'\<a.+>', '', question)
        question2 = question2.replace('`', '"')
        
        txt_clips = []
        
        # ADD QUESTION TITLE TO VIDEO #
        a = SocialBot.text_to_video(titleQuest2, t, clip2_path, font_path, 2, 100)
        txt_clips.append(a[0])
        t = a[1]
        
        # ADD QUESTION TEXT TO VIDEO #
        a = SocialBot.text_to_video(question, t, clip1_path, font_path, 30, 35)
        txt_clips.append(a[0])
        t = a[1]
         
        # ADD ANWSERS TO VIDEO #
            
        for r, an in zip(range(10), top_answer['items']):
            
            #Get Anwser Text
            AnwserText = an['body']
            
            #Format Answer Text
            AnwserText = re.sub(r'\<a.+>', '', AnwserText)
            AnwserText = AnwserText.replace('`', '"')
            anwserText1 = AnwserText
            
            #Create Anwser Title
            titleAnwser = "Anwser " + str(r + 1) + ": "

            # ADD ANSWER TITLE TO VIDEO #
            a = SocialBot.text_to_video(titleAnwser, t, clip2_path, font_path, 2, 100)
            txt_clips.append(a[0])
            t = a[1]
            
            # ADD ANSWER TEXT TO VIDEO #
            a = SocialBot.text_to_video(AnwserText, t, clip1_path, font_path, 30, 35)
            txt_clips.append(a[0])
            t = a[1]
         
        #Put all clips together
        final_video = concatenate_videoclips(txt_clips)
        final_video.write_videofile(out_video_path, fps=24)
            
        #Format Video Title
        titleQuest2 = titleQuest2.replace('&quot;', '"')
        titleQuest2 = titleQuest2.replace('&#vide39;', '"')

        #   UPLOAD   #
        SocialBot.upload_video(driver, titleQuest2, out_video_path)

    def create_rot_short(driver, rot_video_path):
            
            k = 0
            script = SocialBot.ai_chat("Random Interesting Reddid Post With around 120 words, include only the reddit post text nothing else inclunding quotation marks", k)
            title = SocialBot.ai_chat("title for this script: " + script + ", include only the title nothing else", k)
            # if script == "":
                # continue
            
            print("\nTitle: " + title)
            print("\nScript: " + script)
            
            dur_final = 0
            clips, dur_final = SocialBot.create_video_Text(script)
            print("\nFinal Duration: " + str(dur_final))
            
            vid = concatenate_videoclips(clips)
            
            vid.duration = dur_final
            vid.write_videofile(rot_video_path, threads=4, ffmpeg_params=['-crf','18', '-aspect', '9:16'])
            print("\nVideo Created")
            
            title = script[0:90]
            
            SocialBot.upload_video(driver, title, script)

    #--------------------------#
    #   YOUTUBE UPLOAD TOOLS   #
    #--------------------------#

    def upload_quiz(driver, question, a1, a2, a3, a4, n):
        #   UPLOAD   #
        driver.get("https://www.youtube.com/@TheKnowledgeBase69/community")
        sleep(5)
            
        #quiz:    
        driver.find_element(By.CSS_SELECTOR, "span.style-scope:nth-child(4) > ytd-button-renderer:nth-child(1) > yt-button-shape:nth-child(1) > button:nth-child(1)").click()
        print("\nQuiz Button Clicked")

        #Question:
        driver.find_element(By.ID, "contenteditable-root").send_keys(question)
        print("\nQuiz Question Written")

        #Add Anwsers:
        driver.find_element(By.CSS_SELECTOR, "#quiz-attachment > div.button-container.style-scope.ytd-backstage-quiz-editor-renderer > yt-button-renderer > yt-button-shape > button").click()
        driver.find_element(By.CSS_SELECTOR, "#quiz-attachment > div.button-container.style-scope.ytd-backstage-quiz-editor-renderer > yt-button-renderer > yt-button-shape > button").click()
        print("\nQuiz Add Answer Button CLicked Twice")

        #anwser 1:
        driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/div[2]/div/ytd-backstage-quiz-editor-renderer/div[1]/div[1]/div[1]/tp-yt-paper-input-container/div[2]/div/tp-yt-iron-autogrow-textarea/div[2]/textarea").send_keys(a1)
        print("\nQuiz Anwser 1 Written")

        #anwser 2:
        driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/div[2]/div/ytd-backstage-quiz-editor-renderer/div[1]/div[2]/div[1]/tp-yt-paper-input-container/div[2]/div/tp-yt-iron-autogrow-textarea/div[2]/textarea").send_keys(a2)
        print("\nQuiz Anwser 2 Written")

        #anwser 3:
        driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/div[2]/div/ytd-backstage-quiz-editor-renderer/div[1]/div[3]/div[1]/tp-yt-paper-input-container/div[2]/div/tp-yt-iron-autogrow-textarea/div[2]/textarea").send_keys(a3)
        print("\nQuiz Anwser 3 Written")

        #anwser 4:
        driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/div[2]/div/ytd-backstage-quiz-editor-renderer/div[1]/div[4]/div[1]/tp-yt-paper-input-container/div[2]/div/tp-yt-iron-autogrow-textarea/div[2]/textarea").send_keys(a4)
        print("\nQuiz Anwser 4 Written")

        #Select Correct Anwser:
        if n == 1:
            driver.find_element(By.CSS_SELECTOR, "div.quiz-option:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > yt-icon-button:nth-child(1) > button:nth-child(1)").click()
            print("\nQuiz Anwser 1 Selected as Real")
        elif n == 2:
            driver.find_element(By.CSS_SELECTOR, "div.quiz-option:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > yt-icon-button:nth-child(1) > button:nth-child(1)").click()
            print("\nQuiz Anwser 2 Selected as Real")
        elif n == 3:
            driver.find_element(By.CSS_SELECTOR, "div.quiz-option:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > yt-icon-button:nth-child(1) > button:nth-child(1)").click()
            print("\nQuiz Anwser 3 Selected as Real")
        elif n == 4:
            driver.find_element(By.CSS_SELECTOR, "div.quiz-option:nth-child(4) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > yt-icon-button:nth-child(1) > button:nth-child(1)").click()
            print("\nQuiz Anwser 4 Selected as Real")
        
        print(9)
        
        #Publish:
        WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='submit-button']/yt-button-shape/button"))).click()
        print("\nQuiz Publish Button Clicked")
            
        sleep(5)
        print("\nQuiz Sucessfully Uploaded")
        
    def upload_img(driver, path):
        driver.get("https://www.youtube.com/@TheKnowledgeBase69/community")
        print("\nMeme Youtube Opened")
        try:
            #Image:
            WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.ytd-backstage-post-dialog-renderer:nth-child(1) > ytd-button-renderer:nth-child(1) > yt-button-shape:nth-child(1) > button:nth-child(1)"))).click()
            print("\nMeme Image Button Clicked")
            
            sleep(1)
            
            #DRag'n'drop:
            elem = driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-backstage-items/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[7]/ytd-backstage-post-dialog-renderer/div[2]/ytd-commentbox/div[2]/div/div[2]/tp-yt-paper-input-container/div[2]/div/div[3]/ytd-backstage-multi-image-select-renderer/div[1]/input")
            driver.execute_script("arguments[0].scrollIntoView();", elem)
            elem.send_keys(path)
            print("\nMeme Image Drag and Drop Successfull")
            
            sleep(1)

            #Publish:                                                                          
            WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#submit-button > yt-button-shape:nth-child(1) > button:nth-child(1)"))).click()
            print("\nMeme Publish Button Clicked")
            
            sleep(5)
            print("\nMeme Uploaded Sucessfully")
        except:
            pass
            
    def upload_video(driver, title, path):
        
        #if True:
        try:
            print("\nUPLOAD: Start")
            
            #Open Youtube Page
            driver.get("https://www.youtube.com/upload")
            print("\nUPLOAD: Entered Youtbe Page")
            
            #Upload Video
            time.sleep(5)
            driver.find_element(By.XPATH, "//input[@type='file']").send_keys(r"" + path + "")
            print("\nUPLOAD: Video Uploaded")
            
            time.sleep(2)

            #Add Title
            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "textbox")))
            element.click()
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(Keys.BACKSPACE)
            element.send_keys(title)
            print("\nUPLOAD: Title Added")
        
            try: #Not Made For Kids Button
                driver.find_element(By.CSS_SELECTOR , "tp-yt-paper-radio-button.ytkc-made-for-kids-select:nth-child(2) > div:nth-child(1)").click()
                print("\nUPLOAD: Not Made for Kids Button Clicked")
                #driver.implicitly_wait(5)
            except:
                pass    
            
            #Next Button
            WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "//*[@id='next-button']/ytcp-button-shape/button"))).click()
            print("\nUPLOAD: Next Button Clicked 1")
            WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "//*[@id='next-button']/ytcp-button-shape/button"))).click()
            print("\nUPLOAD: Next Button Clicked 2")
            WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "//*[@id='next-button']/ytcp-button-shape/button"))).click()
            print("\nUPLOAD: Next Button Clicked 3")   
            time.sleep(5)
            
            try:
                WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[3]/ytcp-button-shape/button"))).click()
            except:
                pass
            
            #Publish Button
            try:
                WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "//*[@id='next-button']/ytcp-button-shape/button"))).click()
                print("\nUPLOAD: Publish Button Clicked")
            except:
                pass
                time.sleep(1)
            try: #Publish Anyway
                WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "/html/body/ytcp-prechecks-warning-dialog/ytcp-dialog/tp-yt-paper-dialog/div[3]/div/ytcp-button[1]/ytcp-button-shape/button"))).click()
                print("\nUPLOAD: Publish Anyway Button Clicked")
            except:
                pass
                
            #Wait for Video to load
            time.sleep(300)

            #Click Close Window Button
            WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "/html/body/ytcp-uploads-still-processing-dialog/ytcp-dialog/tp-yt-paper-dialog/div[3]/ytcp-button/ytcp-button-shape/button"))).click()
            print("\nUPLOAD: Close Window Button Clicked")
            time.sleep(3)
        except:
            pass