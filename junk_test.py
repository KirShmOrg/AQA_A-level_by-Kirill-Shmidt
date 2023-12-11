import json


def extract_headers():
    with open("all_jsons/cpu_list.json", 'r') as file:
        cpu_list = json.load(file)['cpu_list']

    html_text = [i['HTML text'] for i in cpu_list]
    print(len(html_text), 'processors in database')
    del cpu_list

    result = []
    headers = ['CPU name', 'Cores', 'CPU Mark', 'Thread Mark', 'TDP(W)', 'Socket', 'Category']
    categories = ["Unknown", "Desktop", "Laptop", "Server", "Mobile/Embedded"]
    for text in html_text:
        cpu = {"HTML text": text}
        row_list = text.split()
        # extracting categories
        if "," in row_list[-2] and row_list[-2].replace(",", "") in categories:
            cpu.update({headers[-1]: " ".join(row_list[-2:])})
            row_list = row_list[0:-2]
        elif row_list[-1] in categories:
            cpu.update({headers[-1]: row_list.pop(-1)})
        else:
            print(f"Unknown category in a list:\n{row_list}")
        # up to here, the categories are extracted fully correctly
        # extracting socket(s). unfortunately, sockets are as ass as it can get.
        # it could be "AM4" or "BGA769 (FT3)" or "AM2, AM3" or just "939")
        # my bet is that it's never two just pure integers in a row, so I assume that the next integer is already TDP
        socket = row_list.pop(-1)
        socket_finished = False
        while not socket_finished:
            maybe_tdp = row_list.pop(-1)
            try:
                if maybe_tdp == "NA" or float(maybe_tdp):  # funny enough, TDP can be a flot value (e.g. 4.5)
                    socket_finished = True
                    cpu.update({headers[-2]: socket})
                    cpu.update({headers[-3]: maybe_tdp})
            except ValueError:
                socket = f'{maybe_tdp} {socket}'
        # up to here, sockets and TDP seems to be extracted properly
        # next is thread mark. It is either "NA", int (e.g. "556"), or int with comma (e.g. "1,567")
        thread_mark = row_list.pop(-1).replace(",", "")
        if thread_mark != "NA":
            try:
                thread_mark = int(thread_mark)
            except ValueError:
                print(f"Found non-integer and non-NA Thread Mark in cpu:\n{cpu}")
        cpu.update({headers[-4]: thread_mark})
        # now to CPU mark. the syntax and the logic is the exact same
        cpu_mark = row_list.pop(-1).replace(",", "")
        if cpu_mark != "NA":
            try:
                cpu_mark = int(cpu_mark)
            except ValueError:
                print(f"Found non-integer and non-NA CPU Mark in cpu:\n{cpu}")
        cpu.update({headers[-5]: cpu_mark})

        cpu.update({"the rest": row_list})
        result.append(cpu)

    print(len(result), "results fetched")
    return result


if __name__ == '__main__':
    cpu_list = extract_headers()
    for cpu in cpu_list:
        print(f"{cpu['Cores']}")


