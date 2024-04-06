import time
import json

from component_classes.class_ram import RAM
from component_classes.class_cpu import CPU
from component_classes.class_gpu import GPU
from component_classes.class_motherboard import Motherboard


class Database:
    def __init__(self):
        self.cpu_filters_location = self.__get_full_filepath("all_jsons/techpowerup_cpu_filters.json")
        self.gpu_filters_location = self.__get_full_filepath("all_jsons/techpowerup_gpu_filters.json")
        self.mb_filters_location = self.__get_full_filepath("all_jsons/motherboarddb_mb_filters.json")
        self.provantage_manufacturers_location = self.__get_full_filepath("all_jsons/provantage_manufacturers.json")

    @staticmethod
    def __get_full_filepath(destination_path: str):
        import os

        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, destination_path)

    @staticmethod
    def __update_provantage_manufacturers() -> None:
        from provantage import get_all_manufacturers

        for_update = get_all_manufacturers()
        import json
        import os

        with open(os.path.join(os.path.dirname(__file__), 'all_jsons/provantage_manufacturers.json'), 'w') as file:
            json.dump(for_update, file, indent=4)
        print("Updated all manufacturers")

    def update_filters(self, *component_names) -> None:
        from techpowerup import get_labels_with_values as tpu_filters
        from motherboarddbcom import parse_filters as mbdb_filters

        for _filter in component_names:
            if _filter.upper() == 'CPU':
                cpu_filters = tpu_filters('CPU')
                with open(self.cpu_filters_location, 'w') as file:
                    json.dump(cpu_filters, file, indent=4)
                del cpu_filters
            elif _filter.upper() == 'GPU':
                gpu_filters = tpu_filters('GPU')
                with open(self.gpu_filters_location, 'w') as file:
                    json.dump(gpu_filters, file, indent=4)
                del gpu_filters
            elif _filter.upper() == 'MB':
                mb_filters = mbdb_filters()
                with open(self.mb_filters_location, 'w') as file:
                    json.dump(mb_filters, file, indent=4)
                del mb_filters
            elif _filter.upper() == 'RAM':
                self.__update_provantage_manufacturers()
            else:
                print(f"Can't update filter {_filter}")

    def get_filters(self, *component_names) -> list[dict]:
        result = []  # TODO: refactor it to a dictionary
        for component in component_names:
            if component.upper() == 'CPU':
                with open(self.cpu_filters_location, 'r') as file:
                    result.append(json.load(file))
            elif component.upper() == 'GPU':
                with open(self.gpu_filters_location, 'r') as file:
                    result.append(json.load(file))
            elif component.upper() == 'MB':
                with open(self.mb_filters_location, 'r') as file:
                    result.append(json.load(file))
        return result

    def get_all_provantage_manufacturers(self) -> dict[dict[str, str]]:
        with open(self.provantage_manufacturers_location, 'r') as file:
            return json.load(file)

    @staticmethod
    def get_cpu_list(params: dict) -> list[CPU]:
        from techpowerup import get_component_list

        component_list = get_component_list('CPU', params=params, sort_by='name')
        if 'error' in component_list:
            print(component_list['error'])
            return
        else:
            return [CPU(cpu) for cpu in component_list['CPU']]

    @staticmethod
    def get_gpu_list(params: dict) -> list[GPU]:
        from techpowerup import get_component_list

        component_list = get_component_list('GPU', params=params, sort_by='name')
        if 'error' in component_list:
            print(component_list['error'])
            return
        else:
            return [GPU(gpu) for gpu in component_list['GPU']]

    @staticmethod
    def get_mb_list(params: dict) -> list[Motherboard]:
        from motherboarddbcom import parse_motherboards_list

        mb_list = parse_motherboards_list(params=params)
        if 'error' in mb_list:
            print(mb_list['error'])
            return
        else:
            return [Motherboard(mb) for mb in mb_list]

    @staticmethod
    def get_ram_list(params: dict) -> list[RAM]:
        from provantage_ram import get_ram_list

        return get_ram_list(params, as_objects=True)


db = Database()
