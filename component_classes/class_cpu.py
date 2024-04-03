from dataclasses import dataclass, field
@dataclass
class CPU:
    all_specs: dict= field(init=True, repr=False)

    human_name: str = field(init=False)
    codename: str = field(init=False, repr=False)
    cores: int = field(init=False)
    threads: int = field(init=False)
    clock_speed_GHz: float = field(init=False)
    socket: str = field(init=False)
    process_size_nm: int = field(init=False, repr=False)
    l3_cache_mb: int = field(init=False, repr=False)
    date_of_release: str = field(init=False, repr=False)

    def __post_init__(self):
        self.all_specs = self.all_specs.copy()
        from techpowerup import get_cpu_socket
        self.socket = get_cpu_socket(self.all_specs)
        try:
            self.human_name = self.all_specs['Name']
            self.codename = self.all_specs['Codename']
            self.split_cores_and_threads()
            self.clock_speed_GHz = self.all_specs['Clock']  # TODO: convert into float
            self.process_size_nm = self.all_specs['Process']  # TODO: convert into int nm
            self.l3_cache_mb = self.all_specs['L3 Cache']  # TODO: convert into int mb
            self.date_of_release = self.all_specs['Released']  # TODO: convert into datetime (for fun)
        except Exception as e:  # TODO: write proper exception handling
            print(e)

        del self.all_specs

    def split_cores_and_threads(self) -> None:
        initial_string: str = self.all_specs['Cores']
        if ' / ' in initial_string:
            self.cores, self.threads = map(int, initial_string.split(' / '))
            return
        try:
            self.cores = self.threads = int(initial_string.strip())
        except Exception as e:  # TODO: write proper exception handling
            print(e)




if __name__ == '__main__':
    TEST_CPU = {'Name': 'A10-7870K', 'Codename': 'Godaveri', 'Cores': '4', 'Clock': '3.9 to 4.1 GHz',
                'Socket': 'Socket FM2+', 'Process': '28 nm', 'L3 Cache': 'N/A', 'TDP': '95 W',
                'Released': 'May 28th, 2015'}

    TEST_CPU = CPU(all_specs=TEST_CPU)
    print(TEST_CPU)
