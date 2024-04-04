def test_CPU_class() -> None:
    from component_classes.class_cpu import CPU
    test_cases = [
        {'Name': 'A10-7870K', 'Codename': 'Godaveri', 'Cores': '4', 'Clock': '3.9 to 4.1 GHz',
         'Socket': 'Socket FM2+', 'Process': '28 nm', 'L3 Cache': 'N/A', 'TDP': '95 W',
         'Released': 'May 28th, 2015'},
        {'Name': 'A10-7870K', 'Cores': '4 / 8', 'Clock': '3.9 GHz',
         'Socket': 'Socket FM2+', 'Process': '28 nm', 'L3 Cache': '3 MB', 'TDP': '95 W',
         'Released': 'May 28th, 2015'},
        {'Name': 'Ryzen 3 4100', 'Codename': 'Renoir', 'Cores': '4 / 8', 'Clock': '3.8 to 4 GHz',
         'Socket': 'Socket AM4', 'Process': '7 nm', 'L3 Cache': '8 MB', 'TDP': '65 W', 'Released': 'Apr 4th, 2022'}
    ]
    for case in test_cases:
        i_cpu = CPU(case)
        print(i_cpu)
    else:
        print("All tests passed successfully")


def test_GPU_class() -> None:
    from component_classes.class_gpu import GPU
    test_cases = [
        {'Product Name': 'GeForce RTX 4050', 'GPU Chip': 'AD107', 'Released': 'Unknown', 'Bus': 'PCIe 4.0 x8',
         'Memory': '6 GB, GDDR6, 96 bit', 'GPU clock': '2505 MHz', 'Memory clock': '2250 MHz',
         'Shaders / TMUs / ROPs': '2560 / 80 / 32'},
        {'Product Name': 'GeForce RTX 4060', 'GPU Chip': 'AD107', 'Released': 'May 18th, 2023', 'Bus': 'PCIe 4.0 x8',
         'Memory': '8 GB, GDDR6, 128 bit', 'GPU clock': '1830 MHz', 'Memory clock': '2125 MHz',
         'Shaders / TMUs / ROPs': '3072 / 96 / 48'}
    ]
    for case in test_cases:
        i_GPU = GPU(case)
        print(i_GPU)


def run_all_tests() -> None:
    for run_test in [test_CPU_class, test_GPU_class]:
        run_test()
    print('All tests passed successfully')


if __name__ == '__main__':
    # test_CPU_class()
    test_GPU_class()
    # run_all_tests()
