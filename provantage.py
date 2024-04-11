from bs4.element import Tag
from dataclasses import dataclass, field
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from custom_request import page_from_link
from class_database import db
from component_classes.class_ram import RAM
from component_classes.class_psu import PSU
from class_database import Components

BASE_URL = "https://www.provantage.com/service/searchsvcs"
LINKS = {Components.RAM: BASE_URL + '/B-CRAMM', Components.PSU: BASE_URL + '/B-PPSUP'}
PRODUCT_TYPES = {Components.RAM: 'RAM Module', Components.PSU: "Power Supply"}


def parse_filters(component: Components) -> dict[str]:
    result = {}

    def elements_id_starts_with(element: str, id_starts: str) -> list[WebElement]:
        nonlocal main_div
        return main_div.find_elements(by=By.XPATH, value=f"{element}[@class='sel'][starts-with(@id,'{id_starts}')]")

    def remove_amount_of_results(text: str) -> str:
        if '(' in text and ')' not in text:
            return text
        return text[0: text.find('(')].strip()

    driver = Chrome()
    driver.get(LINKS[component])

    main_div = driver.find_element(by=By.ID, value='ATTRIB1')
    all_headers = elements_id_starts_with(element='table', id_starts='OP')
    for header in all_headers:
        header.click()
    all_headers = elements_id_starts_with(element='table', id_starts='CL')
    all_headers = [remove_amount_of_results(header.text) for header in all_headers]

    all_values = elements_id_starts_with(element='div', id_starts='AT')
    manuf_dict = {}
    for manuf_a in all_values[0].find_elements(by=By.CSS_SELECTOR, value='a'):
        href = manuf_a.get_property('href')
        js_name = href[href.find('(') + 2:href.find(',') - 1]
        manufacturer_name = manuf_a.find_element(by=By.CLASS_NAME, value="choice").text
        manufacturer_name = manufacturer_name[0: manufacturer_name.index("(") - 1]
        manuf_dict.update({manufacturer_name: js_name})
    result.update({all_headers[0]: manuf_dict})

    all_values = [[remove_amount_of_results(div.text) for div in value.find_elements(by=By.CSS_SELECTOR, value='div')]
                  for value in all_values]
    for i in range(1, min([len(all_headers), len(all_values)])):  # I purposefully ignore manufacturers
        result.update({all_headers[i]: all_values[i]})

    return result


@dataclass
class Manufacturer:
    component: Components
    human_name: str = field(default='')

    js_name: str = field(init=False, default='')

    def __post_init__(self):
        if self.human_name not in [None, '']:
            self.js_name = db.get_single_filter(self.component)['Manufacturer'][self.human_name]


def human_param_to_provantage_code(human_param: str, component: Components) -> str:
    checkup_table = {
        Components.RAM: {
            "Product Type | Category": "31100",
            "Size | Capacity": "3113035",
            "Technology | DDR Type": "31113713",
            "Speed": "311971",
            "Form Factor": "311506"
        },
        Components.PSU: {
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


def generate_link(component: Components, parameters: dict[str, str]) -> str:
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


def get_component_list(component: Components, params: dict, as_objects: bool = True) -> list:
    link = generate_link(parameters=params, component=component)
    page = page_from_link(link)
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

    if component == Components.RAM:
        return [RAM(ram_) for ram_ in result_list]
    elif component == Components.PSU:
        return [PSU(psu_) for psu_ in result_list]
    else:
        raise ValueError(f"{component} is not supported by provantage.py")


if __name__ == '__main__':
    test_cases = {
        Components.RAM: {
            'manufacturer': 'AddOn',
            'size': '16 GB',
            'speed': '2666 MHz',
            'DDR_type': 'DDR 4'
        },
        Components.PSU: {
            'manufacturer': "EVGA",
            'modular': 'yes',
            'power': '650 W'
        }
    }
    for ram in get_component_list(component=Components.RAM, params=test_cases[Components.RAM]):
        print(ram)
    for psu in get_component_list(component=Components.PSU, params=test_cases[Components.PSU]):
        print(psu)
