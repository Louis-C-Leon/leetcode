# Selenium webscraper script to compile all free Leetcode problems and write them to files
# so you can work from your favorite IDE! Finds problems based on the HTML of
# leetcode.com as of October 20 2020

import os
import re
import unicodedata
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chromedriver_py import binary_path

difficulty = "Medium"
results = 10


def setup_driver():
    # Initialize Chrome webdriver from the system's installed Chrome app
    # version 86 or newer
    options = webdriver.chrome.options.Options()
    options.headless = True
    driver = webdriver.Chrome(executable_path=binary_path, options=options)
    return driver


def find_urls(driver, wait):
    driver.get(
        'https://leetcode.com/problemset/all/?difficulty={}'.format(difficulty.capitalize()))

    # Use the form control to show all tabe rows
    dropdown = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'select.form-control')))
    dropdown.click()
    options = dropdown.find_elements_by_css_selector('option')
    for option in options:
        text = option.get_attribute('innerText')
        if text == 'all':
            option.click()
            break

    # Get the main table of problems and a list of the table rows
    table = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, 'tbody.reactable-data')))
    rows = table.find_elements_by_css_selector('tr')

    # Iterate through the rows and find the free problems
    free_problem_urls = []
    for row in rows:
        # Look for "Subscribe to unlock" icon in the row
        try:
            selector = 'span[data-original-title="Subscribe to unlock"]'
            row.find_element_by_css_selector(selector)
        # If no lock icon, then save the URL
        except exceptions.NoSuchElementException:
            link = row.find_element_by_css_selector('a')
            url = link.get_attribute('href')
            free_problem_urls.append(url)
        finally:
            if results != 'all' and len(free_problem_urls) >= results:
                break
            continue

    return free_problem_urls


def write_local_problem(driver, wait, url, directories):
    driver.get(url)

    # Select Python 3 as the language
    lang_select = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, 'div[class*="ant-select-enabled"')))
    lang_select.click()
    python_option = driver.find_element_by_css_selector(
        'li[data-cy="lang-select-Python3"]')
    python_option.click()

    # Get the question title, body, and starting code
    title = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, 'div[data-cy="question-title"]')))
    body = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, '[class*="question-content"]')))
    code = driver.find_element_by_css_selector(
        'div.CodeMirror-code')

    # Grab the text from the page elements
    code_text = re.sub(r"\d\n", "", code.get_attribute('innerText'))
    code_text = re.sub(r"\xa0", " ", code_text)
    code_text = re.sub(r"\n\s{8}$", "", code_text)
    title_text = title.get_attribute('innerText')
    folder_name = re.sub(r"(\.|\s)+", "_", title_text).lower()

    # Create a folder and start writing files
    if folder_name in directories or folder_name + "_wip" in directories:
        print('Skipping problem: {}.\nFound existing local folder.'.format(title_text))
        return
    else:
        # create folder with "_wip" suffix for work in progress; won't be committed to git
        print('Creating folder for problem with prompt: {}.'.format(title_text))
        os.mkdir(folder_name + "_wip")

        # Use BS for the body for easier section navigation
        body_soup = BeautifulSoup(
            body.get_attribute('innerHTML'), 'html.parser')
        parts = body_soup.div.contents

        with open('{}/prompt.md'.format(folder_name + '_wip'), 'w') as f:
            f.write('# ' + title_text + '\n\n')
            for part in parts:
                if part.name == 'p':
                    if part.get_text().strip() == '':
                        continue
                    elif part.contents[0].name != 'strong':
                        f.write(part.get_text() + '\n\n')
                    else:
                        f.write('## ' + part.get_text() + '\n\n')
                elif part.name == 'pre':
                    f.write('```' + '\n' + part.get_text() +
                            '\n' + '```' + '\n\n')
                elif part.name == 'ul':
                    items = part.find_all('li')
                    for item in items:
                        f.write('- ' + item.get_text() + '\n')
                else:
                    continue

        with open('{}/solution.py'.format(folder_name + '_wip'), 'w') as f:
            f.write(code_text)


def main():
    driver = setup_driver()
    wait = WebDriverWait(driver, 3)
    directories = os.listdir()

    try:
        urls = find_urls(driver, wait)
        for i in range(1):
            url = urls[i]
            write_local_problem(driver, wait, url, directories)

    except exceptions.TimeoutException:
        print('TIMEOUT: The page took too long to load the expected elements.')
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
