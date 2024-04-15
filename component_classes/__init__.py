from typing_extensions import TypeAlias, Union

from class_database import Components

from .class_cpu import CPU
from .class_gpu import GPU
from .class_motherboard import Motherboard
from .class_ram import RAM
from .class_psu import PSU


ALL_COMPONENTS_TYPES: TypeAlias = Union[type[CPU], type[GPU], type[Motherboard], type[RAM], type[PSU]]

ALL_CLASSES_DICT: dict[Components, ALL_COMPONENTS_TYPES] = {
    Components.CPU: CPU,
    Components.GPU: GPU,
    Components.MB: Motherboard,
    Components.RAM: RAM,
    Components.PSU: PSU
}
