from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from tqdm import tqdm

class len_of_ele_change(object):
    """An expected condidtion that check if the len
    of an elemnt has changed
    """


    def __init__(self, driver, html_doc, length):
        # self.locator = locator
        self.html_doc = html_doc
        # self.current_len = len(self.html_doc.find(id='infinite'))
        self.driver = driver
        self.length = length
        self.times_same = 0
        
        self.new_len = len(BeautifulSoup(self.driver.execute_script('return document.documentElement.outerHTML;'), 'html.parser').find(id='infinite'))
        self.nums = [self.length, self.new_len]
    

    def __call__(self, driver):
        
        # tqdm()
        # nums = [self.length, new_len]
        # print("Old Length: {}".format(self.length))
        # print("New Length: {}".format(new_len))
        # print('Numbers: {}'.format(nums))
        # print('\n')
        

        if self.nums[0] == self.length and self.nums[1] == self.new_len:
            self.times_same += 1
        else:
            self.times_same = 0
            self.nums = [self.length, self.new_len]
        
        if self.times_same > 4:
            return True #self.driver.find_element_by_id((By.ID, 'infinite'))
        else:
            # self.length = new_len
            return False