from component_classes import CPU, GPU, RAM, PSU, Motherboard
from class_database import db, Components, FindBy


# Finished
def correct_sockets(cpu: CPU, mb: Motherboard) -> bool:
    if cpu.socket != mb.socket:
        print("The motherboard and CPU have different sockets!")
        return False
    return True


# Finished
def correct_ram(ram_list: list[RAM], mb: Motherboard, cpu: CPU) -> bool:
    # returns False if critical error, prints error if the PC will boot with this setup
    if len(ram_list) > mb.ram_slots:
        print(f"This motherboard supports only {mb.ram_slots}, got {len(ram_list)} RAM modules instead")
        return False
    for ram in ram_list:  # I might want to introduce ECC support
        if ram.ddr_gen != mb.max_ram.ddr_gen:
            print(f"Wrong Motherboard DDR generation: {mb.max_ram.ddr_gen} was expected, {ram.ddr_gen} received")
            return False
        if ram.ddr_gen != cpu.max_ram.ddr_gen:
            print(f"Wrong CPU DDR generation: {mb.max_ram.ddr_gen} was expected, {ram.ddr_gen} received")
            return False
        if ram.form_factor != mb.max_ram.form_factor:
            print(f"Wrong RAM form factor: expected {mb.max_ram.form_factor}, {ram.form_factor} received")
            return False
        if ram.speed_mhz > mb.max_ram.speed_mhz:
            print("The RAM module is too quick for this motherboard, it will automatically down-clock")
        if ram.speed_mhz > cpu.max_ram.speed_mhz:
            print("The RAM module is too quick for this CPU, it will automatically down-clock")
    total_ram_size = sum([ram.size_gb for ram in ram_list])
    if total_ram_size > mb.max_ram.size_gb:
        print(f"Too much RAM for this motherboard: {mb.max_ram.size_gb} allowed, {total_ram_size} received")

    return True


# Finished
def correct_gpu(gpu: GPU, mb: Motherboard, cpu: CPU) -> bool:
    # Returns False on critical error, prints error if it's not critical enough
    if gpu.pci_e.generation > mb.max_pci_e.generation:
        print(f'The PCIe on the motherboard is not good enough: {gpu.pci_e.generation} is required, '
              f'{mb.max_pci_e.generation} is allowed')
        return False
    if gpu.pci_e.lanes > mb.max_pci_e.lanes:
        print(
            f'Not enough PCIe lanes on the motherboard: {gpu.pci_e.lanes} is required, {mb.max_pci_e.lanes} is allowed')
        return False
    if gpu.pci_e.generation > cpu.max_pcie.generation:
        print(f'The PCIe on the CPU is not good enough: {gpu.pci_e.generation} is required, '
              f'{cpu.max_pcie.generation} is allowed')
        return False
    if gpu.pci_e.lanes > cpu.max_pcie.lanes:
        print(f'Not enough PCIe lanes on the CPU: {gpu.pci_e.lanes} is required, {cpu.max_pcie.lanes} is allowed')
        return False


# Finished
def correct_wattage(psu: PSU, cpu: CPU, gpu: GPU, ram_list: list[RAM]) -> bool:
    # NOTE: as a rule of thumb, crucial.com recommends 3 Watts per every 8 GB
    ram_consumption = sum([ram.size_gb for ram in ram_list]) * 3 / 8
    if psu.wattage > cpu.tdp_w + gpu.tdp_w + ram_consumption:
        print("Your PSU can't output enough wattage for this system!")
        return False
    return True


# Finished
def check_all(cpu: CPU, gpu: GPU, ram_list: list[RAM], mb: Motherboard, psu: PSU) -> bool:
    return correct_sockets(cpu=cpu, mb=mb) and correct_ram(ram_list=ram_list, mb=mb, cpu=cpu) and \
        correct_wattage(psu=psu, cpu=cpu, gpu=gpu, ram_list=ram_list)


if __name__ == '__main__':
    test_cpu = db.get_one_component_list(Components.CPU, by=FindBy.Filters,
                                         value={'tdp': '65 W', 'socket': 'AMD Socket AM5'})[0]
    test_cpu.convert_further_information()
    print(f"{test_cpu = }")

    test_gpu = db.get_one_component_list(Components.GPU, by=FindBy.Filters,
                                         value={'mfgr': 'NVIDIA', 'gpu': 'GP104', 'generation': "GeForce 10"})[0]
    print(f"{test_gpu = }")

    test_ram = db.get_one_component_list(Components.RAM, by=FindBy.Filters,
                                         value={'memory size': '8 GB', 'memory speed': '2666 MHz',
                                                'Memory Technology': 'DDR4 SDRAM', 'form factor': 'DIMM'})[0]
    print(f"{test_ram = }")

    test_psu = db.get_one_component_list(Components.PSU, by=FindBy.Filters,
                                         value={'output power': '300 W'})[0]
    print(f"{test_psu = }")

    test_mb = db.get_one_component_list(Components.MB, by=FindBy.Filters,
                                        value={'socket': "AM4", 'ram_type': 'DDR4', 'manufacturer': 'Biostar'})[0]
    test_mb.convert_further_data()
    print(f"{test_mb = }")

    # print(f"{test_cpu=}\n{test_mb=}\n{test_psu=}\n{test_ram=}\n{test_gpu=}")
    print(check_all(cpu=test_cpu, gpu=test_gpu, ram_list=[test_ram, test_ram], psu=test_psu, mb=test_mb))
