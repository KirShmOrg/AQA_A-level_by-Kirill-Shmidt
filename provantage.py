from bs4 import BeautifulSoup
from bs4.element import Tag
from dataclasses import dataclass, field
from enum import Enum
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

from custom_request import request_get_v2
from class_database import db
from component_classes.class_ram import RAM
from component_classes.class_psu import PSU


class Component(Enum):
    RAM = 'RAM'
    PSU = 'PSU'


BASE_URL = "https://www.provantage.com/service/searchsvcs"
LINKS = {Component.RAM: BASE_URL + '/B-CRAMM', Component.PSU: BASE_URL + '/B-PPSUP'}
PRODUCT_TYPES = {Component.RAM: 'RAM Module', Component.PSU: "Power Supply"}


@dataclass
class Manufacturer:
    component: Component
    human_name: str = field(default='')

    js_name: str = field(init=False, default='')

    def __post_init__(self):
        if self.human_name not in [None, '']:
            self.js_name = db.get_all_provantage_manufacturers()[self.component.value][self.human_name]

    def _fetch_all(self) -> dict:
        driver = Chrome()
        driver.get(LINKS[self.component])

        manufs_div = driver.find_element(by=By.ID, value="AT2001")
        result_dictionary = {}
        for manuf_a in manufs_div.find_elements(by=By.CSS_SELECTOR, value='a'):
            href = manuf_a.get_property('href')
            js_name = href[href.find('(') + 2:href.find(',') - 1]
            manufacturer_name = manuf_a.find_element(by=By.CLASS_NAME, value="choice").text
            manufacturer_name = manufacturer_name[0: manufacturer_name.index("(") - 1]
            result_dictionary.update({manufacturer_name: js_name})

        return result_dictionary


def get_all_manufacturers() -> dict[str, str]:
    all_ram_manufs = Manufacturer(Component.RAM)._fetch_all()
    all_psu_manufs = Manufacturer(Component.PSU)._fetch_all()
    for_update = {Component.RAM.value: all_ram_manufs, Component.PSU.value: all_psu_manufs}
    return for_update


def human_param_to_provantage_code(human_param: str, component: Component) -> str:
    checkup_table = {
        Component.RAM: {
            "Product Type | Category": "31100",
            "Size | Capacity": "3113035",
            "Technology | DDR_type": "31113713",
            "Speed": "311971",
            "Form Factor": "311506"
        },
        Component.PSU: {
            "Product Type | Category": "31100",
            "Wattage | Output Power": "31574",
            "Form Factor": "311506",
            "Efficiency": "31274",
            "Product Family": "377776919",
            "Country Of Origin": "35555883",
            "Is Modular": "377776945"
            # 'Warranty' might be added
        }
    }

    for name, code in checkup_table[component].items():
        if human_param.lower() in name.lower():
            return code


def generate_link(component: Component, parameters: dict[str, str]) -> str:
    link = LINKS[component] + '?'
    parameters['Product Type'] = PRODUCT_TYPES[component]
    if 'manufacturer' in parameters.keys():
        manuf = Manufacturer(component, parameters.pop('manufacturer'))
        link += f"MAN={manuf.js_name}"

    counter = 1
    for key, value in parameters.items():
        provantage_code = human_param_to_provantage_code(key, component)
        html_param_value = value.replace(' ', '+')
        link += f"&A{counter}={provantage_code}&V{counter}={html_param_value}"
        counter += 1
    return link


def get_component_list(component: Component, params: dict, as_objects: bool = True) -> list:
    link = generate_link(parameters=params, component=component)
    response = request_get_v2(link)
    page = BeautifulSoup(response.text, features='html.parser')
    main_div = page.find(id='MAIN').find_all('table', attrs={'class': 'BOX2'})[2].next.next.next.next

    result_list = []
    for text_div in main_div.find_all('div', attrs={'class': 'BOX5B'}):
        product_a: Tag = text_div.find('a', attrs={'class': 'BOX5PRODUCT'})
        human_name = product_a.parent.text
        further_link: str = product_a.attrs['href']
        temp_text = f"{text_div.text} - Name: {human_name} - Link: {further_link}"  # TODO: also add manufacturer's name
        temp_list = temp_text.split(' - ')
        result_list.append(temp_list)

    if as_objects is False:
        return result_list

    if component == Component.RAM:
        return [RAM(ram_) for ram_ in result_list]
    elif component == Component.PSU:
        return [PSU(psu_) for psu_ in result_list]
    else:
        raise ZeroDivisionError(f"This should not have happened: The component is unknown. Expected: {list(Component)}")


if __name__ == '__main__':
    test_cases = {
        Component.RAM: {
            'manufacturer': 'AddOn',
            'size': '16 GB',
            'speed': '2666 MHz',
            'DDR_type': 'DDR 4'
        },
        Component.PSU: {
            'manufacturer': "EVGA",
            'modular': 'yes',
            'power': '650 W'
        }
    }
    for ram in get_component_list(component=Component.RAM, params=test_cases[Component.RAM]):
        print(ram)
    for psu in get_component_list(component=Component.PSU, params=test_cases[Component.PSU]):
        print(psu)
