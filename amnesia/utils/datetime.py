# -*- coding: utf-8 -*-


def itermonths(starts, count):
    backward = count < 0

    year = starts.year
    month = starts.month

    for _ in range(abs(count)):
        if backward:
            if month == 1:
                month = 13
                year -= 1

            month -= 1
        else:
            if month == 12:
                month = 0
                year += 1

            month += 1

        yield (year, month)
