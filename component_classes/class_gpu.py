import datetime
from dataclasses import dataclass, field


@dataclass
class PCIe:
    init_string: str = field(repr=False)

    generation: float = field(init=False)
    lanes: int = field(init=False)

    def __post_init__(self):
        temp_list: list[str] = self.init_string.split()
        if len(temp_list) != 3:
            raise IndexError(f"PCIe info should be 3 words, not {len(temp_list)}: {temp_list}")

        self.generation = float(temp_list[1])
        self.lanes = int(temp_list[2].lstrip('x'))


@dataclass
class GMem:
    init_string: str = field(repr=False)

    size_gb: int = field(init=False)
    type: str = field(init=False)
    width_bits: int = field(init=False, repr=False)
    speed_mhz: int = field(init=False, repr=False)

    def __post_init__(self):
        # TODO: handle empty string
        temp_list: list[str] = self.init_string.split(', ')
        if len(temp_list) != 4:
            raise IndexError(f"memory should contain 4 words, not {len(temp_list)}: {temp_list}")
        if 'GB' not in temp_list[0] or "DDR" not in temp_list[1] or 'bit' not in temp_list[2]:
            raise ValueError(f"Wrong inputs: {self.init_string}")
        self.size_gb, self.type, self.width_bits, self.speed_mhz = int(temp_list[0].split()[0]), temp_list[1], int(
            temp_list[2].split()[0]), int(temp_list[3].split()[0])  # readability is definitely not a priority in this one because no need to

        # should I delete that?
        del self.init_string


@dataclass
class GPU_cores:
    init_string: str = field(repr=False)

    shaders: int = field(init=False)
    tmus: int = field(init=False)
    rops: int = field(init=False)

    def __post_init__(self):
        temp_list: list[str] = self.init_string.split(' / ')
        if len(temp_list) != 3:
            raise IndexError("")
        self.shaders, self.tmus, self.rops = temp_list


@dataclass
class GPU:
    all_specs: dict[str, str] = field(repr=False)

    human_name: str = field(init=False)
    # for all fields where repr=True it should be switched to False after testing
    gpu_chip: str = field(init=False, repr=False)
    speed_str: str = field(init=False, repr=False)
    release_date: str = field(init=False, repr=False)
    pci_e: PCIe = field(init=False)
    memory: GMem = field(init=False)
    cores: GPU_cores = field(init=False)

    def __post_init__(self):
        self.memory = GMem(f"{self.all_specs['Memory']}, {self.all_specs['Memory clock']}")
        self.human_name = self.all_specs['Product Name']
        self.gpu_chip = self.all_specs['GPU Chip']
        self.speed_str = self.all_specs['GPU clock']
        self.release_date = self.all_specs['Released']
        self.pci_e = PCIe(self.all_specs['Bus'])
        self.cores = GPU_cores(self.all_specs['Shaders / TMUs / ROPs'])


if __name__ == '__main__':
    TEST_GPU = {'Product Name': 'GeForce RTX 4050', 'GPU Chip': 'AD107', 'Released': 'Unknown', 'Bus': 'PCIe 4.0 x8',
                'Memory': '6 GB, GDDR6, 96 bit', 'GPU clock': '2505 MHz', 'Memory clock': '2250 MHz',
                'Shaders / TMUs / ROPs': '2560 / 80 / 32'}
    TEST_GPU = GPU(TEST_GPU)
    print(TEST_GPU)
