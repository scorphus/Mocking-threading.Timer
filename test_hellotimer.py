#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of https://pabloaguiar.me/post/mocking-threading-timer/

# Licensed under the BSD-3-Clause license:
# https://opensource.org/licenses/BSD-3-Clause
# Copyright (c) 2019, Pablo S. Blum de Aguiar <scorphus@gmail.com>

import time
import unittest
from functools import wraps
from unittest.mock import Mock, patch

import hellotimer


def patch_hellotimer_timer(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        def side_effect(interval, function, args=None, kwargs=None):
            args = args if args is not None else []
            kwargs = kwargs if kwargs is not None else {}
            function(*args, **kwargs)
            return Mock()

        with patch("hellotimer.Timer", side_effect=side_effect) as timer_mock:
            return f(*(*args, timer_mock), **kwargs)

    return wrapper


def patch_threading_timer(target_timer):
    """patch_threading_timer acts similarly to unittest.mock.patch as a
    function decorator, but specific for threading.Timer. The function passed to
    threading.Timer is called right away with all given arguments.

    :arg str target_timer: the target Timer (threading.Timer) to be patched
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            def side_effect(interval, function, args=None, kwargs=None):
                args = args if args is not None else []
                kwargs = kwargs if kwargs is not None else {}
                # Call whatever is called when interval is reached
                function(*args, **kwargs)
                # Return a mock object to allow function calls on whatever is
                # returned by Timer
                return Mock()

            # Mock target_timer in a context, redefine both its behavior and
            # return value
            with patch(target_timer, side_effect=side_effect) as timer_mock:
                # Pass the mock object to the decorated function
                return f(*(*args, timer_mock), **kwargs)

        return wrapper

    return decorator


class HellotimerTestCase(unittest.TestCase):
    @patch("hellotimer.hello")
    def test_set_timer_with_sleep(self, hello_mock):
        hellotimer.set_timer("Neo")
        time.sleep(1)
        hello_mock.assert_called_once_with("Neo")

    @patch("hellotimer.hello")
    def test_set_timer_with_patch(self, hello_mock):
        def side_effect(interval, function, args=None, kwargs=None):
            args = args if args is not None else []
            kwargs = kwargs if kwargs is not None else {}
            function(*args, **kwargs)
            return Mock()

        with patch("hellotimer.Timer", side_effect=side_effect) as timer_mock:
            hellotimer.set_timer("Neo")
            timer_mock.assert_called_once_with(1.0, hellotimer.hello, ["Neo"])
            hello_mock.assert_called_once_with("Neo")

    @patch_hellotimer_timer
    @patch("hellotimer.hello")
    def test_set_timer_with_decorator_intermediate(self, timer_mock, hello_mock):
        hellotimer.set_timer("Neo")
        timer_mock.assert_called_once_with(1.0, hellotimer.hello, ["Neo"])
        hello_mock.assert_called_once_with("Neo")

    @patch_threading_timer("hellotimer.Timer")
    @patch("hellotimer.hello")
    def test_set_timer_with_decorator_final(self, timer_mock, hello_mock):
        hellotimer.set_timer("Neo")
        timer_mock.assert_called_once_with(1.0, hellotimer.hello, ["Neo"])
        hello_mock.assert_called_once_with("Neo")