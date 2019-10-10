from librfunc import (
    LocalsCatcher
)


if __name__ == "__main__":
    lc = LocalsCatcher()

    a = 1

    with lc:
        b = a

        lc2 = LocalsCatcher()

        with lc2.steal:
            d = 4

        lc3 = LocalsCatcher()

        with lc3.nosteal:
            g = 8

        f = 6

    print(lc)
