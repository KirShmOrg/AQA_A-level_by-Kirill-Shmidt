import json
from typing import Union
from bs4.element import Tag
from dataclasses import dataclass, field
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from custom_request import page_from_link, BeautifulSoup
from class_database import db, ErrorMessage
from component_classes.class_ram import RAM
from component_classes.class_psu import PSU
from class_database import Components

from time import sleep


BASE_URL = "https://www.provantage.com/service/searchsvcs"
LINKS = {Components.RAM: BASE_URL + '/B-CRAMM', Components.PSU: BASE_URL + '/B-PPSUP'}
PRODUCT_TYPES = {Components.RAM: 'RAM Module', Components.PSU: "Power Supply"}


# returns dict[str, str] if it's manufacturer, and list if it's any other filter
def parse_filters(component: Components) -> dict[str, Union[list, dict[str, str]]]:
    result = {}

    def elements_id_starts_with(element: str, id_starts: str) -> list[WebElement]:
        return driver.find_elements(by=By.XPATH, value=f"//{element}[@class='sel'][starts-with(@id,'{id_starts}')]")

    def remove_amount_of_results(text: str) -> str:
        if '(' in text and ')' not in text:
            return text
        return text[0: text.rfind('(')].strip()

    driver = Chrome()
    # driver.maximize_window()
    driver.get(LINKS[component])
    driver.implicitly_wait(5)

    more_features_table = driver.find_element(by=By.ID, value='OPENALL2')  # it's a <table> element
    more_features_table.click()
    all_headers = elements_id_starts_with(element='table', id_starts='OP')
    sleep(1)

    body = driver.find_element(by=By.CSS_SELECTOR, value='body')
    body.send_keys(Keys.PAGE_UP)
    for _ in range(3):
        body.send_keys(Keys.ARROW_DOWN)
    sleep(1)
    # up to here, all the options should be opened and the page is scrolled to almost the top

    for header in all_headers:
        try:
            header.click()
            sleep(0.1)
        except:  # TODO: debug the exception handling. It all took too much time, and just ignoring the error works okay
            pass
    # after clicking, the id changes from OP (press to OPen) to CL (press to CLose)
    all_headers = elements_id_starts_with(element='table', id_starts='CL')
    all_headers = [remove_amount_of_results(header.text) for header in all_headers]

    all_values = elements_id_starts_with(element='div', id_starts='AT')
    # we fetch manufacturers first, since they have a different logic
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
    driver.close()

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
            "Memory Size | Capacity": "3113035",
            "Memory Technology | DDR Type": "31113713",
            "Memory Speed": "311971",
            "Form Factor": "311506"
        },
        Components.PSU: {
            "Product Type | Category": "31100",
            "Output Power | Wattage": "31574",
            "Form Factor": "311506",
            # "Efficiency": "31274",
            "Product Family": "377776919",
            "Country Of Origin": "35555883",
            # "Is Modular": "377776945"
            # 'Warranty' might be added
        }
    }

    for name, code in checkup_table[component].items():
        if human_param.lower() in name.lower():
            return code


def parameters_are_valid(component: Components, params: dict[str, str]) -> Union[ErrorMessage, None]:
    correct_params = db.get_single_filter(component)
    lowercase_correct_params = {}
    for key, value in correct_params.items():
        lowercase_correct_params.update({key.lower(): value})

    for filter_name, option in params.items():
        if filter_name.lower() not in lowercase_correct_params.keys():
            error = ErrorMessage(f"There is no such filters as {filter_name}")
            return error
        elif option not in lowercase_correct_params[filter_name.lower()]:
            error = ErrorMessage(f"There is no such option as {option} in {filter_name}")
            return error
    return None


def generate_link(component: Components, parameters: dict[str, str]) -> Union[str, ErrorMessage]:
    is_correct = parameters_are_valid(component, parameters)
    if isinstance(is_correct, ErrorMessage):
        return is_correct
    if is_correct is not None:
        raise ValueError(f"The result of {parameters_are_valid.__name__} should be either {ErrorMessage} or None\n"
                         f"{is_correct} is received instead")
    # at this point, the parameters should be correct
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


def parse_page(page: BeautifulSoup) -> list[list[str]]:
    main_div = page.find(id='MAIN').find_all('table', attrs={'class': 'BOX2'})[2].next.next.next.next
    result_list = []

    for text_div in main_div.find_all('div', attrs={'class': 'BOX5B'}):
        product_a: Tag = text_div.find('a', attrs={'class': 'BOX5PRODUCT'})
        human_name = product_a.parent.text
        further_link: str = product_a.attrs['href']
        temp_text = f"{text_div.text} - Name: {human_name} - Link: {further_link}"  # TODO: also add manufacturer's name
        temp_list = temp_text.split(' - ')
        result_list.append(temp_list)

    return result_list


def get_component_by_name(component: Components, search_str: str, as_objects: bool = True) -> Union[list, ErrorMessage]:
    link = LINKS[component] + f"?QUERY={search_str}"
    page = page_from_link(link)
    result_list = parse_page(page)

    if as_objects is False:
        return result_list

    if component == Components.RAM:
        return [RAM(ram_) for ram_ in result_list]
    elif component == Components.PSU:
        return [PSU(psu_) for psu_ in result_list]
    else:
        return ErrorMessage(f"{component} is not supported by provantage")


def get_component_list(component: Components, params: dict, as_objects: bool = True) -> list:
    link = generate_link(parameters=params, component=component)
    if isinstance(link, ErrorMessage):
        print(link.message)
        return []
    page = page_from_link(link)
    result_list = parse_page(page)

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
            'memory size': '16 GB',
            'memory speed': '2666 MHz',
            'memory technology': 'DDR4 SDRAM'
        },
        Components.PSU: {
            'manufacturer': "EVGA",
            # 'modular': 'yes',
            'output power': '650 W'
        }
    }
    print(generate_link(Components.RAM, test_cases[Components.RAM]))
    for ram in get_component_list(component=Components.RAM, params=test_cases[Components.RAM]):
        print(ram)
    print(generate_link(Components.PSU, test_cases[Components.PSU]))
    for psu in get_component_list(component=Components.PSU, params=test_cases[Components.PSU]):
        print(psu)
