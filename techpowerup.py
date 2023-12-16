import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import json

LINKS = {'CPU': "https://www.techpowerup.com/cpu-specs/", "GPU": "https://www.techpowerup.com/gpu-specs/"}


def get_labels(website_link: str):
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
        start = string.find('(')
        end = string.find(')')
        if start != -1 and end != -1 and end > start:
            return string[0:start].strip()
        return string

    result = {}
    for label in get_labels(LINKS[hardware_name]):
        siblings = []
        for sibling in label.next_siblings:
            if type(sibling) == Tag:
                siblings.append(sibling.contents)
        result.update({label.text: siblings})
    for property_name, options_list in result.items():
        temp = []
        for option in options_list[0]:
            if type(option) == Tag:
                temp.append(remove_parenthesis(option.text))
        result.update({property_name: temp})
    return result


if __name__ == '__main__':
    cpu_filters = get_labels_with_values('CPU')
    with open("all_jsons/techpowerup_cpu_filters.json", 'w') as file:
        json.dump(cpu_filters, file, indent=4)

    gpu_filters = get_labels_with_values('GPU')
    with open("all_jsons/techpowerup_gpu_filters.json", 'w') as file:
        json.dump(gpu_filters, file, indent=4)
