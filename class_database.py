import json
import time
from enum import Enum

from component_classes.class_ram import RAM
from component_classes.class_psu import PSU
from component_classes.class_cpu import CPU
from component_classes.class_gpu import GPU
from component_classes.class_motherboard import Motherboard


class Components(Enum):
    CPU = 'CPU'
    GPU = 'GPU'
    MB = 'MB'
    RAM = 'RAM'
    PSU = 'PSU'


class Database:

    def __init__(self):
        self._cpu_filters_location = self.__get_full_filepath("all_jsons/techpowerup_cpu_filters.json")
        self._gpu_filters_location = self.__get_full_filepath("all_jsons/techpowerup_gpu_filters.json")
        self._mb_filters_location = self.__get_full_filepath("all_jsons/motherboarddb_mb_filters.json")
        self._ram_filters_location = self.__get_full_filepath('all_jsons/provantage_ram_filters.json')
        self._psu_filters_location = self.__get_full_filepath('all_jsons/provantage_psu_filters.json')

    @staticmethod
    def __get_full_filepath(destination_path: str) -> str:
        import os

        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, destination_path)

    def get_component_filepath(self, component: Components) -> str:
        if component == Components.CPU:
            return self.__get_full_filepath(self._cpu_filters_location)
        elif component == Components.GPU:
            return self.__get_full_filepath(self._gpu_filters_location)
        elif component == Components.MB:
            return self.__get_full_filepath(self._mb_filters_location)
        elif component == Components.RAM:
            return self.__get_full_filepath(self._ram_filters_location)
        elif component == Components.PSU:
            return self.__get_full_filepath(self._psu_filters_location)

    def update_filters(self, *components_to_update: Components) -> None:
        from techpowerup import get_labels_with_values as techpowerup_filters
        from motherboarddbcom import parse_filters as mbdb_filters
        from provantage import parse_filters as provantage_filters

        def dump_into_file(component_: Components, value) -> None:
            with open(self.get_component_filepath(component_), 'w') as file:
                json.dump(value, file, indent=4)

        for component in components_to_update:
            if component == Components.CPU:
                dump_into_file(component, techpowerup_filters('CPU'))
            elif component == Components.GPU:
                dump_into_file(component, techpowerup_filters('GPU'))
            elif component == Components.MB:
                dump_into_file(component, mbdb_filters())
            elif component == Components.RAM:
                dump_into_file(component, provantage_filters(Components.RAM))
            elif component == Components.PSU:
                dump_into_file(component, provantage_filters(Components.PSU))
            else:
                print(f"Can't update filters for {component}")

    def get_filters(self, *component_names: Components) -> dict[Components, dict]:
        def load_from_file(component_: Components) -> dict:
            with open(self.get_component_filepath(component_), 'r') as file:
                return json.load(file)

        result = {}
        for component in component_names:
            if type(component) != Components:
                print(f"Can't get filter for non-Components type: {type(component)}")
                continue
            result.update({component: load_from_file(component)})

        return result

    @staticmethod
    def get_cpu_list(params: dict) -> list[CPU]:
        from techpowerup import get_component_list

        component_list = get_component_list(Components.CPU, params=params, sort_by='name')
        if 'error' in component_list:
            print(component_list['error'])
            return
        else:
            return [CPU(cpu) for cpu in component_list[Components.CPU]]

    @staticmethod
    def get_gpu_list(params: dict) -> list[GPU]:
        from techpowerup import get_component_list

        component_list = get_component_list(Components.GPU, params=params, sort_by='name')
        if 'error' in component_list:
            print(component_list['error'])
            return
        else:
            return [GPU(gpu) for gpu in component_list[Components.GPU]]

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
        from provantage import get_component_list, Components

        return get_component_list(component=Components.RAM, params=params, as_objects=True)

    @staticmethod
    def get_psu_list(params: dict) -> list[PSU]:
        from provantage import get_component_list, Components

        return get_component_list(component=Components.PSU, params=params, as_objects=True)


db = Database()

if __name__ == '__main__':
    # db.update_filters(*list(Components))
    start = time.perf_counter()
    for key, value in db.get_filters(*list(Components)).items():
        print(key, value, '--' * 15, sep='\n')
    print(time.perf_counter() - start)