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
import logging
import logging
import glob

logger = logging.getLogger('analyzer')



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
        logger.info("Trying logging in to get stats")
        self.login(url,field_location)
        if not self.loggedin:
            logger.error("Login failed")
            return []
        episode_list = self.get_episodes()
        logger.info("Getting the stats")
        self.get_stats(episode_list)
        logger.info('{} episode(s) found'.format(len(episode_list)))
        return self.read_data()

    def read_data(self):
        directory = self.saveDirectory
        df = pd.DataFrame(columns=['Time (UTC)','Plays','episode'])
        for filename in os.listdir(directory):
            logger.info(filename+'reading')
            if filename:
                temp = pd.read_csv(os.path.join(directory,filename),sep=',')
                logger.info('{} lines found'.format(temp.shape[0]))
                temp['episode'] = filename.split('_')[0]
                df=pd.concat([df,temp],axis=0)
            else:
                continue
        df['Time (UTC)']=pd.to_datetime(df['Time (UTC)'])
        #shutil.rmtree(self.saveDirectory)
        logger.info('{} lines found'.format(df.shape[0]))
        return df

    def get_episodes(self):
        self.driver.get('https://anchor.fm/dashboard/episodes')
        time.sleep(5)
        page = BeautifulSoup(self.driver.page_source, 'html.parser')
        episodes_list = all_or_default(page, 'a.css-qgnlbk', default=[])
        episodes_list = ['https://anchor.fm' + l["href"] for l in episodes_list]
        return episodes_list

    def get_stats(self,episode_list):
        lenEL = 1
        for episode in episode_list:
            self.driver.get(episode)
            sign_in_button = WebDriverWait(self.driver, 100).until(ec.visibility_of_element_located((By.CLASS_NAME, 'styles__dropdown___3aoQ6')))
            sign_in_button.click()
            select = WebDriverWait(self.driver, 100).until(ec.visibility_of_element_located((By.CLASS_NAME, 'css-1f8f3uu')))
            select.click()
            self.scroll_to_bottom()
            file = WebDriverWait(self.driver, 100).until(ec.visibility_of_element_located((By.CLASS_NAME, 'css-c9fdjl')))
            time.sleep(0.1)
            file.click()
            logger.info('Download Started')
            files = 0
            """
            while(files  != lenEL):
                time.sleep(0.5)
                files = len(glob.glob(os.path.join(self.saveDirectory,'*.csv')))
                logger.info('not found')
            logger.info('download endedls')
            lenEL=lenEL+1
            """
            time.sleep(30)