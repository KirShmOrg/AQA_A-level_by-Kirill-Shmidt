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

    @staticmethod
    def fetch_all() -> list:
        from selenium.webdriver import Chrome
        from selenium.webdriver.common.by import By
        all_manufacturers = []
        driver = Chrome()
        driver.get(BASE_URL)
        manufs_div = driver.find_element(by=By.ID, value="AT2001")
        for manuf_a in manufs_div.find_elements(by=By.CSS_SELECTOR, value='a'):
            href = manuf_a.get_property('href')
            js_name = href[href.find('(') + 2:href.find(',') - 1]
            manufacturer_name = manuf_a.find_element(by=By.CLASS_NAME, value="choice").text
            manufacturer_name = manufacturer_name[0: manufacturer_name.index("(") - 1]
            manufacturer = RAMManufacturer(human_name=manufacturer_name, js_name=js_name)
            all_manufacturers.append(manufacturer)

        return all_manufacturers

    def __repr__(self) -> str:
        return f"RAMManufacturer <{self.__human_name}> access by <{self.js_name}>"

class Filters:
    def __init__(self, with_update: bool = False):
        if with_update:
            raise NotImplementedError("Nah-uh, wait")
        # implementation for now
        # TODO: redo this from a local file

    def

def generate_link(parameters: dict[str, str]):
    link = BASE_URL
    initial_parameters = {"category": "RAM modules"}


def human_param_to_provantage_code(human_param: str) -> str:
    checkup_table = {
        "Product Type": "31100",
        "Memory Size": "3113035",
        "Memory Technology": "31113713",
        "Memory Speed": "311971",
        "Form Factor": "311506"
    }
    if human_param in checkup_table.keys():
        return checkup_table[human_param]



def print_notes():
    human_to_provantage_ram_filter: dict[str, str] = {
        "size": "3113035",
        "ddr_type": "31113713",
        "speed": "311971",
        "form_factor": "311506",
        "": ""
    }


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
    print_notes()
    print(RAMManufacturer.fetch_all())
