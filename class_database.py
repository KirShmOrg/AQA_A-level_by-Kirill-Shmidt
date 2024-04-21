from typing import Union, TypedDict
import json
import time
from enum import Enum
from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorMessage:
    message: str


class Components(Enum):
    CPU = 'CPU'
    GPU = 'GPU'
    MB = 'MB'
    RAM = 'RAM'
    PSU = 'PSU'


class FindBy(Enum):
    Filters = 'Filters'
    SearchStr = 'SearchStr'


class ComponentsWithParams(TypedDict):
    component: Components
    params: dict[str, str]


def check_components(*components: Components) -> None:
    for component in components:
        if type(component) != Components:
            print(component)
            raise TypeError(f"A component should be of type {Components}, not {type(component)}")
    return


from component_classes import CPU, GPU, Motherboard, RAM, PSU, ALL_COMPONENTS_TYPES


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
        check_components(*components_to_update)

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
    def __get_cpu_list(params: dict) -> Union[list[CPU], None]:
        from techpowerup import fetch_component_list

        component_list = fetch_component_list(Components.CPU, params=params, sort_by='name')
        if isinstance(component_list, ErrorMessage):
            print(component_list.message)
            return

        return [CPU(cpu) for cpu in component_list[Components.CPU]]

    @staticmethod
    def __get_cpu_list_by_name(cpu_name: str) -> Union[list[CPU], None]:
        from techpowerup import get_component_by_name

        cpu_list = [CPU(cpu) for cpu in get_component_by_name(Components.CPU, cpu_name)]
        return cpu_list

    @staticmethod
    def __get_gpu_list(params: dict) -> Union[list[GPU], None]:
        from techpowerup import fetch_component_list

        component_list = fetch_component_list(Components.GPU, params=params, sort_by='name')
        if isinstance(component_list, ErrorMessage):
            print(component_list.message)
            return

        return [GPU(gpu) for gpu in component_list[Components.GPU]]

    @staticmethod
    def __get_gpu_list_by_name(gpu_name: str) -> Union[list[GPU], None]:
        from techpowerup import get_component_by_name

        gpu_list = [GPU(gpu) for gpu in get_component_by_name(Components.GPU, gpu_name)]
        return gpu_list

    @staticmethod
    def __get_mb_list(params: dict) -> Union[list[Motherboard], None]:
        from motherboarddbcom import get_motherboards_list

        mb_list = get_motherboards_list(params=params)
        return [Motherboard(mb) for mb in mb_list]

    @staticmethod
    def __get_mb_list_by_name(mb_name: str) -> Union[list[Motherboard], None]:
        from motherboarddbcom import get_motherboards_list

        mb_list = get_motherboards_list({'search': mb_name})
        return [Motherboard(mb) for mb in mb_list]


    @staticmethod
    def __get_ram_list(params: dict) -> Union[list[RAM], None]:
        from provantage import get_component_list, Components

        return get_component_list(component=Components.RAM, params=params, as_objects=True)

    @staticmethod
    def __get_ram_list_by_name(ram_name: str) -> Union[list[RAM], None]:
        from provantage import get_component_by_name

        return get_component_by_name(Components.RAM, search_str=ram_name)

    @staticmethod
    def __get_psu_list(params: dict) -> Union[list[PSU], None]:
        from provantage import get_component_list, Components

        return get_component_list(component=Components.PSU, params=params, as_objects=True)

    @staticmethod
    def __get_psu_list_by_name(psu_name: str) -> Union[list[PSU], None]:
        from provantage import get_component_by_name

        return get_component_by_name(Components.PSU, search_str=psu_name)

    def get_one_component_list(self, component: Components, by: FindBy, value: Union[dict[str, str], str]) -> \
            Union[list[ALL_COMPONENTS_TYPES], None]:
        check_components(component)
        if by == FindBy.Filters:
            if component == Components.CPU:
                result = self.__get_cpu_list(value)
            elif component == Components.GPU:
                result = self.__get_gpu_list(value)
            elif component == Components.MB:
                result = self.__get_mb_list(value)
            elif component == Components.RAM:
                result = self.__get_ram_list(value)
            elif component == Components.PSU:
                result = self.__get_psu_list(value)
            else:
                raise NotImplementedError(f"Parsing {component} is not implemented yet")
            return result
        elif by == FindBy.SearchStr:
            if component == Components.CPU:
                result = self.__get_cpu_list_by_name(value)
            elif component == Components.GPU:
                result = self.__get_gpu_list_by_name(value)
            elif component == Components.MB:
                result = self.__get_mb_list_by_name(value)
            elif component == Components.RAM:
                result = self.__get_ram_list_by_name(value)
            elif component == Components.PSU:
                result = self.__get_psu_list_by_name(value)
            else:
                raise NotImplementedError(f"Parsing {component} is not implemented yet")
            return result
        else:
            raise NotImplementedError(f"Parsing by {by.value} is not implemented yet")


db = Database()

if __name__ == '__main__':
    start = time.perf_counter()

    db.update_filters(*list(Components))

    # for key, value in db.get_multiple_filters(*list(Components)).items():
    #     print(key, value, '--' * 15, sep='\n')
    print(time.perf_counter() - start)
