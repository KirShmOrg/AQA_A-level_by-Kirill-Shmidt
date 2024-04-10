import time

from bs4 import BeautifulSoup
from bs4.element import Tag
from class_database import db

from custom_request import request_get_v2

BASE_URL = "https://motherboarddb.com/motherboards"


def parse_filters() -> dict:
    result = {}
    response = request_get_v2(f"{BASE_URL}")
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


def parse_motherboards_list(params: dict) -> list[dict[str, str]]:
    def get_number_of_pages() -> int:
        nonlocal page
        pagination_options: list[Tag] = page.find('ul', {'class': 'pagination'}).find_all('li', {'class': 'page-item'})
        max_page = 1
        for li in pagination_options:
            if int(li.text) > max_page:  # this could have been done in a very nice max(map(lambda ...)),
                # but the issue is that when we have 1 page, there is no "Next", unlike with 2+ pages
                max_page = int(li.text)
        return max_page

    # filters_time_start = time.perf_counter()
    allowed_filters = db.get_filters('mb')[0]
    # TODO: allow the "value" variable to be a list
    for filter_name, value in params.items():
        if filter_name not in allowed_filters.keys():
            return {'error': f'There is no such filter as {filter_name}'}
        elif value not in allowed_filters[filter_name].keys():
            return {'error': f'There is no such option as {value} in {filter_name}'}

    # print(f"Parsing filters: {time.perf_counter() - filters_time_start}")

    # request_time_start = time.perf_counter()
    query = "?"
    for filter_name, value in params.items():
        query += f'{filter_name}={allowed_filters[filter_name][value]}&'
    query += 'page=1'
    response = request_get_v2(f"{BASE_URL}/ajax/table/{query}&dt=list")
    page = BeautifulSoup(response.text, features="html.parser")
    # print(f"Receiving a page: {time.perf_counter() - request_time_start}")

    # parsing_time_start = time.perf_counter()
    result = {}
    for page_number in range(1, get_number_of_pages() + 1):
        if page_number > 1:
            page = BeautifulSoup(request_get_v2(f"{BASE_URL}/ajax/table/{query[0:-1]}{page_number}&dt=list").text,
                                 features="html.parser")
        names = [tag.text for tag in page.find_all('h4')]
        links = [tag.parent.attrs['href'] for tag in page.find_all('h4')]
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
    # print(f"Parsing the page: {time.perf_counter() - parsing_time_start}")

    # data_refactoring_time_start = time.perf_counter()
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
        specs.update({'Link': "https://motherboarddb.com" + links[names.index(mb_name)]})
        result.update({mb_name: specs})

    final_result = []  # a bad, temporary solution
    # TODO: refactor the code to just do those lines in the main part
    for mb_name, specs in result.items():
        temp = {}
        temp.update({'Name': mb_name})
        temp.update(specs)
        final_result.append(temp)
    # print(f"Data refactoring: {time.perf_counter() - data_refactoring_time_start}")
    return final_result


def get_mb_socket(motherboard: dict) -> str:
    return motherboard['Socket(s)'][3:]  # this is because the actual socket value is like "1x SOCKET_NAME"


def get_further_information(link: str) -> dict:
    def parse_expansions(card: Tag) -> list[str]:
        return [li.text.strip() for li in card.find('ul') if li.text != '\n']

    page = BeautifulSoup(request_get_v2(link).text, features='html.parser')
    cards_dict = {}
    headers_whitelist = [text.lower() for text in ['General Information', 'Expansion Slots', 'Memory']]
    # we might want to add M.2 Slots
    for card in page.find_all('div', {'class': 'card'}):
        card_header = card.find('div', {'class': 'card-header'}).text.lower()
        if card_header not in headers_whitelist:
            continue
        if card_header == 'Expansion Slots'.lower():
            cards_dict.update({card_header: parse_expansions(card)})
            continue
        temp = {}
        for tr in card.find_all('tr'):
            temp.update({tr.find('th').text.strip(): tr.find('td').text.strip().replace('\n', ' ')})
        cards_dict.update({card_header: temp})

    return cards_dict


if __name__ == '__main__':
    # mb_list = parse_motherboards_list(params={'manufacturer': 'Asus',
    #                                           'form_factor': 'Micro-ATX',
    #                                           'socket': 'AM4',
    #                                           'chipset': 'AMD B450',
    #                                           })
    # print(f'{len(mb_list)} motherboards parsed')
    # for mb in mb_list:
    #     print(mb)
    info = get_further_information('https://motherboarddb.com/motherboards/1463/ROG%20Strix%20B450-F%20Gaming/')
    for key, value in info.items():
        print(key, value, '--'*15, sep='\n')
