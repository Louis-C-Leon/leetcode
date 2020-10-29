# Selenium webscraper script to compile all free Leetcode problems and write them to files
# so you can work from your favorite IDE! Finds problems based on the HTML of
# leetcode.com as of October 20 2020

import os
import re
import argparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chromedriver_py import binary_path


class Scraper():
    def __init__(self, count, difficulty):
        print("\nSetting up scraper...")
        self.count = count
        self.difficulty = difficulty
        options = webdriver.chrome.options.Options()
        options.headless = True
        self.driver = webdriver.Chrome(
            executable_path=binary_path, options=options)
        self.wait = WebDriverWait(self.driver, 3)
        self.problem_urls = []
        self.directories = os.listdir()

    # lowercase title and replace space and '.' chars with '_'
    def format_title(self, title):
        return re.sub(r"(\.|\s)+", "_", title).lower()

    # find free problem urls from leetcode HTML
    def get_urls(self):
        print("\nFinding free problem URLs from leetcode.com...")
        self.driver.get(
            'https://leetcode.com/problemset/all/?difficulty={}'.format(self.difficulty))
        self.wait.until(EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, 'select.form-control, tbody.reactable-data tr')))

        # Use the form control to show all table rows
        dropdown = self.driver.find_element_by_css_selector(
            'select.form-control')
        dropdown.click()
        options = dropdown.find_elements_by_css_selector('option')
        for option in options:
            text = option.get_attribute('innerText')
            if text == 'all':
                option.click()
                break

        table = self.driver.find_element_by_css_selector(
            'tbody.reactable-data')
        rows = table.find_elements_by_css_selector('tr')
        for row in rows:
            # Look for "Subscribe to unlock" icon in the row
            try:
                selector = 'span[data-original-title="Subscribe to unlock"]'
                row.find_element_by_css_selector(selector)
            # If no lock icon, then save the URL
            except exceptions.NoSuchElementException:
                link = row.find_element_by_css_selector('a')
                url = link.get_attribute('href')
                title = link.get_attribute('innerText')
                problem_number = row.get_attribute(
                    'innerText').strip().split()[0]
                full_title = problem_number + '. ' + title
                if self.format_title(full_title) in self.directories:
                    continue
                else:
                    self.problem_urls.append(url)
            finally:
                if self.count != 'all' and len(self.problem_urls) >= self.count:
                    break
                continue

    def write_local_problem(self, url):
        self.driver.get(url)
        self.wait.until(EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, 'div[class*="ant-select-light"], div[data-cy="question-title"], [class*="question-content"]')))

        # Select Python 3 as the language
        lang_select = self.driver.find_element_by_css_selector(
            'div[class*="ant-select-light"]')
        lang_select.click()
        python_option = self.driver.find_element_by_css_selector(
            'li[data-cy="lang-select-Python3"]')
        python_option.click()

        # Get the question title, body, and starting code
        title = self.driver.find_element_by_css_selector(
            'div[data-cy="question-title"]')
        body = self.driver.find_element_by_css_selector(
            '[class*="question-content"]')
        code = self.driver.find_element_by_css_selector(
            'div.CodeMirror-code')

        # Grab the text from the page elements and do simple formatting
        # Delete line numbers
        code_text = re.sub(r"\d\n", "", code.get_attribute('innerText'))
        # Replace unicode whitespace chars
        code_text = re.sub(r"\xa0", " ", code_text)
        # Delete the last line of empty space
        code_text = re.sub(r"\n\s{8}$", "", code_text)
        # Name the folder after the problem title; remove '.' and space chars
        title_text = title.get_attribute('innerText')
        folder_name = self.format_title(title_text)

        print('Scraping page for: ' + title_text)
        os.mkdir(folder_name)

        # Use BS for the body to iterate through different tags
        body_soup = BeautifulSoup(
            body.get_attribute('innerHTML'), 'html.parser')
        parts = body_soup.div.contents

        # Create formatted .md document with problem description, examples,
        # and constraints. Ignore embedded images.
        with open('{}/prompt.md'.format(folder_name), 'w') as f:
            f.write(url + '\n\n')
            f.write('# ' + title_text + '\n\n')
            for part in parts:
                # General descriptions and headings are in <p> tags
                if part.name == 'p':
                    # Ignore empty <p> tag
                    if part.get_text().strip() == '':
                        continue
                    # If the inner tag is <strong>, make the line a subheading
                    elif part.contents[0].name == 'strong':
                        f.write('## ' + part.get_text() + '\n\n')
                    else:
                        f.write(part.get_text() + '\n\n')
                # Starting code is in a <pre> tag
                elif part.name == 'pre':
                    f.write('```' + '\n' + part.get_text() +
                            '\n' + '```' + '\n\n')
                # Constraints for the problem are in a <ul> tag
                elif part.name == 'ul':
                    items = part.find_all('li')
                    for item in items:
                        f.write('- ' + item.get_text() + '\n')
                else:
                    continue

        # Create .py file containing the starting code
        with open('{}/solution.py'.format(folder_name), 'w') as f:
            f.write(code_text)

    def write_all_problems(self):
        for url in self.problem_urls:
            self.write_local_problem(url)

    def scrape(self):
        self.get_urls()
        self.write_all_problems()


# Set up arguments for invoking script
parser = argparse.ArgumentParser(
    description='Scrape free problems from leetcode.com and write them to local files')

parser.add_argument('--difficulty', '-d',
                    choices=['easy', 'medium', 'hard'],
                    default='medium',
                    help='select the difficulty of problems (default medium)')

parser.add_argument('--count', '-c',
                    default='10',
                    help='choose a number of remote problems to be scraped, or "all" (default 10).')


def main():
    arguments = parser.parse_args()
    count = arguments.count
    if count != 'all':
        try:
            count = int(count)
        except ValueError:
            raise ValueError(
                'Invalid "count" (-c, --c) value. Should be an integer or "all"')

    scraper = Scraper(count, arguments.difficulty.capitalize())
    scraper.scrape()


if __name__ == "__main__":
    main()
