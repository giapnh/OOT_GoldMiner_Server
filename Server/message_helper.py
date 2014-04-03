__author__ = 'Nguyen Huu Giap'
import socket
from struct import *
import hashlib
from command import Command
from argument import Argument


def gen_msg_register(username="", password=""):
    msg = Command(Command.CMD_REGISTER)
    msg.add_string(Argument.ARG_PLAYER_USERNAME, username)
    msg.add_string(Argument.ARG_PLAYER_PASSWORD, password)
    return msg


def gen_msg_login(username="", password=""):
    msg = Command(Command.CMD_LOGIN)
    msg.add_string(Argument.ARG_PLAYER_USERNAME, username)
    msg.add_string(Argument.ARG_PLAYER_PASSWORD, password)
    return msg


def gen_msg_player_info(info={}):
    msg = Command(Command.CMD_PLAYER_INFO)
    # msg.add_string(Argument.ARG_PLAYER_USERNAME, int(info["username"]))
    return msg


def gen_msg_join(username=""):
    msg = Command(Command.CMD_GAME_MATCHING)
    msg.add_string(Argument.ARG_PLAYER_USERNAME, username)
    return msg


def gen_msg_room_exit():
    msg = Command(Command.CMD_ROOM_EXIT)
    return msg