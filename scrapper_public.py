"""
It is not the strongest species that survive,
nor the most intelligent, but the ones most responsive to change
    -Charles Darwin
"""

import requests
from bs4 import BeautifulSoup
import os
import sys
from time import sleep
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from time import sleep
from custom_EC import len_of_ele_change


IS_WINDOWS = None
WEBSITE = "https://academyofideas.com"
MEMBERS_AREA = 'https://academyofideas.com/members-area'
global CATEGORY_TITLE
CATEGORY_TITLE = ""


print("Welcome, this program scrapes the transcript from an Academy of Ideas article(s).\n")

if sys.platform == 'win32' or sys.platform == 'cygwin':
    IS_WINDOWS = True
else:
    IS_WINDOWS = False

# This returns a request.Session object. Will return an authenticated session if user requests.
def generate_session():

    client = requests.Session()
    acceptable_choice = True
                
    return client

CLIENT = generate_session()

# This function took me 2 weeks to get fully functional lmao.
# Had to build my own custom selenium module, that was fun.
def return_main_htmldoc(category=MEMBERS_AREA):
    height = 0
    page_loaded = False
    at_bottom = False
    driver_options = webdriver.FirefoxOptions()
    driver_options.add_argument('--headless')
    with webdriver.Firefox(options=driver_options) as driver:
        print("Loading...")
        driver.get(category)
        global CATEGORY_TITLE
        title = driver.find_element_by_class_name('page-title').text
        CATEGORY_TITLE = title

        # print("The title for this category link is: {}".format(title))


        while at_bottom == False:
            #Wait until page is loaded before saving the html doc height.
            first_page_load_wait = WebDriverWait(driver, 15)
            first_page_load_wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'page-title')))
            browser_height = driver.execute_script("return document.body.scrollHeight;")
            load_new_articles_wait = WebDriverWait(driver, 20)

            
            if browser_height == height:
                at_bottom = True
                html = driver.execute_script('return document.documentElement.outerHTML;')
            else:
                height = browser_height
                # load_new_articles_wait.until()
                driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
                # Explicit wait here for when new article publications load
                html_doc = BeautifulSoup(driver.execute_script('return document.documentElement.outerHTML;'), 'html.parser')
                current_ele_len = len(html_doc.find(id='infinite'))
                load_new_articles_wait.until(len_of_ele_change(driver=driver, html_doc=html_doc, length=current_ele_len))

    pretty_publication = BeautifulSoup(html, 'html.parser')
    return pretty_publication


def set_mode():
    user_choice = str(input("Are you scraping an Article, or category of articles? (a/c): ")).lower()
    if user_choice == 'c':
        return True
    
    elif user_choice == "a":
        return False

    else:
        print("Invalid Choice\n")
        sleep(1)
        set_mode()


CATEGORY_MODE = set_mode()

# Little bit of recursion here :P
# This helped me better understan how computers call functions, and how return values work.
def get_category_link():
    user_category = str(input('Enter category links here: '))

    # Checking if the chosen links is valid
    if user_category.startswith("https://academyofideas.com/category/"):
        doc = return_main_htmldoc(user_category)
        return doc
    else:
        print("Invalid category link. Eg. https://academyofideas.com/category/abraham-maslow/\n")
        sleep(2)
        doc = get_category_link()
        return doc

if CATEGORY_MODE == True:
    MAIN_DOC = get_category_link()

# If cateory mode is true this function will need to be called
# So that we can grab all of the links from the that specific page, and store them all.
def link_list(category_page_doc):
    array_of_articles = category_page_doc.find_all("h2", {"entry-title"})
    link_list = []
    for i in array_of_articles:
        link_list.append(i.find('a')['href'])
    return link_list


if CATEGORY_MODE == True:
    raw_category_links = link_list(MAIN_DOC)


class Link():
    '''
    This class is used so that we can store all of the approprate attributes in an organized manner
    '''
    def __init__(self, link, isCategory=False):
        self.my_link = link
        self.password = None
        self.isCategory = isCategory

    def set_password(self, password):
        self.password = password

    def set_doc(self, doc):
        self.doc = doc

    def set_title(self, title):
        self.title = title

    def set_transcript(self, transcript):
        self.transcript = transcript


    def get_link(self):
        return self.my_link

    def get_doc(self):
        return self.doc

    def get_title(self):
        return self.title

    def get_transcript(self):
        return self.transcript

    
    def get_password(self):
        return self.password



class Article():
    '''
    This class manipulates the List class objects, then creats files in folders
    unique files in folders from the specific objects attributes.
    Ie. creating a transcrip file, its data being what the List objects's module "get_transcript" returns.
    '''
    def __init__(self):
        self.link_objs = []
        # self.inappropriate_special_characters = ['\n' ,' ',',']
        self.members_area = MEMBERS_AREA
        self.session = CLIENT
        if IS_WINDOWS == True:
            self.home_directory = r"{}".format(os.environ.get('HOME'))
        else:
            self.home_directory = os.environ.get('HOME') + '/'
    
    def set_link(self):
        link = ''
        if CATEGORY_MODE == False:
            link = str(input("Enter article link here: "))
            self.link_objs.append(Link(link, CATEGORY_MODE))
        elif CATEGORY_MODE == True:
            for i in raw_category_links:
                self.link_objs.append(Link(i))

    def check_link(self):
        err = '"{}" is an invalid link. Eg: "https://academyofideas.com/2019/01/carl-jung-value-of-anxiety-disorders/"'
        for i in range(0, len(self.get_link())):
            if not self.get_link()[i].get_link().startswith(WEBSITE):
                print(err.format(self.get_link()[i]))
                self.set_link()


    def get_link(self):
        return self.link_objs

    # Note, this function will prefrom a "GET" request.
    def set_html_doc(self):
        responses = []
        for i in self.get_link():
            i.response = CLIENT.get(i.my_link)
            i.set_doc(BeautifulSoup(i.response.content, 'html.parser'))
    # def set_path(self, obj):

    def set_password(self):
        for i in self.get_link():
            if i.get_doc().find('button', {'class': 'btn btn-copy'}):
                i.set_password(i.get_doc().find('button', {'class': 'btn btn-copy'}).contents[0])
                return True
            else:
                i.set_password(None)
                return False

    def get_password(self, obj):
        return obj.get_password()

    def set_title(self):
        for i in self.get_link():
            i.set_title(i.get_doc().find('title').text)

    def get_title(self, obj):
        return obj.get_title()

    def set_transcript(self):
        skippable_elements = ("Further Readings",
         "View art in video",
         "The following is a transcript of this video",
         "Get a FREE membership video! Subscribe to our Newsletter."
        )

        for i in self.get_link():
            transcript = []
            transcript_as_string = ''
            contents = i.get_doc()
            entry_content_section = i.get_doc().find('div', {'class':'entry-content'})
            # For finding cites, use find all next from the "p" quote tag.
            # This will ensure that text will be grabbed wither wrapped in "a" tag or "p" tag

            for j in entry_content_section.find_all(['p', 'blockquote'], recursive=False):
                if j.find('cite'):
                    transcript.append(j.find('p').text + " -" + j.find('p').find_next().text + '\n\n')
                else:
                    transcript.append(j.text + '\n\n')
            for j in transcript:
                # This skips a line if its unwanted in the transcript. Eg. View art in video, Further Reading etc.
                if not j.startswith(skippable_elements):
                    transcript_as_string += j
                
            i.set_transcript(transcript_as_string)
        return transcript_as_string

    def get_transcript(self, obj):
        return obj.get_transcript()
    

    def build_object(self):
        err = "Example links: https://academyofideas.com/2018/09/passivity-mediocrity-mental-illness/"
        self.set_link()
        self.check_link()
        self.set_html_doc()
        self.set_title()
        self.set_password()
        self.set_transcript()

    # If an article parent folder already exhists, and user wants to scrape it anyway, create a new folder with number added on
    # Eg. Existing folder: articletitle  New folder: articletitle(1) 
    def file_exists_handler(self, path, obj):
        for num in range(1, 99):
            if not os.path.isdir(path + '({})'.format(str(num))):
                new_path = self.main_folder_container + '{}({})'.format(obj.get_title(), str(num))
                return new_path
                

    # This is the functions that creates the "article" file, and the container folder for each article.
    # This function also checks before making the folder that will contain the transcript file, to see if there is already one created.
    def create_parent_folders(self):
        if CATEGORY_MODE == True:
            self.main_folder_container = self.home_directory + "Articles/"
            self.category_folder = self.main_folder_container + CATEGORY_TITLE + '/'
        else:
            self.main_folder_container = self.home_directory + "Articles/"

        for i in self.get_link():
            full_path = self.main_folder_container + i.get_title()
            
            if not os.path.isdir(self.main_folder_container):
                if CATEGORY_MODE == False:
                    try:
                        os.mkdir(self.main_folder_container)
                    except FileExistsError:
                        # If the file already exists, we dont need to make it.
                        pass
                else:
                    try:
                        os.mkdir(self.main_folder_container)
                    except FileExistsError:
                        pass
                    try:
                        os.mkdir(self.category_folder)
                    except FileExistsError:
                        pass
                    
            if CATEGORY_MODE == False:        
                try:
                    os.mkdir(self.main_folder_container + '{}'.format(i.get_title()))

                    # If the file already exists, its likely the article has already been scraped
                    # Ask user if user wants file scrapped again anyway.
                except FileExistsError:
                    while True:
                        sleep(1)
                        user_choice = str(input('\nThe article: "{}" has already been scraped.\n Would you like to scrape it anyway? (y/n): '.format((i.get_title()))).lower())
                        if user_choice == 'y' or user_choice == 'n':
                            break
                    if user_choice == 'y':
                        new_path = self.file_exists_handler(full_path, i)
                        os.mkdir(new_path)
                        self.create_transcript_file(obj=i, path=new_path)

                    elif user_choice == 'n':
                        print("Skipping: {}".format(i.get_title()))
            else:
                try:
                    os.mkdir(self.category_folder + '{}'.format(i.get_title()))

                # If the file already exists, its likely the article has already been scraped
                # Ask user if user wants file scrapped again anyway.
                except FileExistsError:
                    while True:
                        sleep(1)
                        user_choice = str(input('\nThe article: "{}" has already been scraped.\n Would you like to scrape it anyway? (y/n): '.format((i.get_title()))).lower())
                        if user_choice == 'y' or user_choice == 'n':
                            break
                    if user_choice == 'y':
                        new_path = self.file_exists_handler(full_path, i)
                        os.mkdir(new_path)
                        self.create_transcript_file(obj=i, path=new_path)

                    elif user_choice == 'n':
                        print("Skipping: {}".format(i.get_title()))

    # When this function is called with a path parameter
    # It means that a duplicate folder was found, and an alterative file name will be used instead in the creation
    # of data container.
    def create_transcript_file(self, obj=None, path=None):
        total_articles = len(self.get_link())
        if obj == None:
            if CATEGORY_MODE == False:
                for i in tqdm(self.get_link()):
                    with open(self.main_folder_container + i.get_title() +'/transcript.txt', 'w') as f:
                        if i.get_password() != None:
                            f.write(f'The password for the membership video is: {i.get_password()}\n\n' + i.get_transcript())
                        else:
                            f.write('{}'.format(i.get_transcript()))
                        sleep(0.25)
                        print('The article "{}", has been scrapped sucessfully!'.format(i.get_title()))
                        f.close()
            else:
                for i in tqdm(self.get_link()):
                    with open(self.category_folder + i.get_title() +'/transcript.txt', 'w') as f:
                        if i.get_password() != None:
                            f.write(f'The password for the membership video is: {i.get_password()}\n\n' + i.get_transcript())
                        else:
                            f.write('{}'.format(i.get_transcript()))
                        sleep(0.25)
                        print('The article "{}", has been scrapped sucessfully!'.format(i.get_title()))
                        f.close()
        else:
            with open(path +'/transcript.txt', 'w') as f:
                    if obj.get_password() != None:
                        f.write(f'The password for the membership video is: {obj.get_password()}\n\n' + obj.get_transcript())
                    else:
                        f.write('{}'.format(obj.get_transcript))
                    sleep(0.25)
                    print('The article "{}", has been scrapped sucessfully!'.format(obj.get_title()))
                    f.close()

    def create_files(self):
        self.create_parent_folders()
        self.create_transcript_file()

    def run(self):
        # Sets Object attributes
        self.build_object()
        # Creates files and folders and writes respective data into them.
        self.create_files()


# This function runs the entire program
def run():
    x = Article()
    x.run()
    print("Done!")

run()
