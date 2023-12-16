import json
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
BASE_URL = "https://motherboarddb.com/motherboards/"


def get_filters():
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


if __name__ == '__main__':
    filters = get_filters()
    with open('all_jsons/motherboarddb_mb_filters.json', 'w') as file:
        json.dump(filters, file, indent=4)
