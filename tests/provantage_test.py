class MismatchError(Exception):
    def __init__(self, message: str = None):
        self.__message = message or "No error message was provided"
        super().__init__(self.__message)

def check_for_new_manufacturers() -> None:
    raise NotImplementedError()
    import json
    import os
    from provantage_ram import RAMManufacturer

    root_dir, current_dir = os.path.split(os.path.abspath(os.path.curdir))
    with open(os.path.join(root_dir, 'all_jsons/provantage_manufacturers.json'), 'r') as db_file:
        stored_manufacturers = json.load(db_file)

    received_manufacturers = RAMManufacturer.fetch_all_as_dictionary(with_update=False)

    if stored_manufacturers != received_manufacturers:
        raise MismatchError("The list of manufacturers from the database doesn't match the fetched results")

def parse_link_into_dict(link: str) -> dict[str, str]:
    raise NotImplementedError()
    from provantage_ram import BASE_URL
    if link.find(BASE_URL) != 0:
        raise ValueError(f"The link should start with BASE URL: {BASE_URL}\n{link} received instead")

    link = link.replace(BASE_URL, '')
    if len(link) == 0:
        return {}

    stage_1 = {}
    for pair in link[1:].split('&'):
        name, value = pair.split('=')
        stage_1.update({name: value})

    stage_2 = {}
    if 'MAN' in stage_1:
        stage_2.update({'MAN': stage_1.pop('MAN')})

    highest_count = 0
    for key, value in stage_1.items():
        if key[0] in ['V', 'A']:
            i = int(key[1:])
            if i > highest_count:
                highest_count = i
    for i in range(1, highest_count+1):
        stage_2.update({stage_1.pop(f'A{i}'): stage_1.pop(f'V{i}')})

    return stage_2

def test_generate_link() -> None:
    raise NotImplementedError
    from provantage_ram import generate_link
    test_cases = [
        [{"ddr_type": "DDR4 SDRAM", "size": "16 GB", "manufacturer": "AddOn", "speed": "2666 MHz"},
         "https://www.provantage.com/service/searchsvcs/B-CRAMM?MAN=ACPM&A1=31100&V1=RAM+Module&A2=31113713&V2=DDR4+SDRAM&A3=3113035&V3=16+GB&A4=311971&V4=2666+MHz"]
    ]
    for params, expected_link in test_cases:
        received_link = generate_link(parameters=params)
        expected_dict = parse_link_into_dict(expected_link)
        received_dict = parse_link_into_dict(received_link)
        if expected_dict != received_dict:
            raise MismatchError(f"Unexpected link from generate_link():\n{received_link} instead of\n{expected_link}")


tests: list[callable] = [
    check_for_new_manufacturers,
    test_generate_link]

if __name__ == '__main__':
    for test in tests:
        test()
    else:
        print("All tests passed successfully! Congrats!")
