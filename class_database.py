import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from time import sleep

driver = webdriver.Chrome()


class Database:
    def __init__(self,
                 cpus_link="https://www.cpubenchmark.net/CPU_mega_page.html",
                 gpus_link="https://www.videocardbenchmark.net/GPU_mega_page.html"):
        self._all_cpus_link = cpus_link
        self._all_gpus_link = gpus_link
        self._cpu_list = []
        self._gpu_list = []

    def update_cpu_list(self):
        def with_selenium():
            driver.get(self._all_cpus_link)
            sleep(3)
            select = Select(driver.find_element(by=By.NAME, value="cputable_length"))
            select.select_by_value("-1")
            table = driver.find_element(by=By.ID, value="cputable")

            # headers = [i.text for i in table.find_element(by=By.CSS_SELECTOR, value='thead').find_elements(by=By.CSS_SELECTOR, value='th')]

            headers = ['CPU name', 'Cores', 'CPU Mark', 'Thread Mark', 'TDP(W)', 'Socket', 'Category']

            tbody = table.find_element(by=By.CSS_SELECTOR, value='tbody')
            for row in tbody.find_elements(by=By.CSS_SELECTOR, value='tr'):
                _list = row.text.split()
                temp = {}
                for i in range(len(headers) - 1):
                    temp.update({headers[-1 - i]: _list.pop(-1)})

                temp.update({headers[0]: " ".join(_list)})
                self._cpu_list.append(temp)

            with open("cpu_list.json", 'w') as file:
                json.dump({"data": self._cpu_list}, file, indent=4)

        def with_requests():
            cookies = "PHPSESSID=1epjoi3d5vasbfjtdk2j15qctu; _gid=GA1.2.1601590461.1702139575; _ga=GA1.1.1336255102.1702051043; _ga_CMWM67JT90=GS1.1.1702139575.2.1.1702141329.0.0.0"
            response = requests.get("https://www.cpubenchmark.net/data/?_=1702141329768", headers={"Cookie": cookies})
            if response.status_code == 200:
                data = response.json()
                del response
                with open('cpu_response_example.json', 'w') as example:
                    json.dump(data, example, indent=4)

        with_selenium()
        return "stopped"


db = Database()

if __name__ == '__main__':
    print(db.update_cpu_list())
