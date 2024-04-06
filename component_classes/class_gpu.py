import datetime
import time
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
class GCores:
    init_string: str = field(repr=False)

    shaders: int = field(init=False)
    tmus: int = field(init=False)
    rops: int = field(init=False)

    def __post_init__(self):
        temp_list: list[str] = self.init_string.split(' / ')
        if len(temp_list) != 3:
            raise IndexError("")
        self.shaders, self.tmus, self.rops = map(int, temp_list)


@dataclass
class GPU:
    all_specs: dict[str, str] = field(repr=False)

    human_name: str = field(init=False)
    # for all fields where repr=True it should be switched to False after testing
    gpu_chip: str = field(init=False, repr=False, default='')
    speed_str: str = field(init=False, repr=False, default='0 MHz')
    release_year: int = field(init=False, repr=False, default=0)
    pci_e: PCIe = field(init=False, default=PCIe('PCIe 0.0 x0'))
    memory: GMem = field(init=False, default=GMem('0 GB, GDDR0, 0 bits, 0 MHz'))
    cores: GCores = field(init=False, default=GCores('0 / 0 / 0'))
    further_link: str = field(init=False, repr=False, default='')
    exists: bool = field(init=False, repr=False, default=True)
    # TODO: write proper checks, bloody hell

    def __post_init__(self):
        self.memory = GMem(f"{self.all_specs['Memory']}, {self.all_specs['Memory clock']}")
        self.human_name = self.all_specs['Product Name']
        self.gpu_chip = self.all_specs['GPU Chip']
        self.speed_str = self.all_specs['GPU clock']
        self.convert_release_year()
        self.pci_e = PCIe(self.all_specs['Bus'])
        self.cores = GCores(self.all_specs['Shaders / TMUs / ROPs'])
        self.__tdp = None
        self.further_link = f"https://www.techpowerup.com{self.all_specs.get('Link', '')}"

    def convert_release_year(self) -> None:
        if self.all_specs['Released'] in ['Unknown', 'N/A', None, 'None']:
            self.release_year = 0
            return
        elif self.all_specs['Released'] == 'Never Released':
            self.exists = False
            self.release_year = -1
            return
        self.release_year = int(self.all_specs['Released'].split()[-1])

    def __fetch_tdp(self) -> int:
        time.sleep(3)  # it is bad, but we have to respect the server
        from techpowerup import get_gpu_tdp
        return get_gpu_tdp(self.further_link)
    @property
    def tdp(self) -> int:
        if self.__tdp is None:
            self.__tdp = self.__fetch_tdp()  # TODO: remove an infinite loop if fetch returns None
        return self.__tdp



if __name__ == '__main__':
    TEST_GPU = {'Product Name': 'GeForce RTX 4050', 'GPU Chip': 'AD107', 'Released': 'Unknown', 'Bus': 'PCIe 4.0 x8',
                'Memory': '6 GB, GDDR6, 96 bit', 'GPU clock': '2505 MHz', 'Memory clock': '2250 MHz',
                'Shaders / TMUs / ROPs': '2560 / 80 / 32'}
    TEST_GPU = GPU(TEST_GPU)
    print(TEST_GPU)
