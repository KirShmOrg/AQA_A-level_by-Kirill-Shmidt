class Motherboard:
    def __init__(self, init_dict: dict):
        self.__specs = init_dict
        from motherboarddbcom import get_mb_socket
        self.__socket = get_mb_socket(self.all_specs)

    @property
    def all_specs(self) -> dict:
        return self.__specs

    @property
    def socket(self) -> str:
        return self.__socket


if __name__ == '__main__':
    TEST_MB = {'Name': 'Asus TUF B450M-Pro Gaming', 'Socket(s)': '1x AM4', 'Form Factor': 'Micro-ATX',
               'Chipset': 'AMD B450', 'RAM': '2x DDR4 @ 3466 MHz', 'Release Year': '2018',
               'Audio Chip': 'Realtek ALC887', 'USB 2.0 Headers': None, 'USB 3.0 Headers': None, 'SATA3': '4'}
    TEST_MB = Motherboard(init_dict=TEST_MB)
    print(TEST_MB.socket, TEST_MB.all_specs)
