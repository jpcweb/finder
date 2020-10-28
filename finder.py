from urllib.parse import quote
import argparse

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from bcolors import bcolors

BROWSER = "google"

class Finder:
    def __init__(self):
        self.browser = BROWSER
        self.url = {"google": self.google, "duckduckgo": self.duckduckgo}
        self.element_div = {"google": "rc", "duckduckgo": "result"}

    @staticmethod
    def __get_src(url: str):
        """
        Get a web page using the Selenium Firefox Webdriver

        Parameters
        ---
        url (str)
            the url to get
        """
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(
            options=options,
            executable_path="./geckodriver",
        )
        driver.get(url)
        timeout = 2
        try:
            WebDriverWait(driver, timeout)
        except TimeoutException:
            print("Timed out...")
        finally:
            source = driver.page_source
            driver.quit()
        return source

    @staticmethod
    def google() -> str:
        return "https://www.google.com/search?tbs=qdr:w&q=%s"

    @staticmethod
    def duckduckgo() -> str:
        return "https://duckduckgo.com/?t=h_&df=w&ia=web&q=%s"

    def search(self, *argv) -> list:
        """
        Get the web page, parse and crawl it and return the results

        Parameters
        ---
        *argv (list[str])
          the terms

        Result
        ---
        list
        """
        words = '+'.join(argv)
        url_browser = self.url.get(self.browser)

        if url_browser is None:
            print(
                bcolors.colored("[ ! ] " + self.browser + " is not available",
                                bcolors.WARNING))
            return []

        response = self.__get_src(url_browser() % quote(words))
        soup = BeautifulSoup(response, 'html.parser')
        result_elements = soup.findAll('div',
                                       class_=self.element_div[self.browser])
        results = []
        for element in result_elements:
            title, url = self.__crawler(element)
            if title is not None and url is not None:
                results.append({
                    'title': title,
                    'url': url,
                })
        return results

    def __crawler(self, element) -> (str, str):
        """
        Crawl the html page and get titles and links

        Result
        ---
        (str, str)
        """
        if self.browser == "google":
            return element.find('h3').text, element.find('a')['href']
        if self.browser == "duckduckgo":
            return element.find(
                'a', class_="result__a").getText() if element.find(
                    'a', class_="result__a"
                ) is not None else None, element.find('a')['href']
        return None, None

    def format(self, browser, *argv):
        """
        Set the browser and format the news

        Parameters
        ---
        browser (str)
            the browser
        *argv (list[str])
            the terms
        """
        self.browser = browser
        results = self.search(*argv)
        for res in results:
            print(bcolors.colored(res['title'], bcolors.OKBLUE))
            print(bcolors.colored(res['url'], bcolors.OKGREEN) + "\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser',
                        default=BROWSER,
                        help='Choose a browser: google, duckduckgo')
    parser.add_argument('terms', nargs='*')
    result = parser.parse_args()
    terms = " ".join(result.terms)

    print(
        bcolors.colored(
            "Finder: You want to know about " + terms + " on " +
            result.browser, bcolors.HEADER)+"\n")

    Finder().format(result.browser, terms)
