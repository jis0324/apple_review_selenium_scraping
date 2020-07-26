from selenium import webdriver
import time
import random
import os
from bs4 import BeautifulSoup
import csv
import re
import json

base_dir = os.path.dirname(os.path.abspath(__file__))

class Crawlsystem(object):
  def __init__(self):
    global base_dir
    self.page_source = ''

  def set_driver(self):

    options = webdriver.ChromeOptions() 
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.headless = True
    driver = webdriver.Chrome(options=options)
    return driver

  def get_data(self):
    return_data = {
        'Title' : '',
        'Total Rating' : '',
        'Rating Count' : '',
        'Reviews' : list()
    }

    ########################## convert string to DOM ########################
    soup = BeautifulSoup(self.page_source, 'lxml')

    main_content = soup.find('main', class_="selfclear")
    
    if main_content:
        title = soup.find("a", class_="see-all-header__link")
        if title:
            return_data['Title'] = title.text.strip()

        total_rating = soup.find("span", class_="we-customer-ratings__averages__display")
        if total_rating:
            return_data['Total Rating'] = total_rating.text.strip()

        rating_count = soup.find("div", class_="we-customer-ratings__count")
        if rating_count:
            return_data['Rating Count'] = rating_count.text.strip().split(' ')[0]

        review_items = main_content.find_all('div', class_="we-customer-review")
        for review_item in review_items:
            try:
                review_dict = dict()
                review_rate = review_item.find("figure", class_="we-customer-review__rating")
                if review_rate:
                    review_dict["rate"] = review_rate['aria-label'].strip()[0]

                review_user = review_item.find("span", class_="we-customer-review__user")
                if review_user:
                    review_dict["user"] = review_user.text.strip()

                review_date = review_item.find("time", class_="we-customer-review__date")
                if review_date:
                    review_dict["date"] = review_date.text.strip()

                review_title = review_item.find("h3", class_="we-customer-review__title")
                if review_title:
                    review_dict["title"] = review_title.text.strip()

                review_text = review_item.find("blockquote", class_="we-customer-review__body")
                if review_text:
                    review_dict["text"] = review_text.find("p").text.strip()

                if bool(review_dict):
                    return_data["Reviews"].append(review_dict)
            except:
                continue
    
    return return_data

  def main(self):
    self.driver = self.set_driver()
    print('----- Created Chrome Driver -----')
    self.driver.get("https://apps.apple.com/us/app/tiktok-make-your-day/id835599320#see-all/reviews")
    time.sleep(5)
    max_height = self.driver.execute_script("return document.body.scrollHeight")
    max_height_flag = 0

    i=0
    while True:
        # scroll down
        self.driver.execute_script("window.scrollTo(0, " + str(max_height) + ");")
        time.sleep(10)
        # get current document height
        current_height = self.driver.execute_script("return document.body.scrollHeight")

        if current_height > max_height:
            i += 1
            max_height = current_height
            print('-----', i, 'time scroll down -----')
        else:
            max_height_flag += 1
            if max_height_flag > 3:
                max_height_flag = 0
                break
        continue
   
    ########################## get current page source ########################
    self.page_source = self.driver.page_source
    self.driver.quit()
    return_data = self.get_data()
    
    ########################## write into file ########################
    with open( base_dir + '/result.json', 'w', newline="", encoding="utf-8", errors="ignore") as result_json:
        result_json.write(json.dumps(return_data))

if __name__ == '__main__':
  crawlsystem = Crawlsystem()
  crawlsystem.main()
