from dataclasses import dataclass, field

@dataclass
class PSU:
    init_list: list[str] = field(repr=False)

    wattage: int = field(init=False, default=0)
    efficiency: float = field(init=False, default=0.00)


    def __post_init__(self):
        for element in self.init_list:
            if element.lower().endswith('% Efficiency'.lower()):
                self.efficiency = round(int(element.split('%')[0])/100, 2)
            elif element.lower().endswith('W Output Power'.lower()):
                self.wattage = int(element.split('W')[0])
