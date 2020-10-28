# Selenium webscraper script to compile all free Leetcode problems and write them to files
# so you can work from your favorite IDE! Finds problems based on the HTML of
# leetcode.com as of October 20 2020

import os
import re
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
    title = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, 'div[data-cy="question-title"]')))
    body = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, '[class*="question-content"]')))
    title_text = title.get_attribute('innerText')
    folder_name = re.sub(r"(\.|\s)+", "_", title_text).lower()
    if folder_name in directories:
        print('Skipping problem: {}.\nFound existing local folder.'.format(title_text))
        return
    else:
        print('Creating folder for problem with prompt: {}.'.format(title_text))
        soup = BeautifulSoup(body.get_attribute('innerHTML'), 'html.parser')
        parts = soup.div.contents
        os.mkdir(folder_name)
        with open('{}/prompt.md'.format(folder_name), 'w') as f:
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
