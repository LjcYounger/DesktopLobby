from typing import Literal

def counter(amount, n0=0):
    n = n0

    def count(type: Literal['last', 'next', 'get']):
        nonlocal n
        if type == 'last':
            n -= 1
        elif type == 'next':
            n += 1
        return n % amount
    return count