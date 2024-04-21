from typing import Union, TypedDict
import time

from bs4.element import Tag
from class_database import db, Components, ErrorMessage
from custom_request import page_from_link, BeautifulSoup


BASE_URL = "https://motherboarddb.com/motherboards"


class LinkAndQueryDict(TypedDict):
    link: str
    query: str


def parse_filters() -> dict:
    result = {}
    page = page_from_link(BASE_URL)
    selects_list = page.find_all("select", {'class': ["select2-widget", "form-control"]})
    for select in selects_list:
        temp = {}
        for option in select.contents:
            if type(option) == Tag:
                temp.update({option.text.replace("\n", "").strip(): option['value']})
        result.update({select['name']: temp})
    # TODO: add slider filters (e.g. SATA3 Ports or Release Year)
    return result


def generate_link_and_query(params: dict) -> Union[LinkAndQueryDict, ErrorMessage]:
    # filters_time_start = time.perf_counter()
    allowed_filters = db.get_single_filter(Components.MB)
    # TODO: make 'search' a CONSTANT in the `class_database.py`
    if 'search' in params.keys() and isinstance(params['search'], str):
        allowed_filters.update({'search': params['search']})  # I allow this specific search (funny solution)
    # TODO: allow the "value" variable to be a list
    for filter_name_, value_ in params.items():
        if filter_name_ == 'search':
            continue
        if filter_name_ not in allowed_filters.keys():
            return ErrorMessage(f'There is no such filter as {filter_name_}')
        elif value_ not in allowed_filters[filter_name_].keys():
            return ErrorMessage(f'There is no such option as {value_} in {filter_name_}')
    # print(f"Parsing filters: {time.perf_counter() - filters_time_start}")

    query = "?"
    for filter_name_, value_ in params.items():
        if filter_name_ == 'search':
            query += f'{filter_name_}={value_}&'
            continue
        query += f'{filter_name_}={allowed_filters[filter_name_][value_]}&'
    query += 'page=1'
    return {"link": f"{BASE_URL}/ajax/table/{query}&dt=list", 'query': query}


def parse_mb_page(page: BeautifulSoup, query: str) -> dict:
    def get_number_of_pages() -> int:
        nonlocal page
        pagination_options: list[Tag] = page.find('ul', {'class': 'pagination'}).find_all('li', {'class': 'page-item'})
        max_page = 1
        for li in pagination_options:
            if int(li.text) > max_page:  # this could have been done in a very nice max(map(lambda ...)),
                # but the issue is that when we have 1 page, there is no "Next", unlike with 2+ pages
                max_page = int(li.text)
        return max_page

    # parsing_time_start = time.perf_counter()
    result = {}
    for page_number in range(1, get_number_of_pages() + 1):
        if page_number > 1:  # it's very bold to assume that pages only go to a single digit lol (next line, query)
            page = page_from_link(f"{BASE_URL}/ajax/table/{query[0:-1]}{page_number}&dt=list")
        names = [tag.text for tag in page.find_all('h4')]
        links = [tag.parent.attrs['href'] for tag in page.find_all('h4')]
        count = 0
        temp = []
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
        # noinspection PyUnboundLocalVariable
        specs.update({'Link': "https://motherboarddb.com" + links[names.index(mb_name)]})
        result.update({mb_name: specs})
    # print(f"Parsing the page: {time.perf_counter() - parsing_time_start}")

    return result


def get_motherboards_list(params: dict) -> Union[dict, list[dict[str, str]]]:
    temp_dict = generate_link_and_query(params)
    link, query = temp_dict['link'], temp_dict['query']
    # request_time_start = time.perf_counter()
    page = page_from_link(link)
    # print(f"Receiving a page: {time.perf_counter() - request_time_start}")
    result = parse_mb_page(page, query)

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
    def parse_expansions(card_: Tag) -> list[str]:
        return [li.text.strip() for li in card_.find('ul') if li.text != '\n']

    page = page_from_link(link)
    cards_dict = {}
    headers_whitelist = [text.lower() for text in ['General Information', 'Expansion Slots', 'Memory']]
    # I might want to add M.2 Slots
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
    test_params = {
        'search': 'B450M',
        'manufacturer': 'Asus'
    }
    temp = generate_link_and_query(test_params)
    if isinstance(temp, ErrorMessage):
        print(temp.message)
        exit()

    print(temp['link'])
    mb_list = get_motherboards_list(test_params)
    print(f'{len(mb_list)} motherboards parsed')
    for mb in mb_list:
        print(mb)
    info = get_further_information(mb_list[0]['Link'])
    for key, value in info.items():
        print(key, value, '--' * 15, sep='\n')
