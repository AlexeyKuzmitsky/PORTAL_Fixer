from typing import Callable, Any
from datetime import datetime
import functools


def timer(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapped_func(*args, **kwargs) -> Any:
        start_func = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        run = end - start_func
        milliseconds = str(round(run.microseconds / 1000))
        milliseconds = f'{(3-len(milliseconds))*"0"}{milliseconds}'
        print(f'Программа завершена. Время выполнения: {run.seconds}.{milliseconds} сек.')
        # print('\n')
        return result
    return wrapped_func
