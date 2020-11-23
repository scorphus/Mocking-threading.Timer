#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of https://github.com/scorphus/Mocking-threading.Timer

# Licensed under the BSD-3-Clause license:
# https://opensource.org/licenses/BSD-3-Clause
# Copyright (c) 2019-2020, Pablo S. Blum de Aguiar <scorphus@gmail.com>

from threading import Timer


def hello(name):
    print(f"Hello, {name}!")


def set_timer(name):
    timer = Timer(1.0, hello, [name])
    timer.start()
    timer.join()
