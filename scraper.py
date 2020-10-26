# Selenium webscraper script to compile all free Leetcode problems and write them to files
# so you can work from your favorite IDE! Finds problems based on the HTML of
# leetcode.com as of October 20 2020

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chromedriver_py import binary_path

difficulty = "Medium"
results = 10


def find_urls(driver):
    driver.get(
        'https://leetcode.com/problemset/all/?difficulty={}'.format(difficulty))

    # Use the form control to show all tabe rows
    wait = WebDriverWait(driver, 3)
    dropdown = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'select.form-control')))
    print('hi')
    dropdown.click()
    options = dropdown.find_elements_by_css_selector('option')
    for option in options:
        text = option.get_attribute('innerText')
        print(text)
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


def main():
    # Initialize Chrome webdriver from the system's installed Chrome app
    # version 86 or newer
    options = webdriver.chrome.options.Options()
    options.headless = True
    driver = webdriver.Chrome(executable_path=binary_path, options=options)
    wait = WebDriverWait(driver, 3)
    urls = []

    try:
        urls = find_urls(driver)
        for i in range(10):
            url = urls[i]
            driver.get(url)
            description = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, 'div[data-key="description-content"]')))
            title = description.find_element_by_css_selector(
                'div[data-cy="question-title"]')
            body = description.find_element_by_css_selector(
                '[class*="question-content"]')
            print(title.get_attribute('innerText'))
            print(body.get_attribute('innerText'))

    except exceptions.TimeoutException:
        print('TIMEOUT: The page took too long to load the expected elements.')
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
