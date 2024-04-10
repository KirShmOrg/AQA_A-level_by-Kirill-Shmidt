from dataclasses import dataclass, field

@dataclass
class PSU:
    init_list: list[str] = field(repr=False)

    product_name: str = field(init=False, default='', repr=False)
    wattage: int = field(init=False, default=0)
    efficiency: float = field(init=False, default=0.00)
    manufacturer_name: str = field(init=False, default='', repr=False)
    further_link: str = field(init=False, default='', repr=False)
    # __is_modular: bool = field(init=False, default=False, repr=False)
    # __certificate: str = field(init=False, default=False, repr=False) # kinda redundant since we usually have the
    # values of efficiency anyway

    def __post_init__(self):
        for element in self.init_list:
            if element.startswith('Name: '):
                self.product_name = element[len('Name: '):]
            elif element.endswith('% Efficiency'):
                self.efficiency = round(int(element.split('%')[0])/100, 2)
            elif element.endswith('W Output Power'):
                self.wattage = int(element.split('W')[0])
            elif element.startswith('Link: '):
                self.further_link = 'provantage.com' + element.split()[-1]
