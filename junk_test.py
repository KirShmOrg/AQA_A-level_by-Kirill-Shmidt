from time import perf_counter, sleep


def measure_time(func_to_test, *args, **kwargs):
    def wrapper():
        start_time = perf_counter()
        func_to_test()
        end_time = perf_counter()
        print(f"{func_to_test.__name__} took {end_time - start_time} seconds")
    return wrapper


@measure_time
def test_function():
    n = 10
    for i in range(n):
        sleep(0.1)


if __name__ == '__main__':
    test_function()
