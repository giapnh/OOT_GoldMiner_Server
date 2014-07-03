# -*- coding: utf-8 -*-
from ctypes import c_ushort
from argument import Argument
from struct import *
__author__ = 'Nguyen Huu Giap'
"""
<@author Steve Giap
"""


class Command:
    code = 0
    #Command code
    CMD_INVALID = -1
    CMD_REGISTER = 1
    CMD_LOGIN = 2
    CMD_PLAYER_INFO = 3

    CMD_DISCONNECT = 4
    CMD_LOGOUT = 5

    CMD_LIST_FRIEND = 10
    CMD_ADD_FRIEND = 11
    CMD_ACCEPT_FRIEND = 12
    CMD_REMOVE_FRIEND = 13
    CMD_PLAYER_CHAT = 20

    CMD_FRIEND_INFO = 30

    CMD_GAME_MATCHING = 100
    CMD_GAME_MATCHING_CANCEL = 101

    CMD_ROOM_INFO = 102
    CMD_ROOM_EXIT = 105

    CMD_GAME_READY = 110
    CMD_GAME_START = 111

    CMD_MAP_INFO = 120

    "On game"
    CMD_PLAYER_MOVE = 130
    CMD_PLAYER_DROP = 131
    CMD_PLAYER_DROP_RESULT = 132

    CMD_PLAYER_TURN_TIME_OUT = 140
    CMD_PLAYER_TURN = 141

    CMD_ADD_SCORE = 150

    CMD_GAME_FINISH = 160
    CMD_PLAYER_GAME_RESULT = 161

    def __init__(self, code):
        self.args = {}
        self.code = code

    #Add argument
    def add_argument(self, arg_code, arg):
        self.args[arg_code] = arg
        return self

    def add_byte(self, arg_code=0, long_val=int()):
        self.add_argument(arg_code, Argument(Argument.BYTE, long_val))
        return self

    def add_short(self, arg_code=0, long_val=c_ushort()):
        self.add_argument(arg_code, Argument(Argument.SHORT, long_val))
        return self

    def add_int(self, arg_code=0, long_val=int()):
        self.add_argument(arg_code, Argument(Argument.INT, long_val))
        return self

    def add_long(self, arg_code=0, long_val=long()):
        self.add_argument(arg_code, Argument(Argument.LONG, long_val))
        return self

    def add_string(self, arg_code=0, str_val=str()):
        self.add_argument(arg_code, Argument(Argument.STRING, str_val))
        return self

    def add_raw(self, arg_code=0, raw_val=bytes()):
        self.add_argument(arg_code, Argument(Argument.RAW, raw_val))
        return self

    def get_string(self, code=0, default=""):
        if self.args.__contains__(code):
            arg = self.args[code]
            if None != arg:
                return arg.to_string()
        return default

    def get_int(self, code, default=0):
        arg = self.args[code]
        if None != arg:
            return int(arg.number_value)
        return int(default)

    def get_short(self, code, default=0):
        arg = self.args[code]
        if None != arg:
            return c_ushort(arg.number_value)
        return c_ushort(default)

    def get_long(self, code, default=0):
        arg = self.args[code]
        if None != arg:
            return arg.number_value
        return long(default)

    def get_boolean(self, code, default=False):
        arg = self.args[code]
        if None != arg:
            return arg.number_value != 0
        return default

    def get_command_name(self, code):
        for a in dir(self):
            if a.startswith("CMD_"):
                if getattr(self,a) == code:
                    return a
        return "CmdName"

    def get_log(self):
        s = "Command: " + self.get_command_name(self.code) + "[" + str(self.code) + "]\n"
        keys = self.args.keys()
        for key in keys:
            arg = self.args[key]
            s += "    " + arg.get_argument_as_string(key) + "[" + str(key) + "]" + str(arg.to_string()) + "\n"
        s += "\n"
        return s

    def get_bytes(self):
        #Size
        cmd_len = 0
        #command code
        cmd_len += 2
        #number of argument
        cmd_len += 2
        keys = self.args.keys()
        for key in keys:
            arg = self.args[key]
            #argument code
            cmd_len += 2
            #argument data type
            cmd_len += 1
            arg_type = arg.type
            if arg_type == Argument.STRING:
                #string data length
                cmd_len += 4
                cmd_len += len(unicode(str(arg.string_value), 'utf8'))
            elif arg_type == Argument.RAW:
                cmd_len += 4
                cmd_len += len(arg.byte_value)
            else:
                cmd_len += int(arg_type)
        #Buffer
        buff = bytearray(cmd_len)
        offset = 0
        pack_into("<H", buff, 0, self.code)
        offset += 2
        pack_into("<H", buff, offset, len(self.args))
        offset += 2
        keys = self.args.keys()
        for key in keys:
            arg = self.args[key]
            pack_into("<H", buff, offset, key)
            offset += 2
            pack_into("<B", buff, offset, arg.type)
            offset += 1
            if arg.type == Argument.BYTE:
                pack_into("<B", buff, offset, arg.number_value)
                offset += 1
            elif arg.type == Argument.SHORT:
                pack_into("<H", buff, offset, arg.number_value)
                offset += 2
            elif arg.type == Argument.INT:
                pack_into("<i", buff, offset, arg.number_value)
                offset += 4
            elif arg.type == Argument.LONG:
                pack_into("<L", buff, offset, arg.number_value)
                offset += 8
            elif arg.type == Argument.STRING:
                str_len = len(unicode(str(arg.string_value), 'utf8'))
                pack_into("<I", buff, offset, str_len)
                offset += 4
                pack_into(str(str_len)+"s", buff, offset, str(arg.string_value))
                offset += str_len
            else:
                raw_len = len(arg.byte_value)
                buff[offset:offset+raw_len] = arg.byte_value
        return buff