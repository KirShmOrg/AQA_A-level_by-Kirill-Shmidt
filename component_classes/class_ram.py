from dataclasses import dataclass, field


@dataclass
class RAM:
    init_list: list[str] = field(repr=False)

    ddr_gen: int = field(init=False, default=0)
    cl_timing: int = field(init=False, default=0)
    size_gb: int = field(init=False, default=0)
    form_factor: str = field(init=False, default='')
    speed_mhz: int = field(init=False, default=0)
    full_link: str = field(init=False, default='', repr=False)

    def __post_init__(self):
        for element in self.init_list:
            if 'SDRAM' in element:
                temp_list = element.split()
                self.ddr_gen = int(temp_list[0][-1])
            elif element.startswith('CL'):
                self.cl_timing = int(element[2:])
            elif element.endswith('Memory Size'):
                temp_list = element.split()[0:2]  # only the value and the units
                if temp_list[-1] != 'GB':
                    raise ValueError(f"Memory size should be in GB, not in {temp_list[-1]}")
                self.size_gb = int(temp_list[0])
            elif element.endswith('Memory Speed'):
                temp_list = element.split()[0:2]  # only the value and the unit
                if temp_list[-1] != 'MHz':
                    raise ValueError(f"Memory speed should be in MHz, not in {temp_list[-1]}")
                self.speed_mhz = int(temp_list[0])
            elif element.endswith('DIMM'):
                self.form_factor = element
            elif element.endswith('.htm'):
                self.full_link = 'provantage.com' + element
