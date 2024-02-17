from class_database import db

TEST_CPU = db.get_cpu_list(params={"mfgr": 'AMD',
                                   "released": '2015',
                                   "mobile": 'No',
                                   "server": 'No',
                                   "multiUnlocked": 'Yes'})[0]
TEST_MB = db.get_mb_list(params={'manufacturer': 'Asus',
                                 'form_factor': 'Micro-ATX',
                                 'socket': 'AM4',
                                 'chipset': 'AMD B450',
                                 })[0]


def check_sockets(motherboard: dict, cpu: dict) -> bool:
    from motherboarddbcom import get_mb_socket
    mb_socket = get_mb_socket(motherboard)

    from techpowerup import get_cpu_socket
    cpu_socket = get_cpu_socket(cpu)

    return cpu_socket == mb_socket


if __name__ == '__main__':
    print(TEST_CPU)
    print(TEST_MB)
    print(check_sockets(motherboard=TEST_MB, cpu=TEST_CPU))
