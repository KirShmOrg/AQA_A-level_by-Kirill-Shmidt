from dataclasses import dataclass, field

from component_classes.class_ram import RAM
from component_classes.class_gpu import GPU, PCIe


@dataclass
class Motherboard:
    all_specs: dict[str] = field(repr=False)

    human_name: str = field(init=False)
    socket: str = field(init=False, default='')
    form_factor: str = field(init=False, default='', repr=False)
    chipset: str = field(init=False, default='', repr=False)
    max_ram: RAM = field(init=False, default=RAM(['']))
    release_year: int = field(init=False, default=0)
    ram_slots: int = field(init=False, default=0, repr=False)
    further_link: str = field(init=False, default='', repr=False)

    _max_pci_e: PCIe = field(init=False, default=None, repr=False)

    @property
    def max_pci_e(self) -> PCIe:
        if self._max_pci_e is None:
            self.convert_further_data()
        return self._max_pci_e

    def __post_init__(self):
        from motherboarddbcom import get_mb_socket
        self.socket = get_mb_socket(self.all_specs)
        self.human_name = self.all_specs.get('Name', '')
        self.form_factor = self.all_specs.get('Form Factor', '')
        self.chipset = self.all_specs.get('Chipset', '')
        self.release_year = int(self.all_specs.get('Release Year', 0))
        self.convert_ram()
        self.further_link = self.all_specs.get('Link', '')

    def convert_ram(self) -> None:
        if 'RAM' not in self.all_specs.keys():
            return
        temp_list: list = self.all_specs.get('RAM').split()
        if len(temp_list) != 5:
            raise IndexError(f"RAM should be 5 words, not {len(temp_list)}: {temp_list}")
        self.ram_slots = int(temp_list[0].rstrip('x'))
        ram_list = []
        ram_list += [f"{temp_list[1]} SDRAM"]
        ram_list += [f"{' '.join(temp_list[-2:])} Memory Speed"]
        self.max_ram = RAM(ram_list)

    def convert_further_data(self) -> None:
        from motherboarddbcom import get_further_information
        deep_data = get_further_information(link=self.further_link)
        self.max_ram.size_gb = int(deep_data['memory']['Maximum Capacity'].split()[0])
        self.max_ram.form_factor = deep_data['memory']['Slot Type'].split()[-1]
        self._max_pci_e = PCIe(' '.join(deep_data['expansion slots'][0].split()[1:4]))


if __name__ == '__main__':
    TEST_MB = {'Name': 'Asus TUF B450M-Pro Gaming', 'Socket(s)': '1x AM4', 'Form Factor': 'Micro-ATX',
               'Chipset': 'AMD B450', 'RAM': '2x DDR4 @ 3466 MHz', 'Release Year': '2018',
               'Audio Chip': 'Realtek ALC887', 'USB 2.0 Headers': None, 'USB 3.0 Headers': None, 'SATA3': '4',
               'Link': 'https://motherboarddb.com/motherboards/1463/ROG%20Strix%20B450-F%20Gaming/'}
    TEST_MB = Motherboard(TEST_MB)
    TEST_MB.convert_further_data()
    print(TEST_MB.max_ram.size_gb, TEST_MB.max_pci_e)
