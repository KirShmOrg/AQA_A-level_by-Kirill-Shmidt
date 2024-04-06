from time import sleep
from requests import get, Response

def request_get_v2(link: str, sleep_time: int = 0.5) -> Response:
    sleep(sleep_time)
    response = get(link)
    if response.status_code == 429:
        print(f'Too many requests for {link}. Sleeping for {sleep_time*2}')
        return request_get_v2(link, sleep_time * 2)
    return get(link)