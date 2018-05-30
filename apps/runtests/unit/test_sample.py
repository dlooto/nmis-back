# encoding: utf-8
#
# Created by junn, on 16/12/20
#

"""

"""

import logging
import pytest
from django.contrib.auth import get_user_model

from users.models import User


def func(x):
    return x + 1

def test_func():
    assert func(3) == 4


class TestClass():
    def test_one(self):
        x = "this"
        assert 'h' in x

    def test_two(self):
        x = "hello"
        assert not hasattr(x, 'check')

# @pytest.mark.django_db
# def test_get_organ():
#     organ_id = 1
#     organ = Organ.objects.get(id=organ_id)
#     assert organ.id+1 == organ_id+1

# @pytest.mark.django_db
# def test_get_user():
#     email = u'xiongjun@juyanggroup.com'
#     user = get_user_model().objects.get(email=email)
#     assert user.email == email
#
#



