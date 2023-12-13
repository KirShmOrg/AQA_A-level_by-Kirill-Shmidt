import requests
from bs4 import BeautifulSoup
import json

BASELINK = "https://www.techpowerup.com/cpu-specs/"


def get_labels():
    def filter_labels():
        nonlocal labels
        for label in labels:
            if 'title' in label.attrs:
                if label['title'] == 'Close':
                    labels.pop(labels.index(label))

    labels = []
    main_page = BeautifulSoup(requests.get(BASELINK).content)
    for fieldset in main_page.find_all('fieldset'):
        if 'filters' in fieldset['class']:
            labels = fieldset.find_all_next('label')
            filter_labels()
            return labels
    return labels


def save_label_with_values():
    result = {}
    for label in get_labels():
        siblings = []
        for sibling in label.next_siblings:
            siblings.append(sibling.text.strip().replace('\n', ''))
        result.update({label.text: siblings})
    with open('techpowerup_search.json', 'w') as search_file:
        json.dump(result, search_file, indent=4)


if __name__ == '__main__':
    save_label_with_values()
