import json
import time

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from class_database import db

BASE_URL = "https://motherboarddb.com/motherboards/"


def parse_filters():
    result = {}
    response = requests.get(f"{BASE_URL}")
    page = BeautifulSoup(response.text, features="html.parser")
    selects_list = page.find_all("select", {'class': ["select2-widget", "form-control"]})
    for select in selects_list:
        temp = {}
        for option in select.contents:
            if type(option) == Tag:
                temp.update({option.text.replace("\n", "").strip(): option['value']})
        result.update({select['name']: temp})
    # TODO: add slider filters (e.g. SATA3 Ports or Release Year)
    return result


def horse_around():
    response = requests.get(f"{BASE_URL}ajax/table/?dt=table&page=1")
    page = BeautifulSoup(response.text)
    print(page.prettify())


def parse_motherboards_list(params: dict):
    def get_number_of_pages():
        nonlocal page
        text = page.find('p').text
        return int(text.split()[-1])

    allowed_filters = db.get_filters('mb')[0]
    # TODO: allow the "value" variable to be a list
    for filter_name, value in params.items():
        if filter_name not in allowed_filters.keys():
            return {'error': f'There is no such filter as {filter_name}'}
        elif value not in allowed_filters[filter_name].keys():
            return {'error': f'There is no such option as {value} in {filter_name}'}

    query = "?"
    for filter_name, value in params.items():
        query += f'{filter_name}={allowed_filters[filter_name][value]}&'
    query += 'page=1'
    response = requests.get(f"{BASE_URL}ajax/table/{query}")
    page = BeautifulSoup(response.text, features="html.parser")

    result = {}
    for page_number in range(get_number_of_pages()):
        page = BeautifulSoup(requests.get(f"{BASE_URL}ajax/table/{query[0:-1]}{page_number}&dt=list").text,
                             features="html.parser")
        names = [tag.text for tag in page.find_all('h4')]
        count = 0
        for ul in page.find_all('ul', attrs={'class': ['list-unstyled']}):
            if count // 2 == 0:
                temp = []
            else:
                for element in ul.contents:
                    if type(element) == Tag:
                        temp.append(" ".join(element.text.strip().replace('\n', "").split()))
            result.update({names[count // 2]: temp})
            count += 1
        time.sleep(1)

    for mb_name, properties in result.items():
        specs = {}
        for _property in properties:
            column_index = _property.find(':')
            key = _property[0: column_index]
            value = _property[column_index + 1:]
            if value == '':
                specs.update({key: None})
            else:
                specs.update({key: value.strip()})
        result.update({mb_name: specs})

    final_result = []  # a bad, temporary solution
    # TODO: refactor the code to just do those lines in the main part
    for mb_name, specs in result.items():
        temp = {}
        temp.update({'Name': mb_name})
        temp.update(specs)
        final_result.append(temp)

    return final_result


def get_mb_socket(motherboard: dict) -> str:
    return motherboard['Socket(s)'][3:]  # this is because the actual socket value is like "1x SOCKET_NAME"


if __name__ == '__main__':
    mb_list = parse_motherboards_list(params={'manufacturer': 'Asus',
                                              # 'form_factor': 'Micro-ATX',
                                              'socket': 'AM4',
                                              # 'chipset': 'AMD B450',
                                              })
    if 'error' in mb_list.keys():
        print(mb_list['error'])
    else:
        print(f'{len(mb_list)} motherboards parsed')
        print(mb_list)
