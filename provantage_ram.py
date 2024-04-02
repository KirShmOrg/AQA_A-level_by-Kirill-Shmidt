import time

from bs4 import BeautifulSoup
from bs4.element import Tag
import requests

# from component_classes.class_ram import RAM

# The general logic of filters: An: key n, Vn: value n (e.g. A1 V1)

BASE_URL = 'https://www.provantage.com/service/searchsvcs/B-CRAMM'


class RAMManufacturer:
    def __init__(self, human_name: str, js_name: str):
        self.__human_name = human_name
        self.__js_name = js_name

    @property
    def human_name(self) -> str:
        return self.__human_name

    @property
    def js_name(self) -> str:
        return self.__js_name

    def __repr__(self) -> str:
        return f"RAMManufacturer <{self.__human_name}> access by <{self.js_name}>"


def get_generation():
    page = requests.get(BASE_URL)
    soup = BeautifulSoup(page.text, features="html.parser")
    # searchbox = soup.find('input', attrs={'class': "SEARCHBOX"})

    # ID of div with all manufacturers: "AT2001", class="sel". tag in request header: MAN={value}
    # where value is the parameter of js function inside this div from div.a.href
    manufacturers_div = soup.find('div', attrs={'id': "AT2001"})
    for element in soup.find_all('a', attrs={'class': 'choice'}):
        print(element.text)


def get_filters():
    from selenium.webdriver import Chrome
    driver = Chrome()
    driver.get(BASE_URL)
    time.sleep(3)
    from selenium.webdriver.common.by import By
    # all_tables = driver.find_element(by=By.ID, value='ATTRIB1').find_elements(by=By.XPATH,
    #                                                                           value='//table[@class="sel"]')

    manufacturers_div = driver.find_element(by=By.ID, value="AT2001")
    for a_tag in manufacturers_div.find_elements(by=By.TAG_NAME, value='a'):
        href = a_tag.get_property('href')
        js_name = href[href.find('(') + 2:href.find(',') - 1]
        manufacturer_name = a_tag.find_element(by=By.CLASS_NAME, value="choice").text
        manufacturer_name = manufacturer_name[0: manufacturer_name.index("(") - 1]
        manufacturer = RAMManufacturer(human_name=manufacturer_name, js_name=js_name)
        print(manufacturer)

        next_link = BASE_URL + aLinkMCCopy(manufacturer.js_name, '2001')
        print(next_link)
    time.sleep(120)

def print_notes():
    human_to_provantage_ram_filter: dict[str, str] = {
        "size": "3113035",
        "ddr_type": "31113713",
        "speed": "311971"
    }

#
def aLinkMCCopy(t: str, b: str):
    # function ALinkMC(t,b){var a='/service/searchsvcs/B-CRAMM?';if(b==2001)a+='MAN='+t;else a+='CAT='+t;window.location.href=a;}
    a = '/service/searchsvcs/B-CRAMM?'
    if b == '2001':
        a += 'MAN='
    else:
        a += 'CAT='
    a += t
    return a


def aLinkCopy():  # Used heavily, from what it seems
    # function ALink(t, b){var a = '/service/searchsvcs/B-CRAMM?A1=3113035&V1=8+GB';if (t == 'Various')t='Unclassified';t=t.replace( / ` / g, "'");t=t.replace( / ~ / g, '"');t=t.replace( / % / g, '%25');t=t.replace( / \+ / g, '%2B');a=a+'&A2='+b+'&V2='+t;a=a.replace( / / g, '+');window.location.href=a;}
    pass


if __name__ == '__main__':
    # get_generation()
    get_filters()
