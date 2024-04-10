def test_cpu_fetching() -> None:
    from techpowerup import get_component_list
    gpu_list = get_component_list('GPU', params={
        'mfgr': 'NVIDIA',
        'mobile': 'No',
        'workstation': 'No',
        'released': '2005'
    })
    for gpu in gpu_list:
        print(gpu)

if __name__ == '__main__':
    test_cpu_fetching()
