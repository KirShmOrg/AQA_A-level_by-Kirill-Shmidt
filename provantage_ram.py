from bs4.element import Tag
import json

from custom_request import request_get_v2


# The general logic of filters: An: key n, Vn: value n (e.g. A1 V1)

BASE_URL = 'https://www.provantage.com/service/searchsvcs/B-CRAMM'


class RAMManufacturer:
    FILEPATH = "all_jsons/provantage_manufacturers.json"

    def __init__(self, human_name: str = None, js_name: str = None, init_dict: dict[str, str] = None):
        self.__human_name = human_name
        self.__js_name = js_name
        if human_name is not None and js_name is not None:
            if init_dict is not None:
                print(f"Since both the keywords and the dictionary was passed into __init__ of {self.__class__}, "
                      f"only keywords will be used")
            return

        if len(init_dict) > 1:
            raise ValueError("Variable 'init_dict' should be only 1 key and 1 value")
        self.__human_name, self.__js_name = init_dict

    @property
    def human_name(self) -> str:
        return self.__human_name

    @property
    def js_name(self) -> str:
        return self.__js_name

    @staticmethod
    def fetch_all_as_dictionary(with_update: bool = False) -> dict[str, str]:
        if not isinstance(with_update, bool):
            raise TypeError(f"Variable 'with update' should be type bool, not {type(with_update)}")

        from selenium.webdriver import Chrome
        from selenium.webdriver.common.by import By

        driver = Chrome()
        driver.get(BASE_URL)
        manufs_div = driver.find_element(by=By.ID, value="AT2001")

        result_dictionary = {}
        for manuf_a in manufs_div.find_elements(by=By.CSS_SELECTOR, value='a'):
            href = manuf_a.get_property('href')
            js_name = href[href.find('(') + 2:href.find(',') - 1]
            manufacturer_name = manuf_a.find_element(by=By.CLASS_NAME, value="choice").text
            manufacturer_name = manufacturer_name[0: manufacturer_name.index("(") - 1]
            result_dictionary.update({manufacturer_name: js_name})

        if with_update is True:
            filepath = RAMManufacturer.FILEPATH
            with open(filepath, 'w') as file:
                json.dump(result_dictionary, file, indent=4)
                file.truncate()
                print(f"Updated '{filepath}'")

        return result_dictionary

    @staticmethod
    def fetch_all_as_objects(with_update: bool = False) -> list:
        objects_list = []
        all_manufacturers: dict[str, str] = RAMManufacturer.fetch_all_as_dictionary(with_update=with_update)
        for human_name, js_name in all_manufacturers.items():
            objects_list.append(RAMManufacturer(human_name=human_name, js_name=js_name))
        return objects_list

    def __cmp__(self, other) -> bool:
        if not isinstance(other, RAMManufacturer):
            raise TypeError("You can only compare within the RAMManufacturer class")
        return self.js_name == other.js_name or self.human_name == other.human_name

    def __repr__(self) -> str:
        return f"RAMManufacturer <{self.__human_name}> access by <{self.js_name}>"


def generate_link(parameters: dict[str, str]) -> str:
    import os

    current_dir = os.path.dirname(__file__)
    manufacturers_filename = os.path.join(current_dir, 'all_jsons/provantage_manufacturers.json')

    link = BASE_URL + "?"
    initial_parameters = {"category": "RAM Module"}

    if "manufacturer" in parameters.keys():
        manuf_to_find = parameters.pop('manufacturer')
        with open(manufacturers_filename, 'r') as file:
            manufacturers = json.load(file)

        if manuf_to_find not in manufacturers:
            raise ValueError(f"""The manufacturer '{manuf_to_find}' was not found on the website""")

        link += f"MAN={manufacturers[manuf_to_find]}"

    counter = 1
    parameters.update(initial_parameters)
    for key, value in parameters.items():
        provantage_code = human_param_to_provantage_code(key)
        html_param_value = value.replace(' ', '+')
        link += f"&A{counter}={provantage_code}&V{counter}={html_param_value}"
        counter += 1

    return link


def human_param_to_provantage_code(human_param: str) -> str:
    # NOTE: !!MAKE SURE that the words within the keys are not substrings of other keys!!
    checkup_table = {
        "Product Type | Category": "31100",
        "Size | Capacity": "3113035",
        "Technology | DDR_type": "31113713",
        "Speed": "311971",
        "Form Factor": "311506"
    }

    for name, code in checkup_table.items():
        if human_param.lower() in name.lower():
            return code
    raise ValueError(f"Couldn't find parameter '{human_param}' ")


def get_ram_list(params: dict, as_objects: bool = False) -> list:
    link = generate_link(params)
    response = request_get_v2(link)
    if response.status_code != 200:
        raise ConnectionError(f"The status is incorrect: {response.status_code}")

    from bs4 import BeautifulSoup

    page = BeautifulSoup(response.text, features='html.parser')
    main_div = page.find(id='MAIN').find_all('table', attrs={'class': 'BOX2'})[2].next.next.next.next

    result_ram_list = []
    for text_div in main_div.find_all('div', attrs={'class': 'BOX5B'}):
        product_a: Tag = text_div.find('a', attrs={'class': 'BOX5PRODUCT'})
        human_name = product_a.parent.text
        further_link: str = product_a.attrs['href']
        temp_text = f"{text_div.text} - Name: {human_name} - Link: {further_link}"
        temp_list = temp_text[temp_text.find('RAM Modules')::].split(' - ')
        result_ram_list.append(temp_list)

    if as_objects is True:
        from component_classes.class_ram import RAM

        return [RAM(ram) for ram in result_ram_list]

    return result_ram_list


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


if __name__ == '__main__':
    # print(RAMManufacturer.fetch_all_as_dictionary())
    test_params = {
        'manufacturer': 'AddOn',
        'size': '16 GB',
        'speed': '2666 MHz',
        'DDR_type': 'DDR 4'
    }
    ram_list = get_ram_list(test_params, as_objects=True)
    print(f"Got {len(ram_list)} RAMs")
    for ram in ram_list:
        print(ram)
