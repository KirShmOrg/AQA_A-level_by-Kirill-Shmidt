from class_database import db
from time import sleep
from time import perf_counter


def test_cpu() -> None:
    cpu_test_start = perf_counter()
    cpu_list = db.get_cpu_list(params={"mfgr": 'AMD',
                                       "released": '2022',
                                       "mobile": 'No',
                                       "server": 'No',
                                       "multiUnlocked": 'Yes'})
    for cpu in cpu_list:
        # print(cpu.all_specs['Released'], cpu.release_year, cpu.exists, sep=' | ')
        print(cpu)
    print(perf_counter() - cpu_test_start)


def test_gpu() -> None:
    gpu_test_start = perf_counter()
    gpu_list = db.get_gpu_list(params={'mfgr': 'NVIDIA',
                                       'released': '2023',
                                       'mobile': 'No',
                                       'workstation': 'No',
                                       'performance': '1080'})
    for gpu in gpu_list:
        # print(gpu.all_specs['Released'], gpu.release_year, gpu.exists, sep=' | ')
        print(gpu)
    print(perf_counter() - gpu_test_start)


def test_ram() -> None:
    ram_test_start = perf_counter()
    ram_list = db.get_ram_list({
        'manufacturer': 'Samsung',
        'size': '8 GB',
        'ddr_type': 'DDR4 SDRAM'
    })
    for ram in ram_list:
        print(ram)
    print(perf_counter() - ram_test_start)


def test_psu() -> None:
    psu_test_start = perf_counter()
    psu_list = db.get_psu_list({
        'manufacturer': "EVGA",
        'modular': 'yes',
        'power': '650 W'
    })
    for psu in psu_list:
        print(psu)
    print(perf_counter() - psu_test_start)


def test_mb() -> None:
    mb_test_start = perf_counter()
    mb_list = db.get_mb_list(params={'manufacturer': 'Asus',
                                     'form_factor': 'Micro-ATX',
                                     'socket': 'AM4',
                                     'chipset': 'AMD B450',
                                     })
    for mb in mb_list:
        print(mb)
    print(perf_counter() - mb_test_start)


def run_all_tests() -> None:
    all_tests = [test_cpu, test_gpu, test_ram, test_psu, test_mb]
    for run_test in all_tests:
        run_test()
        print('--' * 15)
        sleep(1)


if __name__ == '__main__':
    start_time = perf_counter()
    # db.update_filters('CPU', 'GPU', 'MB', 'RAM')
    # run_all_tests()
    test_mb()
    # test_ram()
    # test_cpu()
    # test_gpu()
    # test_psu()
    test_duration = perf_counter() - start_time
    print(test_duration)
