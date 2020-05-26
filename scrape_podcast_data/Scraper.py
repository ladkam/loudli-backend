import time
from time import sleep

import selenium.webdriver
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
import os


class Scraper(object):
    """
    Wrapper for selenium Chrome driver with methods to scroll through a page and
    to scrape and parse info from a linkedin page

    Params:
        - cookie {str}: li_at session cookie required to scrape linkedin profiles
        - driver {webdriver}: driver to be used for scraping
        - scroll_pause {float}: amount of time to pause (s) while incrementally
        scrolling through the page
        - scroll_increment {int}: pixel increment for scrolling
        - timeout {float}: time to wait for page to load first batch of async content
    """

    def __init__(self,podcast,username,password,scraperInstance=None, driver = webdriver.Chrome('/Users/amine/work/django_api_marketPlace/driver/chromedriver'), scroll_pause=0.05, scroll_increment=200, timeout=3000):
        if type(self) is Scraper:
            raise Exception(
                'Scraper is an abstract class and cannot be instantiated directly')
        if scraperInstance:
            self.was_passed_instance = True
            self.driver = scraperInstance.driver
            self.scroll_increment = scraperInstance.scroll_increment
            self.timeout = scraperInstance.timeout
            self.scroll_pause = scraperInstance.scroll_pause
            self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            self.driver.implicitly_wait(15)
            return

        self.saveDirectory = '/Users/amine/work/django_api_marketPlace/marketplace_api/data_api/static/temp/'+podcast
        print(self.saveDirectory)
        os.mkdir(self.saveDirectory)
        print('file created')
        options = webdriver.ChromeOptions()
        prefs = {"download.default_directory": self.saveDirectory}
        options.add_experimental_option("prefs", prefs)
        self.was_passed_instance = False
        prefs = {"download.default_directory": self.saveDirectory}
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome('/Users/amine/work/django_api_marketPlace/driver/chromedriver',options=options)
        self.scroll_pause = scroll_pause
        self.loggedin =False
        self.scroll_increment = scroll_increment
        self.username = username
        self.password = password
        self.timeout = timeout
        self.driver.set_window_size(1920, 1080)

    def login(self,url,field_location):
        self.driver.get(url)
        self.driver.implicitly_wait(15)
        if field_location['type'] == 'xpath':
            userField = WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located((By.XPATH, field_location['username'])))
            passwordField = WebDriverWait(self.driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, field_location['password'])))
            submitButton = WebDriverWait(self.driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, field_location['submit'])))
        if field_location['type'] == 'name':
            userField = self.driver.find_element_by_name(field_location['username'])
            passwordField = self.driver.find_element_by_name(field_location['password'])
            submitButton = self.driver.find_element_by_name(field_location['submit'])
        userField.send_keys(self.username)
        passwordField.send_keys(self.password)
        submitButton.click()
        sleep(2)
        if self.driver.current_url==url:
            self.loggedin = False
        else:
            self.loggedin = True

    def get_html(self, url,field_location):
        self.load_profile_page(url)
        return self.driver.page_source

    def scroll_to_bottom(self):
        """Scroll to the bottom of the page

        Params:
            - scroll_pause_time {float}: time to wait (s) between page scroll increments
            - scroll_increment {int}: increment size of page scrolls (pixels)
        """
        expandable_button_selectors = [
            'button[aria-expanded="false"].pv-skills-section__additional-skills',
            'button[aria-expanded="false"].pv-profile-section__see-more-inline',
            'button[aria-expanded="false"].pv-top-card-section__summary-toggle-button',
            'button[data-control-name="contact_see_more"]'
        ]

        current_height = 0
        while True:

            # Scroll down to bottom
            new_height = self.driver.execute_script(
                "return Math.min({}, document.body.scrollHeight)".format(current_height + self.scroll_increment))
            if (new_height == current_height):
                break
            self.driver.execute_script(
                "window.scrollTo(0, Math.min({}, document.body.scrollHeight));".format(new_height))
            current_height = new_height
            # Wait to load page
            time.sleep(self.scroll_pause)

    def wait(self, condition):
        return WebDriverWait(self.driver, self.timeout).until(condition)

    def wait_for_el(self, selector):
        return self.wait(EC.presence_of_element_located((
            By.CSS_SELECTOR, selector
        )))

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.quit()

    def quit(self):
        if self.driver and not self.was_passed_instance:
            self.driver.quit()
