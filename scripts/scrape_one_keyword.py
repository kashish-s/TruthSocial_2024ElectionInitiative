from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import re
from datetime import datetime
import logging
import os
import csv
import pandas as pd
from multiprocessing import Process, Semaphore
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


HUMAN_PAUSE_TIME_LOWER = 0.5
HUMAN_PAUSE_TIME_UPPER = 0.8
SCROLL_SPEED = 0.01
TIME_BETWEEN_THREADS = 1

USERNAME = "USERNAME"
PASSWORD = "PASSWORD"

keywords_save_folder = 'trending_keywords_save_path'
BASE_URL = "https://truthsocial.com"

# Set the download path to the current working directory
custom_path = os.path.join(os.getcwd(), "webdriver_cache")
os.makedirs(custom_path, exist_ok=True)  # Create the directory if it doesn't exist

# Set options to tell webdriver-manager to use this path
os.environ["WDM_LOCAL"] = "1"  # Store drivers locally in the current directory
os.environ["WDM_CACHE"] = custom_path  # Set cache path



options = Options()
options.add_argument("--window_size=1920,1800")
options.add_argument("--log-level=3")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-logging")
options.add_argument("start-maximized")


def convert_to_datetime(date_string):
    try:
        date_time_obj = datetime.strptime(date_string, '%b %d, %Y, %I:%M %p')
    except:
        new_datetime_string = date_string.split(':')[0]
        new_datetime_string = new_datetime_string[:-2]
        new_datetime_string += '00:00'
        date_time_obj = datetime.strptime(new_datetime_string, '%b %d, %Y, %H:%M')
    return date_time_obj

def convert_user_date_to_datetime(date_string):
    date_time_obj = datetime.strptime(date_string, '%B %Y')
    return date_time_obj

def human_pause():
    pause_time = random.uniform(HUMAN_PAUSE_TIME_LOWER, HUMAN_PAUSE_TIME_UPPER)
    time.sleep(pause_time)
    
    
def save_to_tsv(keyword, data_list):
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data_list)
    keywords_save_folder = 'path_to_tending_keywords'
    
    
    # Append the DataFrame to the TSV file
    with open(f'{keywords_save_folder}{keyword}_{datetime.now().strftime("%Y-%m-%d")}.tsv', 'a', encoding='utf-8', newline='') as file:
        df.to_csv(file, sep='\t', index=False, header=file.tell() == 0)


def login(driver):
    driver.get(f"{BASE_URL}/login")
    time.sleep(5)
    try:
        sign_in_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//button[span[contains(text(), "Sign In")]]'))
        )
        sign_in_button.click()
        
        # user_name_entry = driver.find_element(By.XPATH, '//input[@name="username"]')
        user_name_entry = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="username"]'))
        )
        user_name_entry.click()
        user_name_entry.send_keys(USERNAME)
        
        password_entry = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="password"]'))
        )
        password_entry.click()
        password_entry.send_keys(PASSWORD)
        # password_entry.sendKeys(Keys.RETURN)
        
        
        submit_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//button[span[contains(text(), "Sign In")]]'))
        )
        submit_button.click()
    except Exception as e:
        print(e)
        pass
    time.sleep(5)
    print('Logged in...')
    
def final_clean_status_text(status_text):
    # Remove parts that start with <div class="relative -mt-7" and go until the end
    status_text = re.sub(r'<div class="relative.*', '', status_text, flags=re.DOTALL)
    return status_text.strip()


def get_all_statuses_on_screen_specific(driver, truth_count_limit, keyword):
    reached_page_end = False
    time.sleep(3)
    scroll_height = 200
    truth_info_list = []
    truth_ids = []
    while not reached_page_end:
        statuses = driver.find_elements(By.XPATH, '//div[@data-testid="status"]')
        for status in statuses:
            status_label = None
            try:
                status_id_pattern = re.search(r'data-id="(\d*)"', status.get_attribute("innerHTML"))
                truth_id = status_id_pattern.group(0).split("\"")[1]
                if truth_id not in truth_ids:
                    truth_username = re.findall(r'a title=\"(.*?)\" href=\"\/@\1', status.get_attribute('innerHTML'))[0]
                    status_label = status.get_attribute("innerHTML")
                    clean_other_tags = re.compile('<p>')
                    status_label = re.sub(clean_other_tags, '', status_label)
                    clean_other_tags = re.compile('</p>')
                    status_label = re.sub(clean_other_tags, '', status_label)

                    associated_tags = re.findall(r'<a href="https://truthsocial.com/tags/(.*?)" class="mention hashtag', status.get_attribute("innerHTML"))
                    tagged_accounts = re.findall(r'href="https://truthsocial.com/@(.*?)"', status.get_attribute('innerHTML'))
                    timestamp = re.findall(r'<time title="(.*?)" class="text-sm text-gray-700.*</time>', status.get_attribute("innerHTML"))
                    if len(timestamp) > 0:
                        try:
                            timestamp = convert_to_datetime(timestamp[0].split("\"")[0])
                        except Exception as e:
                            timestamp = convert_to_datetime(timestamp[0])

                    like_count = re.findall(r'title="Reply.*<span>(.*)</span>', status.get_attribute("innerHTML"))
                    if len(like_count) > 0:
                        if "k" in like_count[0]:
                            like_count = float(like_count[0].split("k")[0])
                            like_count = like_count * 1000
                        else:
                            like_count = like_count[0]
                        like_count = int(like_count)
                    else:
                        like_count = 0

                    reply_count = re.findall(r'title="Reply.*<span>(.*)</span>.*title="ReTruth"', status.get_attribute("innerHTML"))
                    if len(reply_count) > 0:
                        if "k" in reply_count[0]:
                            reply_count = float(reply_count[0].split("k")[0])
                            reply_count = reply_count * 1000
                        else:
                            reply_count = reply_count[0]
                    else:
                        reply_count = 0
                    reply_count = int(reply_count)

                    retruth_count = re.findall(r'title="Reply.*<span>.*</span>.*title="ReTruth.*<span>(.*)</span>.*title="Like"', status.get_attribute("innerHTML"))
                    if len(retruth_count) > 0:
                        if "k" in retruth_count[0]:
                            retruth_count = float(retruth_count[0].split("k")[0])
                            retruth_count = retruth_count * 1000
                        else:
                            retruth_count = retruth_count[0]
                    else:
                        retruth_count = 0
                    retruth_count = int(retruth_count)

                    media_gallery = re.findall(r'<div class="media-gallery"(.*?)<div class="pt-4"><div class="flex flex-row', status.get_attribute("innerHTML"))
                    truth_url = f"{BASE_URL}/@{truth_username}/posts/{truth_id}"
                    media_items = []
                    if len(media_gallery) > 0:
                        media_items = re.findall(r'<a class="media-gallery__item-thumbnail" href="(.*?)" target="_blank"><div data-testid="still-image-container"', status.get_attribute("innerHTML"))

                    videos = re.findall(r'<iframe src="(.*?)" title', status.get_attribute("innerHTML"))
                    video_urls = []
                    if len(videos) > 0:
                        video_urls = [curr_video.split("\"")[0] for curr_video in videos]
                    cleaned_media_items = media_items
                    for curr_video in video_urls:
                        curr_video = re.sub(r'&amp;', '&', curr_video)
                        cleaned_media_items.append(curr_video)
                    quoted_post = None
                    quoted_url = None
                    quoted_id = None
                    quoted_user = truth_username
                    is_quote = re.findall(r'data-testid="quoted-status"', status.get_attribute('innerHTML'))
                    if len(is_quote) > 0:
                        is_quote = True
                        quoted_post = re.findall(r'RT: https://truthsocial.com.*', status.get_attribute('innerHTML'))
                        quoted_url = quoted_post[0].split(' ')[-1]
                        quoted_user = quoted_url.split('/')[-3]
                        quoted_id = quoted_url.split('/')[-1]
                    else:
                        is_quote = False

                    status_text = re.findall(r'<div class=\"status__content.*?<p.*?>(.*?)<div data-testid=\"status-action-bar', status.get_attribute('innerHTML'))
                    if len(status_text) == 0:
                        status_text = status.get_attribute('innerHTML')
                    try:
                        status_links = re.findall(r'rel="nofollow noopener" target="_blank" class="status-link" title="(.*?)"><span', status_text[0])
                        links_total = []
                        for status_link in status_links:
                            status_link = re.sub(r'&amp;', '&', status_link)
                            links_total.append(status_link)
                        status_links = links_total
                    except:
                        logging.warning(f" status links: {status.get_attribute('innerHTML')}\n")
                    status_text = re.sub(r'<a href="https://truthsocial.com/tags/(.*?)" class="mention hashtag status-link" rel="nofollow noopener" target="_blank">#<span>\1</span></a>',r'#\1', status_text[0])
                    status_text = re.sub(r'<span class="h-card"><a href="https://truthsocial.com/@(.*?)" class="u-url mention status-link" rel="nofollow noopener" target="_blank" title="\1">@<span>\1</span></a></span>',r'@\1', status_text)
                    status_text = re.sub(r'<img draggable="false" class="emojione" alt=".*?" title=":(.*?):" src="/packs/emoji/.*?">',r'<emoji: \1>', status_text)
                    status_text = re.sub(r'<a href="(.*?)" rel="nofollow noopener".*?</a>',r'\1', status_text)
                    status_text = re.sub(r'-wrapper".*?ltr;">',r'', status_text)
                    status_text = re.sub(r'<p>', ' ', status_text)
                    status_text = re.sub(r'</p>', ' ', status_text)
                    status_text = re.sub(r'<br>', ' ', status_text)
                    status_text = re.sub(r'&amp;', 'and', status_text)
                    try:
                        status_text = re.findall(r'(.*?)</div>', status_text)[0]
                    except:
                        pass
                    status_text = status_text.strip()

                    is_retruth = False
                    retruth_status = re.findall(r'<div class="svg-icon text-green-600".*ReTruthed</div>', status.get_attribute('innerHTML'))
                    if len(retruth_status) > 0:
                        try:
                            is_retruth = True
                            retruthed_post = re.findall(r'aria-label="(.*?)ReTruthed.*?<div data-id="(.*?)"', status.get_attribute('innerHTML'))
                            retruthed_account = retruthed_post[0][0].split(',')[-2][1:]
                            retruthed_post_id = retruthed_post[0][1]
                            retruthed_post_url = f'{BASE_URL}/@{retruthed_account}/posts/{retruthed_post_id}'
                            retruthed_post_text = retruthed_post[0][0].split(',')[:-5]
                            retruthed_post_text = ''.join(retruthed_post_text)
                            retruthed_post_text = re.sub(r'&amp;', 'and', retruthed_post_text)
                        except:
                            retruthed_post = re.findall(r'href="(.*?)"><time title=', retruth_status)
                            retruthed_parts = retruthed_post[0].split("/")
                            retruthed_post_id = retruthed_parts[-1]
                            retruthed_account = retruthed_parts[0]
                            retruthed_post_url = f'{BASE_URL}/@{retruthed_account}/posts/{retruthed_post_id}'
                            logging.error(f'Error with retruth status:{retruthed_parts}\n\n{retruthed_post_id}\n\n{retruthed_account}\n\n{retruthed_post_url}', exc_info=True)
                    else:
                        retruthed_post_url = None
                        retruthed_post_id = None
                        retruthed_account = None

                    is_reply = False
                    replying_to = []
                    replies = re.findall(r'<a class="reply-mentions__account" href="/(.*?)"', status.get_attribute('innerHTML'))
                    if len(replies) > 0:
                        is_reply = True
                        replying_to = replies
                    status_text = final_clean_status_text(status_text)

                    truth_info = {
                        "url": truth_url,
                        "external_id": int(truth_id),
                        "timestamp": timestamp,
                        "author_username": truth_username,
                        "associated_tags": associated_tags,
                        "tagged_accounts": tagged_accounts,
                        "status_links": status_links,
                        "media_urls": cleaned_media_items,
                        "like_count": like_count,
                        "reply_count": reply_count,
                        "retruth_count": retruth_count,
                        "is_quote": is_quote,
                        "is_retruth": is_retruth,
                        "is_reply": is_reply,
                        "replying_to": replying_to,
                        "status": status_text,
                    }
                    # print(truth_info)

                    truth_info_list.append(truth_info)
                    truth_ids.append(truth_id)
                    print(f"Collected {len(truth_info_list)} truths related to {keyword}")
                    if len(truth_info_list) >= truth_count_limit:
                        return truth_info_list
                    if len(truth_info_list) % 50 == 0:
                        string = f"Collected {len(truth_info_list)} truths so far\t\t\t"
                        print(string)
                        logging.info(f"{string} | {truth_username}")
                        print('Saving/Appending .tsv file...')
                        save_to_tsv(keyword, truth_info_list)
            except Exception as e:
                print(e)
                pass
        driver.execute_script(f"window.scrollTo(0,{scroll_height});")
        height_left = driver.execute_script("return document.body.scrollHeight")

        if height_left <= scroll_height:
            time.sleep(8)
            height_left = driver.execute_script("return document.body.scrollHeight")
            if height_left <= scroll_height:
                reached_page_end = True
        else:
            scroll_height += 150
            time.sleep(SCROLL_SPEED)

    string = f"Collected {len(truth_info_list)} truths\t\t\t"
    print(string)
    return truth_info_list

def search(driver, keyword):
    driver.get(f"{BASE_URL}/search")
    time.sleep(10)
    search_bar = driver.find_element(By.XPATH, '//input[@id="search"]')
    truths_button = driver.find_element(By.XPATH, '//button[@id="tabs--tab--3"]')

    search_bar.send_keys(keyword)
    search_bar.send_keys(Keys.RETURN)
    truths_button.click()
    
def search_for_hashtag(driver, keyword):
    driver.get(f"{BASE_URL}/tags/{keyword}")
    time.sleep(10)
    
    
def get_trending_hashtags(driver):
    driver.get(f"{BASE_URL}/search")
    
    # Wait for the hashtags button to be clickable and click it
    hashtags_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@id="tabs--tab--3"]'))
    )
    hashtags_button.click()
    print('Selected Hashtags')
    
    # Wait for the hashtag elements to be present
    hashtag_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='hashtag']//a"))
    )

    # Extract the hashtags from the href attribute
    hashtags = [element.get_attribute('href').split('/tags/')[1] for element in hashtag_elements]
    
    return hashtags


    
    
def get_trending_posts(driver):
    driver.get(f"{BASE_URL}/search")
    time.sleep(10)
    

def search_keywords(keyword, driver, truth_count_limit): 
    human_pause()
    # search(driver, keyword)
    search_for_hashtag(driver, keyword)
    time.sleep(10)
    return get_all_statuses_on_screen_specific(driver, truth_count_limit, keyword)

from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Save a list to a JSON file and accept a keyword argument.')

    # Add arguments
    parser.add_argument('--keyword', type=str, required=True, help='A keyword argument')

    # Parse the arguments
    args = parser.parse_args()

    # Access the keyword argument
    keyword = args.keyword
    print(f'Scraping for {keyword}')
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    login(driver)
    truth_count_limit = 25000
    time.sleep(10)
    truths = search_keywords(keyword, driver, truth_count_limit)
    driver.close()
    driver.quit()