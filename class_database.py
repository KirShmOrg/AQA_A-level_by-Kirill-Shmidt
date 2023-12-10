import json
from time import sleep, time


class Database:
    def __init__(self,
                 cpus_link="https://www.cpubenchmark.net/CPU_mega_page.html",
                 gpus_link="https://www.videocardbenchmark.net/GPU_mega_page.html"):
        self._all_cpus_link = cpus_link
        self._all_gpus_link = gpus_link
        self._cpu_list = []
        self._gpu_list = []
        self._cpu_list_location = "all_jsons/cpu_list.json"
        self._gpu_list_location = "all_jsons/gpu_list.json"

    def update_cpu_list(self, method: str):
        def with_selenium():
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.select import Select
            driver = webdriver.Chrome()
            driver.get(self._all_cpus_link)
            sleep(3)
            select = Select(driver.find_element(by=By.NAME, value="cputable_length"))
            select.select_by_value("-1")
            table = driver.find_element(by=By.ID, value="cputable")

            # headers = [i.text for i in table.find_element(by=By.CSS_SELECTOR, value='thead').find_elements(by=By.CSS_SELECTOR, value='th')]

            headers = ['CPU name', 'Cores', 'CPU Mark', 'Thread Mark', 'TDP(W)', 'Socket', 'Category']

            tbody = table.find_element(by=By.CSS_SELECTOR, value='tbody')

            start_time = time()
            trs = tbody.find_elements(by=By.CSS_SELECTOR, value='tr')
            end_time = time()
            print(f'Found all table rows in {end_time - start_time}')

            start_time = time()
            for row in trs:
                text = row.text
                temp = {"HTML text": text}

                at_index = text.find('@')
                if at_index != -1:
                    temp.update({headers[0]: text[0:at_index].rstrip()})  # updates the name
                    text = text[at_index+1:].lstrip()  # removes text up to @ symbol
                    # proceeds to add properties in orders of headers
                    # can cause errors if more than one category is present and written separated by comma (,)
                    _list = text.split()

                    freq = _list.pop(0).replace("+", "")  # this could be either "2.20", "2.20+" or "2.20GHz"
                    try:
                        freq = float(freq)
                        freq = str(freq) + _list.pop(0)
                    except ValueError as vr:
                        if "could not convert string to float:" in vr.__str__():
                            temp.update({"Frequency": freq})
                        else:
                            print(f"Found a ValueError which is not due to float conversion:\n{vr}")

                    for header in headers[1:]:
                        temp.update({header: _list.pop(0)})
                else:
                    # here we start from the end and go to the beginning, because we don't know how long the name is
                    _list = text.split()
                    temp.update({"original_list": _list.copy()})
                    # There could be 1 or 2 categories. In the latter case, they will be separated by ", " which is meh
                    if "," in _list[-2]:
                        temp.update({headers[-1]: " ".join(_list[-2:])})
                        _list = _list[0:-2]
                    else:
                        temp.update({headers[-1]: _list.pop(-1)})
                    for i in range(len(headers) - 2):
                        temp.update({headers[-2 - i]: _list.pop(-1)})
                    temp.update({headers[0]: " ".join(_list)})
                self._cpu_list.append(temp)

            end_time = time()
            print(f'Finished fetching in {end_time - start_time}')

            with open(self._cpu_list_location, 'w') as file:
                json.dump({"cpu_list": self._cpu_list}, file, indent=4)
            self._cpu_list = []
            return {}

        def with_requests():
            import requests
            cookies = "PHPSESSID=1epjoi3d5vasbfjtdk2j15qctu; _gid=GA1.2.1601590461.1702139575; _ga=GA1.1.1336255102.1702051043; _ga_CMWM67JT90=GS1.1.1702139575.2.1.1702141329.0.0.0"
            response = requests.get("https://www.cpubenchmark.net/data/?_=1702141329768", headers={"Cookie": cookies})
            if response.status_code == 200:
                data = response.json()
                del response
                with open('cpu_response_example.json', 'w') as example:
                    json.dump(data, example, indent=4)
            return {"error": "This feature is not available yet"}

        if method in ['s', 'sel', 'selenium']:
            response = with_selenium()
        elif method in ['r', 'req', 'request', 'requests']:
            response = with_requests()
        else:
            return {'error': "wrong method"}

        if 'error' not in response.keys():
            return {"status": 200, "message": "updated successfully"}
        else:
            return response

    def get_cpu_list(self):
        try:
            with open(self._cpu_list_location, 'x'):
                print("CPU List wasn't found in the database. Fetching the values from the website")
                self.update_cpu_list(method='selenium')
                return self.get_cpu_list()
        except FileExistsError:
            print("Found a record in the database. Returning...")
            with open(self._cpu_list_location, 'r') as data_file:
                return json.load(data_file)['cpu_list']


db = Database()

if __name__ == '__main__':
    print(db.update_cpu_list(method='selenium'))
    cpu_list = db.get_cpu_list()
    temp = []
    for cpu in cpu_list:
        try:
            if int(cpu['Cores']) >= 4:
                temp.append(cpu)
        except ValueError:
            print(f"Non-integer value of cores found:\n{cpu}")
    print(len(temp))
