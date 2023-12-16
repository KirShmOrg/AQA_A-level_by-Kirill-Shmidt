import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import json
from class_database import db

LINKS = {'CPU': "https://www.techpowerup.com/cpu-specs/", "GPU": "https://www.techpowerup.com/gpu-specs/"}


def parse_labels(website_link: str):
    def filter_labels():
        nonlocal labels
        for label in labels:
            if 'title' in label.attrs:
                if label['title'] == 'Close':
                    labels.pop(labels.index(label))

    labels = []
    main_page = BeautifulSoup(requests.get(website_link).content, features='html.parser')
    for fieldset in main_page.find_all('fieldset'):
        if 'filters' in fieldset['class']:
            labels = fieldset.find_all_next('label')
            filter_labels()
            return labels
    return labels


def get_labels_with_values(hardware_name: str):
    if hardware_name.upper() not in LINKS.keys():
        return {'error': f'updating {hardware_name} is not possible'}

    def remove_parenthesis(string: str):
        # TODO: figure our whether we need this at all
        start = string.find('(')
        end = string.find(')')
        if start != -1 and end != -1 and end > start:
            return string[0:start].strip()
        return string

    result = {}
    for label in parse_labels(LINKS[hardware_name]):
        siblings = []
        for sibling in label.next_siblings:
            if type(sibling) == Tag:
                siblings.append(sibling.contents)
        result.update({label['for']: siblings})
    for property_name, options_list in result.items():
        temp = []
        for option in options_list[0]:
            if type(option) == Tag:
                if option['value'] != "":
                    temp.append(option['value'])
        result.update({property_name: temp})
    return result


def get_component_list(component_name: str,
                       sort_by: str = 'name',
                       # mfgr: str = None,
                       # released: int = None,
                       # is_mobile: bool = None,
                       # is_server: bool = None,
                       # tdp: int = None,
                       # nCores: int = None,
                       # nThreads: int = None,
                       # generation: str = None,
                       # socket: str = None,
                       # codename: str = None,
                       # process_nm: int = None,
                       # is_multi_unlocked: bool = None,
                       # has_igp: bool = None,
                       params: dict = None
                       ):
    if component_name.upper() not in LINKS.keys():
        return {'error': f'updating {component_name} is not possible'}
    if sort_by not in ['name', 'released', 'generation']:
        return {'error': f"You can't sort by {sort_by}"}

    if params is not None:
        allowed_filters = db.get_filters(component_name)[0]

        for filter_name, value in params.items():
            if filter_name not in allowed_filters.keys():
                return {'error': f"There is no such filter as {filter_name}"}
            elif value not in allowed_filters[filter_name]:
                return {'error': f"There is no such option as {value} in filter {filter_name}"}
        # up to here, the values are definitely correct

        query = "?"
        for _filter, value in params.items():
            query += f"{_filter}={value}&"
        query += f'sort={sort_by}'
    else:
        query = ""
    response = requests.get(f"{LINKS[component_name]}{query}")
    page = BeautifulSoup(response.text, features='html.parser')

    table = page.find('div', id="list").find('table')
    headers_row = table.find('thead', {"class": ['colheader']}).find('tr')
    headers = []
    for header in headers_row.contents:
        if type(header) == Tag:
            if header.name == 'th':
                headers.append(header.text)

    result = []
    for row in table.find_all('tr'):
        cpu = {}
        count = 0
        for element in row.contents:
            if type(element) == Tag:
                cpu.update({headers[count]: element.text.replace("\n", "").strip()})
                count += 1
        result.append(cpu)

    return {component_name.upper(): result}


if __name__ == '__main__':
    # cpu_filters = get_labels_with_values('CPU')
    # with open("all_jsons/techpowerup_cpu_filters.json", 'w') as file:
    #     json.dump(cpu_filters, file, indent=4)
    #
    # gpu_filters = get_labels_with_values('GPU')
    # with open("all_jsons/techpowerup_gpu_filters.json", 'w') as file:
    #     json.dump(gpu_filters, file, indent=4)
    cpu_list = get_component_list('CPU', params={"mfgr": 'AMD',
                                                 "released": '2022',
                                                 "mobile": 'No',
                                                 "server": 'No',
                                                 "multiUnlocked": 'Yes'})
    if 'error' in cpu_list.keys():
        print(cpu_list['error'])
    else:
        cpu_list = cpu_list['CPU'][2:]
        print(f'\nParsed {len(cpu_list)} CPUs\n')
        for i in cpu_list:
            print(i)

    gpu_list = get_component_list('GPU', params={'mfgr': 'NVIDIA',
                                                 'released': '2023',
                                                 'mobile': 'No',
                                                 'workstation': 'No',
                                                 'performance': '1080'})
    if 'error' in gpu_list.keys():
        print(gpu_list['error'])
    else:
        gpu_list = gpu_list['GPU'][2:]
        print(f"\nParsed {len(gpu_list)} GPUs\n")
        for i in gpu_list:
            print(i)
