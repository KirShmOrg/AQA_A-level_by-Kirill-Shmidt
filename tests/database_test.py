from time import sleep

from class_database import db, Components, FindBy
from motherboarddbcom import generate_link_and_query as mbdb_link_and_query
from provantage import generate_link as provantage_link
from techpowerup import generate_link as techpowerup_link
from wrappers import measure_time


@measure_time
def test_cpu() -> None:
    test_params = {"mfgr": 'AMD',
                   "released": '2022',
                   "mobile": 'No',
                   "server": 'No',
                   "multiUnlocked": 'Yes'}
    print(techpowerup_link(Components.CPU, test_params))
    cpu_list = db.get_one_component_list(Components.CPU, by=FindBy.Filters, value=test_params)
    for cpu in cpu_list:
        # print(cpu.all_specs['Released'], cpu.release_year, cpu.exists, sep=' | ')
        print(cpu)
    return


@measure_time
def test_gpu() -> None:
    test_params = {'mfgr': 'NVIDIA',
                   'released': '2023',
                   'mobile': 'No',
                   'workstation': 'No',
                   'performance': '1080'}
    print(techpowerup_link(Components.GPU, test_params))
    gpu_list = db.get_one_component_list(Components.GPU, by=FindBy.Filters, value=test_params)
    for gpu in gpu_list:
        # print(gpu.all_specs['Released'], gpu.release_year, gpu.exists, sep=' | ')
        print(gpu)
    return


@measure_time
def test_ram() -> None:
    test_params = {
        'manufacturer': 'Samsung',
        'memory size': '8 GB',
        'memory technology': 'DDR4 SDRAM'
    }
    print(provantage_link(Components.RAM, test_params))
    ram_list = db.get_one_component_list(Components.RAM, by=FindBy.Filters, value=test_params)
    for ram in ram_list:
        print(ram)
    return


@measure_time
def test_psu() -> None:
    test_params = {
        'manufacturer': "EVGA",
        # 'modular': 'yes',
        'output power': '650 W'
    }
    print(provantage_link(Components.PSU, test_params))
    psu_list = db.get_one_component_list(Components.PSU, by=FindBy.Filters, value=test_params)
    for psu in psu_list:
        print(psu)
    return


@measure_time
def test_mb() -> None:
    test_params = {'manufacturer': 'Asus',
                   'form_factor': 'Micro-ATX',
                   'socket': 'AM4',
                   'chipset': 'AMD B450',
                   }
    print(mbdb_link_and_query(test_params)['link'])
    mb_list = db.get_one_component_list(Components.MB, by=FindBy.Filters, value=test_params)
    for mb in mb_list:
        print(mb)
    return


def run_all_tests() -> None:
    all_tests = [test_cpu, test_gpu, test_ram, test_psu, test_mb]
    for run_test in all_tests:
        run_test()
        print('--' * 15)
        sleep(1)
    print("All tests passed successfully")
    return


@measure_time
def main() -> None:
    run_all_tests()
    # test_mb()
    # test_ram()
    # test_cpu()
    # test_gpu()
    # test_psu()


if __name__ == '__main__':
    main()
    # for gpu in db.get_one_component_list(Components.GPU, by=FindBy.SearchStr, value='4090'):
    #     print(gpu)
