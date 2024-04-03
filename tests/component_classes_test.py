def test_CPU_class() -> None:
    from component_classes.class_cpu import CPU
    test_cases = [
        {'Name': 'A10-7870K', 'Codename': 'Godaveri', 'Cores': '4', 'Clock': '3.9 to 4.1 GHz',
         'Socket': 'Socket FM2+', 'Process': '28 nm', 'L3 Cache': 'N/A', 'TDP': '95 W',
         'Released': 'May 28th, 2015'},
        {'Name': 'A10-7870K', 'Codename': 'Godaveri', 'Cores': '4 / 8', 'Clock': '3.9 to 4.1 GHz',
         'Socket': 'Socket FM2+', 'Process': '28 nm', 'L3 Cache': 'N/A', 'TDP': '95 W',
         'Released': 'May 28th, 2015'}
    ]
    for case in test_cases:
        i_cpu = CPU(case)
