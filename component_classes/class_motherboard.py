from dataclasses import dataclass, field

from component_classes.class_ram import RAM


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

    def __post_init__(self):
        from motherboarddbcom import get_mb_socket
        self.socket = get_mb_socket(self.all_specs)
        self.human_name = self.all_specs['Name']
        self.form_factor = self.all_specs['Form Factor']
        self.chipset = self.all_specs['Chipset']
        self.release_year = int(self.all_specs['Release Year'])
        self.convert_ram()

    def convert_ram(self) -> None:
        if 'RAM' not in self.all_specs.keys():
            return
        temp_list: list = self.all_specs['RAM'].split()
        if len(temp_list) != 5:
            raise IndexError(f"RAM should be 5 words, not {len(temp_list)}: {temp_list}")
        self.ram_slots = int(temp_list[0].rstrip('x'))
        ram_list = []
        ram_list += [f"{temp_list[1]} SDRAM"]
        ram_list += [f"{' '.join(temp_list[-2:])} Memory Speed"]
        self.max_ram = RAM(ram_list)


if __name__ == '__main__':
    TEST_MB = {'Name': 'Asus TUF B450M-Pro Gaming', 'Socket(s)': '1x AM4', 'Form Factor': 'Micro-ATX',
               'Chipset': 'AMD B450', 'RAM': '2x DDR4 @ 3466 MHz', 'Release Year': '2018',
               'Audio Chip': 'Realtek ALC887', 'USB 2.0 Headers': None, 'USB 3.0 Headers': None, 'SATA3': '4'}
    TEST_MB = Motherboard(TEST_MB)
    print(TEST_MB.socket, TEST_MB.all_specs)
