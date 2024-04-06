import datetime
from dataclasses import dataclass, field


@dataclass  # I might want to use 'frozen=True'
class CPU:
    all_specs: dict = field(init=True, repr=False)

    human_name: str = field(init=False)
    codename: str = field(init=False, repr=False)
    cores: int = field(init=False, repr=False)
    threads: int = field(init=False)
    clock_speed_range_GHz: dict[str, float] = field(init=False, repr=False)
    socket: str = field(init=False)
    process_size_nm: int = field(init=False, repr=False)
    l3_cache_mb: int = field(init=False, repr=False)
    tdp_w: int = field(init=False)
    release_year: int = field(init=False, repr=False, default=0)
    further_link: str = field(init=False, repr=False, default='')
    exists: bool = field(init=False, repr=False, default=True)

    def __post_init__(self):
        from techpowerup import get_cpu_socket
        self.socket = get_cpu_socket(self.all_specs)
        self.convert_name_and_codename()
        self.split_cores_and_threads()
        self.convert_clock_speed()
        self.convert_process_size()
        self.convert_l3_cache()
        self.convert_tdp()
        self.convert_d_o_r()
        self.convert_link()


    # TODO: might as well just write down default values as field property
    def split_key_with_checks(self, key: str, split_by: str = ' ') -> list:
        if key not in self.all_specs:
            return None
        string_value = self.all_specs[key]
        if string_value in [None, 'N/A', 'Unknown', '']:
            return None
        return self.all_specs[key].split(split_by)

    def convert_name_and_codename(self) -> None:
        if self.split_key_with_checks('Name') is None:
            raise ValueError("A CPU should have a name!")
        # TODO: handle issues of value being equal to '' (empty string)
        self.human_name = self.all_specs['Name']
        if self.split_key_with_checks('Codename') is None:
            self.codename = "No codename"
            return
        self.codename = self.all_specs['Codename']
        return

    def split_cores_and_threads(self) -> None:
        initial_string: str = self.all_specs['Cores']
        if ' / ' in initial_string:
            self.cores, self.threads = map(int, initial_string.split(' / '))
            return
        try:
            self.cores = self.threads = int(initial_string.strip())
        except Exception as e:  # TODO: write proper exception handling
            print(e)

    def convert_clock_speed(self) -> None:
        temp_list = self.split_key_with_checks('Clock')
        if temp_list is None:
            self.clock_speed_range_GHz = {'min': 0.0, 'max': 0.0}

        speed_unit = temp_list[-1]
        if speed_unit != 'GHz':
            raise NotImplementedError(f"The clock speed is not in GHz, it is instead {speed_unit}")

        if len(temp_list) < 3 or temp_list[1] != 'to':
            self.clock_speed_range_GHz = {'min': float(temp_list[0]), 'max': float(temp_list[0])}
            return

        self.clock_speed_range_GHz = {'min': float(temp_list[0]), 'max': float(temp_list[2])}
        return

    def convert_l3_cache(self) -> None:
        temp_list = self.split_key_with_checks('L3 Cache')
        if temp_list is None:
            self.l3_cache_mb = 0
            return
        elif len(temp_list) != 2:
            raise IndexError(
                f"Value for l3 cache should contain exactly two words\nreceived {temp_list} of len {len(temp_list)}")
        elif temp_list[-1] != 'MB':
            raise NotImplementedError(f"For now, the program can only take values in MB, not in {temp_list[-1]}")

        self.l3_cache_mb = int(temp_list[0])
        return

    def convert_process_size(self) -> None:
        temp_list = self.split_key_with_checks('Process')
        if temp_list is None:
            self.process_size_nm = 0
        elif len(temp_list) != 2:
            raise IndexError(f"Process size should be 2 words, not {temp_list} with len {len(temp_list)}")
        elif temp_list[-1] != 'nm':
            raise NotImplementedError(f"The program can't convert {temp_list[-1]} into nm")

        self.process_size_nm = temp_list[0]
        return

    def convert_tdp(self):
        temp_list = self.split_key_with_checks('TDP')
        if temp_list is None:
            raise ValueError(f"A processor should have TDP\nall specs: {self.all_specs}")
        elif len(temp_list) != 2:
            raise IndexError(f"TDP should be 2 words, not {temp_list} of length {len(temp_list)}")
        elif temp_list[-1].lower() != 'w':
            raise ValueError(f"TDP should be measured in W, not in {temp_list[-1]}")
        self.tdp_w = int(temp_list[0])

    def convert_d_o_r(self) -> None:
        if 'Released' not in self.all_specs.keys():
            return
        if self.all_specs['Released'] in ['Unknown', 'N/A', None, 'None']:
            self.release_year = 0
            return
        elif self.all_specs['Released'] == 'Never Released':
            self.exists = False
            self.release_year = -1
            return
        self.release_year = int(self.all_specs['Released'].split()[-1])

    def convert_link(self) -> None:
        self.further_link = self.all_specs.get('Link', '')


if __name__ == '__main__':
    TEST_CPU = {'Name': 'A10-7870K', 'Codename': 'Godaveri', 'Cores': '4', 'Clock': '3.9 to 4.1 GHz',
                'Socket': 'Socket FM2+', 'Process': '28 nm', 'L3 Cache': 'N/A', 'TDP': '95 W',
                'Released': 'May 28th, 2015'}

    TEST_CPU = CPU(all_specs=TEST_CPU)
    print(TEST_CPU)
