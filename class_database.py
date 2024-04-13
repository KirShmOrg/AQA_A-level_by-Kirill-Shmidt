from typing import Union, TypedDict
import json
import time
from enum import Enum
from dataclasses import dataclass

from component_classes.class_ram import RAM
from component_classes.class_psu import PSU
from component_classes.class_cpu import CPU
from component_classes.class_gpu import GPU
from component_classes.class_motherboard import Motherboard


@dataclass(frozen=True)
class ErrorMessage:
    message: str


class Components(Enum):
    CPU = 'CPU'
    GPU = 'GPU'
    MB = 'MB'
    RAM = 'RAM'
    PSU = 'PSU'


class ComponentsWithParams(TypedDict):
    component: Components
    params: dict[str, str]


def check_components(*components) -> None:
    for component in components:
        if type(component) != Components:
            print(component)
            raise TypeError(f"A component should be of type {Components}, not {type(component)}")
    return


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

    def __get_component_filepath(self, component: Components) -> str:
        check_components(component)
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
        else:
            raise FileNotFoundError(f"The component {component} doesn't have a filepath")

    def __read_component_file(self, component: Components) -> dict:
        check_components(component)
        with open(self.__get_component_filepath(component), 'r') as file:
            return json.load(file)

    def update_filters(self, *components_to_update: Components) -> None:
        check_components(components_to_update)

        from techpowerup import get_labels_with_values as techpowerup_filters
        from motherboarddbcom import parse_filters as mbdb_filters
        from provantage import parse_filters as provantage_filters

        def dump_into_file(component_: Components, value) -> None:  # TODO: might refactor it into a sep. function
            with open(self.__get_component_filepath(component_), 'w') as file:
                json.dump(value, file, indent=4)

        for component in components_to_update:
            if component in [Components.CPU, Components.GPU]:
                dump_into_file(component, techpowerup_filters(component))
            elif component == Components.MB:
                dump_into_file(component, mbdb_filters())
            elif component in [Components.RAM, Components.PSU]:
                dump_into_file(component, provantage_filters(component))
            else:
                print(f"Can't update filters for {component}")

    def get_single_filter(self, component: Components) -> dict:
        check_components(component)
        return self.__read_component_file(component)

    def get_multiple_filters(self, *components: Components) -> dict[Components, dict]:
        check_components(*components)

        result = {}
        for component in components:
            result.update({component: self.get_single_filter(component)})

        return result

    @staticmethod
    def get_cpu_list(params: dict) -> Union[list[CPU], None]:
        from techpowerup import fetch_component_list

        component_list = fetch_component_list(Components.CPU, params=params, sort_by='name')
        if isinstance(component_list, ErrorMessage):
            print(component_list.message)
            return

        return [CPU(cpu) for cpu in component_list[Components.CPU]]

    @staticmethod
    def get_gpu_list(params: dict) -> Union[list[GPU], None]:
        from techpowerup import fetch_component_list

        component_list = fetch_component_list(Components.GPU, params=params, sort_by='name')
        if isinstance(component_list, ErrorMessage):
            print(component_list.message)
            return

        return [GPU(gpu) for gpu in component_list[Components.GPU]]

    @staticmethod
    def get_mb_list(params: dict) -> list[Motherboard]:
        from motherboarddbcom import parse_motherboards_list

        mb_list = parse_motherboards_list(params=params)
        return [Motherboard(mb) for mb in mb_list]

    @staticmethod
    def get_ram_list(params: dict) -> list[RAM]:
        from provantage import get_component_list, Components

        return get_component_list(component=Components.RAM, params=params, as_objects=True)

    @staticmethod
    def get_psu_list(params: dict) -> list[PSU]:
        from provantage import get_component_list, Components

        return get_component_list(component=Components.PSU, params=params, as_objects=True)

    def get_multiple_components(self, components_with_params: ComponentsWithParams) -> \
            dict[Components, Union[list, None]]:
        check_components(components_with_params.keys())
        result = {}
        for component, params in components_with_params.keys():
            if component == Components.CPU:
                value_ = self.get_cpu_list(params)
            elif component == Components.GPU:
                value_ = self.get_gpu_list(params)
            elif component == Components.MB:
                value_ = self.get_mb_list(params)
            elif component == Components.RAM:
                value_ = self.get_ram_list(params)
            elif component == Components.PSU:
                value_ = self.get_psu_list(params)
            else:
                raise NotImplementedError(f"Parsing {component} is not implemented yet")
            result.update({component: value_})

        return result


db = Database()

if __name__ == '__main__':
    # db.update_filters(*list(Components))
    start = time.perf_counter()

    for key, value in db.get_multiple_filters(*list(Components)).items():
        print(key, value, '--' * 15, sep='\n')

    print(time.perf_counter() - start)
