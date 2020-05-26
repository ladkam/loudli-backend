import time
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from .Scraper import Scraper
from .utils import *
from .utils import AnyEC
import os
import pandas as pd
import shutil



class AnchorScraper(Scraper):
    """
    Scraper for Personal LinkedIn Profiles. See inherited Scraper class for
    details about the constructor.
    """

    def scrape(self):
        url="https://anchor.fm/login"
        self.submit_ = {
            'type': 'xpath',
            'username': "//input[@type='email']",
            'password': "//input[@type='password']",
            'submit': "//button[@type='submit']"
        }
        field_location = self.submit_
        self.login(url,field_location)
        if not self.loggedin:
            return []
        episode_list = self.get_episodes()
        self.get_stats(episode_list)
        print('{} episode(s) found'.format(len(episode_list)))
        return self.read_data()

    def read_data(self):
        directory = self.saveDirectory
        df = pd.DataFrame(columns=['Time (UTC)','Plays','episode'])
        for filename in os.listdir(directory):
            if filename:
                temp = pd.read_csv(os.path.join(directory,filename),sep=',')
                temp['episode'] = filename.split('_')[0]
                df=pd.concat([df,temp],axis=0)
            else:
                continue
        df['Time (UTC)']=pd.to_datetime(df['Time (UTC)'])
        shutil.rmtree(self.saveDirectory)
        print('Reading data')
        return df

    def get_episodes(self):
        self.driver.get('https://anchor.fm/dashboard/episodes')
        time.sleep(10)
        page = BeautifulSoup(self.driver.page_source, 'html.parser')
        episodes_list = all_or_default(page, 'a.css-qgnlbk', default=[])

        episodes_list = ['https://anchor.fm' + l["href"] for l in episodes_list]
        print(episodes_list)
        return episodes_list

    def get_stats(self,episode_list):
        for episode in episode_list:
            self.driver.get(episode)
            sign_in_button = WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located((By.CLASS_NAME, 'styles__dropdown___3aoQ6')))
            sign_in_button.click()
            select = WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located((By.CLASS_NAME, 'css-1f8f3uu')))
            select.click()
            self.scroll_to_bottom()
            file = WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located((By.CLASS_NAME, 'css-c9fdjl')))
            time.sleep(0.1)
            file.click()
            time.sleep(0.1)