from component_classes.class_cpu import CPU
from component_classes.class_gpu import GPU
from component_classes.class_ram import RAM
from component_classes.class_psu import PSU
from component_classes.class_motherboard import Motherboard
from class_database import db

def correct_sockets(cpu: CPU, mb: Motherboard) -> bool:
    return cpu.socket == mb.socket


def correct_ram(ram_list: list[RAM], mb: Motherboard) -> bool:
    if len(ram_list) > mb.ram_slots:
        print(f"This motherboard supports only {mb.ram_slots}, got {len(ram_list)} RAM modules instead")
        return False
    for ram in ram_list:
        if ram.ddr_gen != mb.max_ram.ddr_gen:
            print(f"Wrong DDR generation: {mb.max_ram.ddr_gen} was expected, {ram.ddr_gen} received")
            return False
        if ram.speed_mhz > mb.max_ram.speed_mhz:
            print("The RAM module is too quick for this motherboard, it will automatically down-clock")

    return True


def correct_gpu(gpu: GPU, mb: Motherboard) -> bool:
    raise NotImplementedError("Can't do that yet")


def correct_wattage(psu: PSU, cpu: CPU, gpu: GPU):
    return psu.wattage > cpu.tdp_w + gpu.tdp_w


def check_all(cpu: CPU, gpu: GPU, ram_list: list[RAM], mb: Motherboard, psu: PSU) -> bool:
    return correct_wattage(psu=psu, cpu=cpu, gpu=gpu) and correct_sockets(cpu=cpu, mb=mb) \
        and correct_ram(ram_list=ram_list, mb=mb)


if __name__ == '__main__':
    test_cpu = db.get_cpu_list({'tdp': '65 W', 'socket': 'AMD Socket AM4'})[0]
    print(f"{test_cpu = }")
    test_gpu = db.get_gpu_list({'mfgr': 'NVIDIA', 'gpu': 'GP104', 'generation': "GeForce 10"})[0]
    print(f"{test_gpu = }")
    test_ram = RAM(['8 GB Memory Size', '2666 MHz Memory Speed', 'DDR4 SDRAM'])
    print(f"{test_ram = }")
    test_psu = PSU(['300 W Output Power'])
    print(f"{test_psu = }")
    test_mb = db.get_mb_list({'socket': "AM4", 'ram_type': 'DDR4', 'manufacturer': 'Biostar'})[0]
    print(f"{test_mb = }")
    # print(f"{test_cpu=}\n{test_mb=}\n{test_psu=}\n{test_ram=}\n{test_gpu=}")
    print(check_all(cpu=test_cpu, gpu=test_gpu, ram_list=[test_ram, test_ram], psu=test_psu, mb=test_mb))
