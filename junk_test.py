import json

with open("all_jsons/cpu_list.json", 'r') as file:
    cpu_list = json.load(file)['cpu_list']

html_text = [i['HTML text'] for i in cpu_list]
del cpu_list
# print(len(html_text))

result = []
headers = ['CPU name', 'Cores', 'CPU Mark', 'Thread Mark', 'TDP(W)', 'Socket', 'Category']
categories = ["Unknown", "Desktop", "Laptop", "Server", "Mobile/Embedded"]
for text in html_text:
    _temp = {"HTML text": text}
    _list = text.split()
    # extracting categories
    if "," in _list[-2] and _list[-2].replace(",", "") in categories:
        _temp.update({headers[-1]: " ".join(_list[-2:])})
        _list = _list[0:-2]
    elif _list[-1] in categories:
        _temp.update({headers[-1]: _list.pop(-1)})
    else:
        print(f"Unknown category in a list:\n{_list}")
    # up to here, the categories are extracted fully correctly
    # extracting socket

    result.append(_temp)

print(len(result))
