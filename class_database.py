# import techpowerup
# import motherboarddbcom


class Database:
    def __init__(self):
        # from techpowerup import LINKS
        # from motherboarddbcom import BASE_URL as MB_BASE_URL
        # self.cpu_link = LINKS['CPU']
        # self.gpu_link = LINKS['GPU']
        # self.mb_link = MB_BASE_URL
        self.cpu_filters_location = "all_jsons/techpowerup_cpu_filters.json"
        self.gpu_filters_location = "all_jsons/techpowerup_gpu_filters.json"
        self.mb_filters_location = "all_jsons/motherboarddb_mb_filters.json"
        self.ram_filters_location = "all_jsons/provantage_ram_filters.json"

    def update_filters(self, *component_names):
        import json
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
            else:
                print(f"Can't update {_filter}")

    def get_filters(self, *component_names):
        import json
        result = []
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

    @staticmethod
    def get_cpu_list(params: dict):
        from techpowerup import get_component_list
        component_list = get_component_list('CPU', params=params, sort_by='name')
        if 'error' in component_list:
            print(component_list['error'])
            return
        else:
            return component_list['CPU'][2:]

    @staticmethod
    def get_gpu_list(params: dict):
        from techpowerup import get_component_list
        component_list = get_component_list('GPU', params=params, sort_by='name')
        if 'error' in component_list:
            print(component_list['error'])
            return
        else:
            return component_list['GPU'][2:]

    @staticmethod
    def get_mb_list(params: dict):
        from motherboarddbcom import parse_motherboards_list
        mb_list = parse_motherboards_list(params=params)
        if 'error' in mb_list:
            print(mb_list['error'])
            return
        else:
            return mb_list


db = Database()

if __name__ == '__main__':
    db.update_filters('CPU', 'GPU', 'MB')
    cpu_list = db.get_cpu_list(params={"mfgr": 'AMD',
                                       "released": '2022',
                                       "mobile": 'No',
                                       "server": 'No',
                                       "multiUnlocked": 'Yes'})
    gpu_list = db.get_gpu_list(params={'mfgr': 'NVIDIA',
                                       'released': '2023',
                                       'mobile': 'No',
                                       'workstation': 'No',
                                       'performance': '1080'})
    print(cpu_list)
    print(gpu_list)
    mb_list = db.get_mb_list(params={'manufacturer': 'Asus',
                                     'form_factor': 'Micro-ATX',
                                     'socket': 'AM4',
                                     'chipset': 'AMD B450',
                                     })
    print(mb_list)
