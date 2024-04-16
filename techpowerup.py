from typing import Union

from bs4 import BeautifulSoup
from bs4.element import Tag

from class_database import db, Components, ErrorMessage
from component_classes.class_gpu import PCIe
from component_classes.class_ram import RAM
from custom_request import page_from_link


BASE_URL = 'https://www.techpowerup.com'
LINKS = {Components.CPU: BASE_URL + "/cpu-specs/", Components.GPU: BASE_URL + "/gpu-specs/"}


def parse_labels(website_link: str) -> list:
    def filter_labels():
        nonlocal labels
        for label in labels:
            if 'title' in label.attrs:
                label: Tag  # for typechecker
                if label['title'] == 'Close':
                    labels.pop(labels.index(label))

    labels = []
    main_page = page_from_link(website_link)
    for fieldset in main_page.find_all('fieldset'):
        if 'filters' in fieldset['class']:
            labels = fieldset.find_all_next('label')
            filter_labels()
            return labels
    return labels


def get_labels_with_values(component: Components) -> Union[ErrorMessage, dict[Components, list]]:
    if component not in LINKS.keys():
        error = ErrorMessage(f'updating {component} is not possible')
        return error

    result = {}
    for label in parse_labels(LINKS[component]):
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


def generate_link(component: Components, params: dict, sort_by: str = 'name') -> Union[ErrorMessage, str]:
    if params is not None:
        allowed_filters = db.get_single_filter(component)

        for filter_name, value in params.items():
            if filter_name not in allowed_filters.keys():
                error = ErrorMessage(f"There is no such filter as {filter_name}")
                return error
            elif value not in allowed_filters[filter_name]:
                error = ErrorMessage(f"There is no such option as {value} in filter {filter_name}")
                return error
        # up to here, the values are definitely correct

        query = "?"
        for _filter, value in params.items():
            query += f"{_filter}={value}&"
        query += f'sort={sort_by}'
    else:
        query = ""
    return f"{LINKS[component]}{query}"

def convert_table_to_list(table: Tag) -> list:
    headers_row = table.find('thead', {"class": ['colheader']}).find('tr')
    headers = []
    for header in headers_row.contents:
        if type(header) == Tag:
            header: Tag  # for typechecker
            if header.name == 'th':
                headers.append(header.text)

    result = []
    for row in table.find_all('tr')[2:]:
        count = 0
        tpu_component = {}
        link = row.find('a').attrs['href']
        tpu_component.update({"Link": BASE_URL + link})
        for element in row.contents:
            if type(element) != Tag:
                continue
            tpu_component.update({headers[count]: element.text.replace("\n", "").strip()})
            count += 1
        result.append(tpu_component)

    return result

def fetch_component_list(component: Components, params: dict = None, sort_by: str = 'name') -> \
        Union[ErrorMessage, dict[Components, list]]:
    if component not in LINKS.keys():
        error = ErrorMessage(f'Fetching {component} is not possible')
        return error
    if sort_by not in ['name', 'released', 'generation']:
        error = ErrorMessage(f"You can't sort by {sort_by}")
        return error

    link = generate_link(component=component, params=params, sort_by=sort_by)
    page = page_from_link(link)

    table = page.find('div', id="list").find('table')
    result = convert_table_to_list(table=table)
    # TODO: do some checking maybe? idk

    return {component: result}


def get_cpu_socket(cpu: dict) -> str:
    return cpu['Socket'][len('Socket '):]  # this is very error-prone
    # TODO: make a proper socket class or sth

def get_component_by_name(component: Components, name: str) -> list:
    link = f"{LINKS[component]}?ajaxsrch={name}"
    page = page_from_link(link)
    table = page.find('table')
    return convert_table_to_list(table=table)


def get_further_cpu_data(link: str) -> dict:
    def get_td_text_by_th(th_name: str) -> str:
        nonlocal page
        return page.find('th', string=th_name).parent.find('td').text.strip()

    deep_data = {'pcie': None, 'ram': None}

    page = page_from_link(link)

    further_pcie = PCIe('Gen 0.0 x0')
    pcie_string = get_td_text_by_th('PCI-Express:')
    pcie_list = pcie_string[0: pcie_string.find('(')].split(', ')
    further_pcie.lanes = int(pcie_list[-1].split()[0])
    further_pcie.generation = float(pcie_list[0].split()[-1])
    deep_data['pcie'] = further_pcie

    further_ram = RAM([])
    ddr_type = get_td_text_by_th('Memory Support:')
    further_ram.ddr_gen = int(ddr_type[-1])
    speed_mts = get_td_text_by_th('Rated Speed:')
    further_ram.speed_mhz = int(speed_mts.split()[0])
    deep_data['ram'] = further_ram

    return deep_data


def get_gpu_tdp(gpu_link: str) -> int:
    page = page_from_link(gpu_link, sleep_time=3)
    return int(page.find('dt', string='TDP').parent.find('dd').text.split()[0])


if __name__ == '__main__':
    # print(get_gpu_tdp('https://www.techpowerup.com/gpu-specs/radeon-rx-7600-xt.c4190'))
    # print(get_further_cpu_data('https://www.techpowerup.com/cpu-specs/ryzen-5-3600.c2132'))
    # for cpu in get_component_by_name(Components.CPU, 'Pentium'):
    #     print(cpu)
    pass
