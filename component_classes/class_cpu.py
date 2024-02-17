class CPU:
    def __init__(self, init_dict: dict):
        self.__specs = init_dict
        from techpowerup import get_cpu_socket
        self.__socket = get_cpu_socket(self.all_specs)

    @property
    def all_specs(self) -> dict:
        return self.__specs

    @property
    def socket(self) -> str:
        return self.__socket


if __name__ == '__main__':
    TEST_CPU = {'Name': 'A10-7870K', 'Codename': 'Godaveri', 'Cores': '4', 'Clock': '3.9 to 4.1 GHz',
                'Socket': 'Socket FM2+', 'Process': '28 nm', 'L3 Cache': 'N/A', 'TDP': '95 W',
                'Released': 'May 28th, 2015'}

    TEST_CPU = CPU(init_dict=TEST_CPU)
    print(TEST_CPU.socket, TEST_CPU.all_specs)
