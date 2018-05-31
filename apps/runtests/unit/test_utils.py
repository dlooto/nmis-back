#!/usr/bin/env python
# encoding: utf-8
import unittest
from utils import eggs


def test_list_include():
    a = [1, 2]
    b = [1, 2, 3]
    assert eggs.included_in(a, b)

    a = [1, 2, 4]
    b = [1, 2, 3]
    assert not eggs.included_in(a, b)

    l1 = [('name', 'junn'), ('pwd', 111)]
    l2 = [('name', 'junn'), ('pwd', 111), ('email', 'test@test.com')]
    assert eggs.included_in(l1, l2)

def is_include(a, b):
    """ 是否list a包括list b """
    return set(a).intersection(set(b)) == set(a)


def incr_month_day(year, month, day):
    return None

def expired_on(year, month, day):
    tmp = month + 1
    if tmp > 12:
        return (year + 1, 1, incr_month_day(year+1, 1, day) )

    return (year, tmp, incr_month_day(year, tmp, day) )
