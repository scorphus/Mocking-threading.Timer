#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of pabloaguiar.me/post/karen-on-python-mocks-threading-timer

# Licensed under the BSD-3-Clause license:
# https://opensource.org/licenses/BSD-3-Clause
# Copyright (c) 2019-2020, Pablo S. Blum de Aguiar <scorphus@gmail.com>

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
    function decorator, but specifically for threading.Timer. The function
    passed to threading.Timer is called right away with all given arguments.

    :arg str target_timer: the target Timer (threading.Timer) to be patched
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            def side_effect(interval, function, args=None, kwargs=None):
                args = args if args is not None else []
                kwargs = kwargs if kwargs is not None else {}
                # Call whatever would be called when interval is reached
                function(*args, **kwargs)
                # Return a mock object to allow function calls on the
                # returned value
                return Mock()

            with patch(target_timer, side_effect=side_effect) as timer_mock:
                # Pass the mock object to the decorated function for further
                # assertions
                return f(*(*args, timer_mock), **kwargs)

        return wrapper

    return decorator


class HellotimerTestCase(unittest.TestCase):
    def setUp(self):
        hello_patcher = patch("hellotimer.hello")
        self.hello_mock = hello_patcher.start()
        self.addCleanup(hello_patcher.stop)

    def test_set_timer_with_sleep(self):
        hellotimer.set_timer("Neo")
        time.sleep(1)
        self.hello_mock.assert_called_once_with("Neo")

    def test_set_timer_with_patch(self):
        def side_effect(interval, function, args=None, kwargs=None):
            args = args if args is not None else []
            kwargs = kwargs if kwargs is not None else {}
            function(*args, **kwargs)
            return Mock()

        with patch("hellotimer.Timer", side_effect=side_effect) as timer_mock:
            hellotimer.set_timer("Neo")
            self.hello_mock.assert_called_once_with("Neo")
            timer_mock.assert_called_once_with(1.0, hellotimer.hello, ["Neo"])

    @patch_hellotimer_timer
    def test_set_timer_with_decorator_intermediate(self, timer_mock):
        hellotimer.set_timer("Neo")
        self.hello_mock.assert_called_once_with("Neo")
        timer_mock.assert_called_once_with(1.0, hellotimer.hello, ["Neo"])

    @patch_threading_timer("hellotimer.Timer")
    def test_set_timer_with_decorator_final(self, timer_mock):
        hellotimer.set_timer("Neo")
        self.hello_mock.assert_called_once_with("Neo")
        timer_mock.assert_called_once_with(1.0, hellotimer.hello, ["Neo"])
