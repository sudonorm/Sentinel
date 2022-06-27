import pandas as pd
import os
import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import numpy as np
from telegram_sidekick import TelegramSidekick
from string import ascii_lowercase
from typing import List, Dict
import argparse
import re

### For local development #######################

# from dotenv import load_dotenv
# from os.path import join, dirname

# dotenv_path = join(dirname(__file__), '.env')
# load_dotenv(dotenv_path)

# TOKEN = os.environ.get("TELEGRAM_TOKEN")
# CHAT_ID = int(os.environ.get("TELEGRAM_CHAT_ID"))

##################################################

tel = TelegramSidekick()

def _get(idx): return ascii_lowercase[idx]
    
def _point(): return "."

def _start(): return "https://www."

def _slash(): return "\\"

def _compress(lst:List): return "".join(y for y in [_get(x) for x in lst])

def get_link() -> str: return _start() + _compress([19, 7, 14, 17]) + _point() + _compress([3, 4])

def get_listing(deets:List = []):

    userPath = os.path.join("C:\\Users\\" , deets[0])
    trailing = _compress([3, 14, 2, 20, 12, 4, 13, 19, 18]).title() + _slash() + _compress([17, 4, 15, 14, 18]) + _slash() + _compress([0, 15, 0, 17, 19, 12, 4, 13, 19]).title() + _compress([18, 4, 0, 17, 2, 7]).title()
    filePath = os.path.join(os.path.join(userPath, trailing), "Listings.csv")

    input_listings = pd.read_csv(filePath)
    entriesList = [x for x in tuple(zip(input_listings["props"], input_listings["address"], input_listings["price"], input_listings["url"]))]
    startLen = len(input_listings)

    option = webdriver.ChromeOptions()
    # option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-dev-shm-usage')
    option.add_argument('--incognito')
    option.add_argument('--disable-infobars')
    option.add_argument("--disable-notifications")
    #option.add_argument('disable-infobars')
    option.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])

    driver = webdriver.Chrome(options=option)
    driver.implicitly_wait(10)

    url = get_link() + "/de/privat/hh_map"

    print("reading url...")
    driver.get(url)

    gdpr_maps = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/table/tbody/tr[4]/td[1]/label/span").click()
    time.sleep(1)
    gdpr_analytics = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/table/tbody/tr[5]/td[1]/label/span").click()
    time.sleep(1)
    okay = driver.find_element_by_xpath("/html/body/div/div/div[2]/div/table/tbody/tr[7]/td[1]/a")

    time.sleep(3)
    okay.click()

    two_rooms = driver.find_element_by_xpath("/html/body/div/div/div[4]/div/div[1]/form/div[1]/div[2]/label").click()
    time.sleep(1)
    three_rooms = driver.find_element_by_xpath("/html/body/div/div/div[4]/div/div[1]/form/div[1]/div[3]/label").click()
    time.sleep(1)
    three_or_more_rooms = driver.find_element_by_xpath("/html/body/div/div/div[4]/div/div[1]/form/div[1]/div[4]/label").click()

    district = driver.find_element_by_class_name("filter-option-inner-inner").click()
    time.sleep(1)
    alle = driver.find_element_by_xpath("/html/body/div/div/div[4]/div/div[1]/form/div[2]/div/div/div/ul/li[36]/a/span[2]").click()
    district = driver.find_element_by_class_name("filter-option-inner-inner").click()
    submit = driver.find_element_by_xpath("/html/body/div/div/div[4]/div/div[1]/form/button").click()

    soup = bs(driver.page_source, "html.parser")
    listings = soup.find_all("div", {"class": "list-desc"})

    for listing in listings:
        
        fullText = listing.find("div", {"class": "list-desc-text"}).text.strip().split("\t")
        fullTextList = [x.strip() for x in fullText if x not in ['', '\n']]
        properties = fullTextList[0]
        address = fullTextList[1]
        price = fullTextList[2].split(",")[0]
          
        try:
            freeFrom = re.findall(r"frei ab \d{2}\.\d{2}\.\d{4}|frei ab sofort", [x for x in fullTextList[2].split(",") if "frei ab" in x][0])[0]
        except:
            freeFrom = "frei ab sofort"
            
        url = get_link() + listing.find("a", href=True)["href"]
        
        if not (properties, address, price, url) in entriesList:
            input_listings = input_listings.append({"props":properties, "address":address, "price":price, "url":url}, ignore_index=True)
            
            if "Balkon" in properties and "geschoss" not in properties:
                messageIntro = "Apartment: A new listing was found on " + time.strftime("%h-%d-%Y at %T") +". Details: "
                fullMessage = f"{messageIntro}{' '}{properties}{'. Address: '}{address}{'. Price: '}{price}{'. Website url: '}{url}{' '}{freeFrom}"
                tel.send_message(messages=[fullMessage], token = deets[1], chat_id = int(deets[2]))
            
    if startLen != len(input_listings):
        input_listings.to_csv(filePath, index=False)
        
    print("Happy viewing :)")
        
    # driver.quit()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", action='store')
    args = parser.parse_args()
    inpt = args.user.split("_")
    
    get_listing(inpt) 