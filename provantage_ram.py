# import time

from bs4 import BeautifulSoup
from bs4.element import Tag
import requests

# from component_classes.class_ram import RAM

# The general logic of filters: An: key n, Vn: value n (e.g. A1 V1)

BASE_URL = 'https://www.provantage.com/service/searchsvcs/B-CRAMM'


class RAMManufacturer:
    def __init__(self, human_name: str = None, js_name: str = None):
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
        for_json = {}
        for manuf_a in manufs_div.find_elements(by=By.CSS_SELECTOR, value='a'):
            href = manuf_a.get_property('href')
            js_name = href[href.find('(') + 2:href.find(',') - 1]
            manufacturer_name = manuf_a.find_element(by=By.CLASS_NAME, value="choice").text
            manufacturer_name = manufacturer_name[0: manufacturer_name.index("(") - 1]
            manufacturer = RAMManufacturer(human_name=manufacturer_name, js_name=js_name)
            for_json.update({manufacturer_name: js_name})
            all_manufacturers.append(manufacturer)

        import json
        filepath = "all_jsons/provantage_manufacturers.json"
        with open(filepath, 'w') as file:
            json.dump(for_json, file, indent=4)
            file.truncate()
            print(f"Updated '{filepath}'")

        return all_manufacturers

    def __cmp__(self, other) -> bool:
        if not isinstance(other, RAMManufacturer):
            raise TypeError("You can only compare within the RAMManufacturer class")
        return self.js_name == other.js_name or self.human_name == other.human_name

    def __repr__(self) -> str:
        return f"RAMManufacturer <{self.__human_name}> access by <{self.js_name}>"


class Filters:
    def __init__(self, with_update: bool = False):
        if with_update:
            raise NotImplementedError("Nah-uh, wait")
        # implementation for now
        # TODO: redo this from a local file


def generate_link(parameters: dict[str, str]) -> str:
    link = BASE_URL + "?"
    initial_parameters = {"category": "RAM modules"}

    if "manufacturer" in parameters.keys():
        manuf_to_find = parameters.pop('manufacturer')

        import json
        with open('all_jsons/provantage_manufacturers.json', 'r') as file:
            manufacturers = json.load(file)

        if manuf_to_find not in manufacturers:
            raise ValueError(f"""The manufacturer '{manuf_to_find}' was not found on the website""")

        link += f"MAN={manufacturers[manuf_to_find]}"

    counter = 1
    for key, value in parameters.items():
        provantage_code = human_param_to_provantage_code(key)
        html_param_value = value.replace(' ', '+')
        link += f"&A{counter}={provantage_code}&V{counter}={html_param_value}"
        counter += 1

    return link


def human_param_to_provantage_code(human_param: str) -> str:
    checkup_table = {
        "Product Type": "31100",
        "Size": "3113035",
        "Technology": "31113713",
        "Speed": "311971",
        "Form Factor": "311506"
    }

    for name, code in checkup_table.items():
        if human_param in name.lower():
            return code
    raise ValueError(f"Couldn't find parameter '{human_param}' ")


def print_notes() -> None:
    human_to_provantage_ram_filter: dict[str, str] = {
        "size": "3113035",
        "ddr_type": "31113713",
        "speed": "311971",
        "form_factor": "311506",
        "": ""
    }


def aLinkMCCopy(t: str, b: str) -> str:
    # function ALinkMC(t,b){var a='/service/searchsvcs/B-CRAMM?';if(b==2001)a+='MAN='+t;else a+='CAT='+t;window.location.href=a;}
    a = '/service/searchsvcs/B-CRAMM?'
    if b == '2001':
        a += 'MAN='
    else:
        a += 'CAT='
    a += t
    return a


def aLinkCopy() -> str:  # Used heavily, from what it seems
    # function ALink(t, b){var a = '/service/searchsvcs/B-CRAMM?A1=3113035&V1=8+GB';if (t == 'Various')t='Unclassified';t=t.replace( / ` / g, "'");t=t.replace( / ~ / g, '"');t=t.replace( / % / g, '%25');t=t.replace( / \+ / g, '%2B');a=a+'&A2='+b+'&V2='+t;a=a.replace( / / g, '+');window.location.href=a;}
    pass


def test_generate_link() -> None:
    test_cases = [[{
        "manufacturer": "Advantech-DLoG",
        "size": "32 GB"
    }, f'{BASE_URL}?MAN=ADVN&A1=3113035&V1=32+GB']]
    for test_params, expected in test_cases:
        result = generate_link(test_params)
        if result != expected:
            raise RuntimeError(f"function generate_link failed the test\nExpected {expected}\nGot {result}")
        print("Test was passed")
        print(f"{result = }")


if __name__ == '__main__':
    print_notes()
    # print(RAMManufacturer.fetch_all())
    test_generate_link()