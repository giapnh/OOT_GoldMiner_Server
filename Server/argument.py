# -*- coding: utf-8 -*-
__author__ = 'Nguyen Huu Giap'
from struct import *


class Argument:
    #region Fields and Constants
    LONG = 8
    INT = 4
    SHORT = 2
    BYTE = 1
    STRING = 10
    RAW = 11

    type = 0
    number_value = 0
    string_value = ""
    byte_value = bytes()

    def __init__(self, _type, value):
        """

        @param _type: Data type
        """
        if _type is not None:
            self.type = _type
            if value is not None:
                if self.type == self.BYTE or self.type == self.SHORT or self.type == self.INT or self.type == self.LONG:
                    self.number_value = value
                elif self.type == self.STRING:
                    self.string_value = value
                else:
                    self.byte_value = value
        pass

    def get_log(self):
            s = ""
            if self.type == self.SHORT:
                s += "short: " + self.number_value
            elif self.type == self.INT:
                s += "int: " + self.number_value
            elif self.type == self.STRING:
                s += "String: " + self.string_value
            elif self.type == self.RAW:
                s += "Raw: " + len(self.byte_value)
            elif self.type == self.BYTE:
                s += "Byte: " + self.number_value
            elif self.type == self.LONG:
                s += "Long: " + self.number_value
            return s

    def to_string(self):
        if self.type == self.STRING:
            return self.string_value
        if self.type == self.RAW:
            try:
                s = self.byte_value.decode('utf-8')
                return s
            except Exception:
                return "ex"
        else:
            return self.number_value

    def get_argument_as_string(self, code):
        for a in dir(self):
            if a.startswith("ARG_"):
                if getattr(self, a) == code:
                    return a
        return "ArgName"

    ARG_CODE = 0
    ARG_OS = 1
    ARG_OS_VERSION = 2

    ARG_TYPE = 9
    ARG_COUNT = 10

    ARG_MESSAGE = 10
    ARG_PLAYER_USERNAME = 20
    ARG_PLAYER_PASSWORD = 21
    ARG_PLAYER_BIRTHDAY = 22
    ARG_PLAYER_EMAIL = 23
    ARG_PLAYER_LEVEL = 24
    ARG_PLAYER_LEVEL_UP_POINT = 25
    ARG_PLAYER_LEVEL_UP_REQUIRE = 26
    ARG_PLAYER_CUP = 27
    ARG_PLAYER_SPEED_MOVE = 30
    ARG_PLAYER_SPEED_DROP = 31
    ARG_PLAYER_SPEED_DRAG = 32

    ARG_ROOM_ID = 100
    ARG_CUP_WIN = 101
    ARG_CUP_LOST = 102

    ARG_MAP_ID = 120

    "On game"
    ARG_MOVE_FROM = 130
    ARG_MOVE_TO = 131

    ARG_DROP_ANGLE_X = 135
    ARG_DROP_ANGLE_Y = 136