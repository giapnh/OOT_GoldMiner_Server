# -*- coding: utf-8 -*-
from smtpd import usage
from turtle import _Root
from database.dbmanager import DBManager
from help import log
import message_helper

__author__ = 'Nguyen Huu Giap'
from command import Command
from argument import Argument
from struct import *
import random
import thread
import socket
import select
import Message
import time
from room_info import RoomInfo

"""
@author: giapnh
"""

# HOST, PORT, RECV_BUFFER = "192.168.100.40", 5555, 4096
HOST, PORT, RECV_BUFFER = "182.48.50.239", 5555, 4096
data = None
reading = True
"""Connection List"""
connection_list = []
waiting_list = []
playing_list = []
"Room list"
room_list = {}
"""List player loged in"""
name_sock_map = {}
sock_name_map = {}


def read(sock, data):
    try:
        """
        Analysis command
        @param sock the socket of client
        @param data the read data
        """
        read_count = 0
        code = int(unpack("<H", data[0:2])[0])
        read_count += 2
        cmd = Command(code)
        num_arg = int(unpack("<H", data[2:4])[0])
        read_count += 2
        for i in range(0, num_arg, 1):
            """Read all argument"""
            arg_code = int(unpack("<H", data[read_count:read_count + 2])[0])
            read_count += 2
            # Argument type
            arg_type = int(unpack("B", data[read_count:read_count + 1])[0])
            read_count += 1
            if arg_type == Argument.STRING:
                # string len
                str_len = int(unpack("<I", data[read_count:read_count + 4])[0])
                read_count += 4
                str_val = str(unpack(str(str_len) + "s", data[read_count:read_count + str_len])[0])
                read_count += str_len
                cmd.add_string(arg_code, str_val)
            elif arg_type == Argument.RAW:
                raw_len = int(unpack("<I", data[read_count:read_count + 4])[0])
                read_count += 4
                raw_data = data[read_count, read_count + raw_len]
                read_count += raw_len
                cmd.add_raw(arg_code, raw_data)
            elif arg_type == Argument.BYTE:
                byte_val = int(unpack("B", data[read_count:read_count + 1])[0])
                read_count += 1
                cmd.add_byte(arg_code, byte_val)
            elif arg_type == Argument.SHORT:
                short_val = int(unpack("<H", data[read_count:read_count + 2])[0])
                read_count += 2
                cmd.add_short(arg_code, short_val)
            elif arg_type == Argument.INT:
                int_val = int(unpack("<i", data[read_count:read_count + 4])[0])
                read_count += 4
                cmd.add_int(arg_code, int_val)
            elif arg_type == Argument.LONG:
                long_val = long(unpack("<L", data[read_count:read_count + 8])[0])
                read_count += 8
                cmd.add_long(arg_code, long_val)
        analysis_message(sock, cmd)
    except Exception:
        pass
    pass


def analysis_message(sock, cmd):
    """
    @param sock: client just sent message
    @param cmd: command
    @return: no return
    """
    log.log("<<<<<<Receive:   " + cmd.get_log())
    if cmd.code == Command.CMD_LOGIN:
        analysis_message_login(sock, cmd)
        pass
    elif cmd.code == Command.CMD_LOGOUT:
        analysis_message_logout(sock, cmd)
        pass
    elif cmd.code == Command.CMD_REGISTER:
        analysis_message_register(sock, cmd)
        pass
    elif cmd.code == Command.CMD_PLAYER_CHAT:
        analysis_message_chat(sock, cmd)
        pass
        """Friend Action"""
    elif cmd.code == Command.CMD_LIST_FRIEND:
        analysis_message_list_friend(sock, cmd)
        pass
    elif cmd.code == Command.CMD_FRIEND_INFO:
        analysis_message_friend_info(sock, cmd)
        pass
    elif cmd.code == Command.CMD_ADD_FRIEND:
        analysis_message_add_friend(sock, cmd)
        pass
    elif cmd.code == Command.CMD_ACCEPT_FRIEND:
        analysis_message_accept_friend(sock, cmd)
        pass
    elif cmd.code == Command.CMD_REMOVE_FRIEND:
        analysis_message_remove_friend(sock, cmd)
        pass
    elif cmd.code == Command.CMD_CANCEL_REQUEST:
        analysis_message_cancel_request(sock, cmd)
        pass
    elif cmd.code == Command.CMD_UPGRADE:
        analysis_message_upgrade(sock, cmd)
        pass
        """Game Action"""
    elif cmd.code == Command.CMD_GAME_MATCHING:
        analysis_message_game_join(sock, cmd)
        pass
    elif cmd.code == Command.CMD_GAME_MATCHING_CANCEL:
        analysis_message_game_join_cancel(sock, cmd)
        pass
    elif cmd.code == Command.CMD_ROOM_EXIT:
        analysis_message_room_exit(sock, cmd)
        pass
    elif cmd.code == Command.CMD_GAME_READY:
        analysis_message_game_ready(sock, cmd)
        pass
        """On Game Playing Action"""
    elif cmd.code == Command.CMD_PLAYER_MOVE:
        analysis_message_player_move(sock, cmd)
        pass
    elif cmd.code == Command.CMD_PLAYER_TURN_TIME_OUT:
        analysis_message_turn_timeout(sock, cmd)
        pass
    elif cmd.code == Command.CMD_PLAYER_DROP:
        analysis_message_player_drop(sock, cmd)
        pass
    elif cmd.code == Command.CMD_PLAYER_DROP_RESULT:
        analysis_message_player_drop_result(sock, cmd)
        pass
    elif cmd.code == Command.CMD_GAME_FINISH:
        analysis_message_game_finish(sock, cmd)
        pass
    elif cmd.code == Command.CMD_GAME_FORCE_FINISH:

        pass
    else:
        pass
    return cmd


def analysis_message_login(sock, cmd):
    """
    Login Message
    @param sock:
    @param cmd:
    @return:
    """
    if db.check_user_login(cmd.get_string(Argument.ARG_PLAYER_USERNAME),
                           cmd.get_string(Argument.ARG_PLAYER_PASSWORD)):
        if cmd.get_string(Argument.ARG_PLAYER_USERNAME) in name_sock_map.keys():
            # Send message disconnect to old client
            old_sock = name_sock_map[cmd.get_string(Argument.ARG_PLAYER_USERNAME)]
            disconnect_cmd = Command(Command.CMD_DISCONNECT)
            disconnect_cmd.add_int(Argument.ARG_CODE, 1)
            disconnect_cmd.add_string(Argument.ARG_MESSAGE, Message.MSG_DISCONNECT)
            send(old_sock, disconnect_cmd)
            # Send message login success to new client
            """Add player to list"""
            name_sock_map[cmd.get_string(Argument.ARG_PLAYER_USERNAME)] = sock
            sock_name_map[sock] = cmd.get_string(Argument.ARG_PLAYER_USERNAME)
            sock_name_map.pop(old_sock)
            send_cmd = Command(Command.CMD_LOGIN)
            send_cmd.add_int(Argument.ARG_CODE, 1)
            send(sock, send_cmd)
            """Send player info"""
            info = db.get_user_info(cmd.get_string(Argument.ARG_PLAYER_USERNAME))
            send_cmd = Command(Command.CMD_PLAYER_INFO)
            send_cmd.add_int(Argument.ARG_PLAYER_LEVEL, int(info["level"]))
            send_cmd.add_int(Argument.ARG_PLAYER_LEVEL_UP_POINT, int(info["levelup_point"]))
            send_cmd.add_int(Argument.ARG_PLAYER_CUP, int(info["cup"]))
            send_cmd.add_int(Argument.ARG_PLAYER_LEVEL_UP_REQUIRE, int(info["require_point"]))
            send_cmd.add_int(Argument.ARG_PLAYER_SPEED_MOVE, int(info["speed_move"]))
            send_cmd.add_int(Argument.ARG_PLAYER_SPEED_DROP, int(info["speed_drop"]))
            send_cmd.add_int(Argument.ARG_PLAYER_SPEED_DRAG, int(info["speed_drag"]))
            send(sock, send_cmd)
            remove_sock(old_sock)
            pass
        else:
            """Add player to list"""
            name_sock_map[cmd.get_string(Argument.ARG_PLAYER_USERNAME)] = sock
            sock_name_map[sock] = cmd.get_string(Argument.ARG_PLAYER_USERNAME)
            send_cmd = Command(Command.CMD_LOGIN)
            send_cmd.add_int(Argument.ARG_CODE, 1)
            send(sock, send_cmd)
            """Send player info"""
            info = db.get_user_info(cmd.get_string(Argument.ARG_PLAYER_USERNAME))
            send_cmd = Command(Command.CMD_PLAYER_INFO)
            send_cmd.add_int(Argument.ARG_PLAYER_LEVEL, int(info["level"]))
            send_cmd.add_int(Argument.ARG_PLAYER_LEVEL_UP_POINT, int(info["levelup_point"]))
            send_cmd.add_int(Argument.ARG_PLAYER_CUP, int(info["cup"]))
            send_cmd.add_int(Argument.ARG_PLAYER_LEVEL_UP_REQUIRE, int(info["require_point"]))
            send_cmd.add_int(Argument.ARG_PLAYER_SPEED_MOVE, int(info["speed_move"]))
            send_cmd.add_int(Argument.ARG_PLAYER_SPEED_DROP, int(info["speed_drop"]))
            send_cmd.add_int(Argument.ARG_PLAYER_SPEED_DRAG, int(info["speed_drag"]))
            send(sock, send_cmd)
    else:
        send_cmd = Command(Command.CMD_LOGIN)
        send_cmd.add_int(Argument.ARG_CODE, 0)
        send_cmd.add_string(Argument.ARG_MESSAGE, "Invalid login info, please check again or register first!")
        send(sock, send_cmd)
        pass
    return


def analysis_message_register(sock, cmd):
    """
    Register message
    @param sock:
    @param cmd:
    @return:
    """
    send_cmd = Command(Command.CMD_REGISTER)
    if db.check_user_exits(cmd.get_string(Argument.ARG_PLAYER_USERNAME)):
        send_cmd.add_int(Argument.ARG_CODE, 0)
    else:
        db.add_user(cmd.get_string(Argument.ARG_PLAYER_USERNAME), cmd.get_string(Argument.ARG_PLAYER_PASSWORD))
        send_cmd.add_int(Argument.ARG_CODE, 1)
    sock.sendall(send_cmd.get_bytes())
    return


def analysis_message_logout(sock, cmd):
    remove_sock(sock)
    pass


def analysis_message_chat(sock, cmd):
    """
    Chat message
    @param sock:
    @param cmd:
    @return:
    """
    from_user = sock_name_map[sock]
    to_user = cmd.get_string(Argument.ARG_PLAYER_USERNAME, "no name")
    message = cmd.get_string(Argument.ARG_MESSAGE, "no content")
    send_cmd = Command(Command.CMD_PLAYER_CHAT)
    send_cmd.add_string(Argument.ARG_PLAYER_USERNAME, from_user)
    send_cmd.add_string(Argument.ARG_MESSAGE, message)
    if check_player_online(to_user):
        send(name_sock_map[to_user], send_cmd)
        # name_sock_map[to_user].sendall(send_cmd.get_bytes())
    pass


def analysis_message_list_friend(sock, cmd):
    """
    Get list friend
    @param sock:
    @param cmd:
    @return:
    """
    limit = cmd.get_int(Argument.ARG_LIMIT, 0)
    offset = cmd.get_int(Argument.ARG_OFFSET, 0)
    list_friend = db.get_list_friend_mutual(cmd.get_string(Argument.ARG_PLAYER_USERNAME), limit, offset)
    for key in list_friend.keys():
        friend_info = Command(Command.CMD_FRIEND_INFO)
        friend_info.add_string(Argument.ARG_PLAYER_USERNAME, key)
        friend_info.add_int(Argument.ARG_PLAYER_LEVEL, int(list_friend[key]["level"]))
        friend_info.add_int(Argument.ARG_PLAYER_CUP, int(list_friend[key]["cup"]))
        # TODO
        send(sock, friend_info)
        pass
    pass


def analysis_message_friend_info(sock, cmd):
    info = db.get_user_info(cmd.get_string(Argument.ARG_PLAYER_USERNAME))
    if None != info:
        friend_info = Command(Command.CMD_FRIEND_INFO)
        friend_info.add_string(Argument.ARG_PLAYER_USERNAME, str(info["username"]))
        friend_info.add_int(Argument.ARG_PLAYER_LEVEL, int(info["level"]))
        friend_info.add_int(Argument.ARG_PLAYER_LEVEL_UP_POINT, int(info["levelup_point"]))
        friend_info.add_int(Argument.ARG_PLAYER_CUP, int(info["cup"]))
        friend_info.add_int(Argument.ARG_PLAYER_LEVEL_UP_REQUIRE, int(info["require_point"]))
        friend_info.add_int(Argument.ARG_PLAYER_SPEED_MOVE, int(info["speed_move"]))
        friend_info.add_int(Argument.ARG_PLAYER_SPEED_DRAG, int(info["speed_drag"]))
        friend_info.add_int(Argument.ARG_PLAYER_SPEED_DROP, int(info["speed_drop"]))
        friend_info.add_int(Argument.ARG_FRIEND_TYPE,
                           db.get_friend_type(sock_name_map.get(sock),cmd.get_string(Argument.ARG_PLAYER_USERNAME)))
        send(sock, friend_info)
        pass
    pass

def analysis_message_add_friend(sock, cmd):
    """
    Add friend message
    @param sock:
    @param cmd:
    @return:
    """
    if db.add_friend(sock_name_map.get(sock), cmd.get_string(Argument.ARG_PLAYER_USERNAME)):
        send_cmd = Command(Command.CMD_ADD_FRIEND)
        send_cmd.add_int(Argument.ARG_CODE, 1)
        send_cmd.add_string(Argument.ARG_MESSAGE, "Send friend request successful!")
        send(sock, send_cmd)
        if check_player_online(cmd.get_string(Argument.ARG_PLAYER_USERNAME)):
            send_cmd = Command(Command.CMD_ADD_FRIEND)
            send_cmd.add_int(Argument.ARG_CODE, 2)
            send_cmd.add_string(Argument.ARG_MESSAGE, "You have a friend request from " + str(sock_name_map.get(sock)))
            send_cmd.add_string(Argument.ARG_PLAYER_USERNAME, str(sock_name_map.get(sock)))
            send(name_sock_map[cmd.get_string(Argument.ARG_PLAYER_USERNAME)], send_cmd)
            pass
    else:
        send_cmd = Command(Command.CMD_ADD_FRIEND)
        send_cmd.add_int(Argument.ARG_CODE, 0)
        send_cmd.add_string(Argument.ARG_PLAYER_USERNAME, str(sock_name_map.get(sock)))
        send_cmd.add_string(Argument.ARG_MESSAGE, "Send friend invitation failure or became "
                                                  "friend before you send invitation! Please try again!")
        send(sock, send_cmd)
        pass


def analysis_message_accept_friend(sock, cmd):
    code = cmd.get_int(Argument.ARG_CODE, 0)
    if code == 0:
        "denied"
        # update database
        db.denied_friend(sock_name_map.get(sock), cmd.get_string(Argument.ARG_PLAYER_USERNAME))
        send_cmd = Command(Command.CMD_ACCEPT_FRIEND)
        send_cmd.add_int(Argument.ARG_CODE, 0)
        send_cmd.add_string(Argument.ARG_MESSAGE, "Denied friend request successful")
        send(sock, send_cmd)
    else:
        "accept"
        # update database
        if db.accept_friend(sock_name_map.get(sock), cmd.get_string(Argument.ARG_PLAYER_USERNAME)):
            # send message to user
            send_cmd = Command(Command.CMD_ACCEPT_FRIEND)
            send_cmd.add_int(Argument.ARG_CODE, 1)
            send_cmd.add_string(Argument.ARG_MESSAGE, "You and " + str(cmd.get_string(Argument.ARG_PLAYER_USERNAME))
                                + " became friend!")
            send(sock, send_cmd)
            # If other user is online, send message
            if check_player_online(cmd.get_string(Argument.ARG_PLAYER_USERNAME)):
                try:
                    send_cmd2 = Command(Command.CMD_ACCEPT_FRIEND)
                    send_cmd2.add_int(Argument.ARG_CODE, 2)
                    send_cmd2.add_string(Argument.ARG_MESSAGE, "You and " + str(sock_name_map.get(sock))
                                         + " became friend!")
                    send_cmd2.add_string(Argument.ARG_PLAYER_USERNAME, str(sock_name_map.get(sock)))
                    send(name_sock_map[cmd.get_string(Argument.ARG_PLAYER_USERNAME)], send_cmd2)
                    pass
                except Exception as inst:
                    print inst.message
                pass
            else:
                log.log("Client is offline")
    pass


def analysis_message_remove_friend(sock, cmd):
    if db.un_friend(sock_name_map.get(sock), cmd.get_string(Argument.ARG_PLAYER_USERNAME)):
        send_cmd = Command(Command.CMD_REMOVE_FRIEND)
        send_cmd.add_int(Argument.ARG_CODE, 1)
        send_cmd.add_string(Argument.ARG_MESSAGE, "Remove friend successful!")
        send(sock, send_cmd)
        send_cmd = Command(Command.CMD_REMOVE_FRIEND)
        send_cmd.add_string(Argument.ARG_PLAYER_USERNAME, str(sock_name_map.get(sock)))
        send_cmd.add_int(Argument.ARG_CODE, 2)
        send_cmd.add_string(Argument.ARG_MESSAGE, "You are removed friendship with " + str(sock_name_map.get(sock)) +
                            " !")
        send(name_sock_map[cmd.get_string(Argument.ARG_PLAYER_USERNAME)], send_cmd)
        pass
    else:
        send_cmd = Command(Command.CMD_REMOVE_FRIEND)
        send_cmd.add_int(Argument.ARG_CODE, 0)
        send_cmd.add_string(Argument.ARG_MESSAGE, "Remove friend failure!")
        send(sock, send_cmd)
    pass


def analysis_message_cancel_request(sock, cmd):
    if db.cancel_request(sock_name_map.get(sock), cmd.get_string(Argument.ARG_PLAYER_USERNAME)):
        send_cmd = Command(Command.CMD_CANCEL_REQUEST)
        send_cmd.add_string(Argument.ARG_PLAYER_USERNAME, cmd.get_string(Argument.ARG_PLAYER_USERNAME))
        send_cmd.add_int(Argument.ARG_CODE, 1)
        send_cmd.add_string(Argument.ARG_MESSAGE, "Cancel request successful!!!")
        send(sock, send_cmd)
        pass
    else:
        send_cmd = Command(Command.CMD_CANCEL_REQUEST)
        send_cmd.add_string(Argument.ARG_PLAYER_USERNAME, cmd.get_string(Argument.ARG_PLAYER_USERNAME))
        send_cmd.add_int(Argument.ARG_CODE, 0)
        send_cmd.add_string(Argument.ARG_MESSAGE, "Cancel request failure!!!")
        send(sock, send_cmd)
    pass


def analysis_message_invite_friend(sock, cmd):
    pass


def analysis_message_upgrade(sock, cmd):
    kind = cmd.get_int(Argument.ARG_TYPE, 0)
    amount = cmd.get_int(Argument.ARG_AMOUNT, 0)
    if type == 0:
        return
    if amount <= 0:
        return
    db.upgrade(sock_name_map.get(sock), kind, amount)
    return


"""====================GAME MESSAGE================"""


def analysis_message_game_join(sock, cmd):
    waiting_list.append(sock)
    log.log("Add client to Waiting List")
    pass


def analysis_message_room_exit(sock, cmd):
    room_id = cmd.get_int(Argument.ARG_ROOM_ID, 0)
    room = room_list.get(room_id)
    if None != room:
        send_cmd = Command(Command.CMD_ROOM_EXIT)
        send_cmd.add_int(Argument.ARG_CODE, 1)
        if room.sock1 == sock:
            send(room.sock1, send_cmd)
            send(room.sock2, send_cmd)
            pass
        else:
            send(room.sock2, send_cmd)
            send(room.sock1, send_cmd)
            pass
        del room_list[room_id]
        log.log("Size of room list = " + str(len(room_list)))
    pass


def analysis_message_game_join_cancel(sock, cmd):
    waiting_list.remove(sock)
    log.log("Remove client from Waiting List")
    pass


def analysis_message_game_ready(sock, cmd):
    is_ready = cmd.get_int(Argument.ARG_CODE, 0)
    room_id = cmd.get_int(Argument.ARG_ROOM_ID, 0)
    """Search sock in room_info list"""
    room = room_list.get(room_id)
    if None != room:
        if room.sock1 == sock:
            # Send to opponent sock
            ready_cmd = Command(Command.CMD_GAME_READY)
            ready_cmd.add_string(Argument.ARG_PLAYER_USERNAME, sock_name_map.get(sock, "no name"))
            ready_cmd.add_byte(Argument.ARG_CODE, is_ready)
            send(room.sock2, ready_cmd)
            if is_ready == 1:
                room.ready[0] = True
            else:
                room.ready[0] = False

        elif room.sock2 == sock:
            ready_cmd = Command(Command.CMD_GAME_READY)
            ready_cmd.add_string(Argument.ARG_PLAYER_USERNAME, sock_name_map.get(sock, "no name"))
            ready_cmd.add_byte(Argument.ARG_CODE, is_ready)
            send(room.sock1, ready_cmd)
            # Send to opponent sock
            if is_ready == 1:
                room.ready[1] = True
            else:
                room.ready[1] = False

        if room.is_all_ready():
            "Send start game message if 2 player ready"
            start_cmd = Command(Command.CMD_GAME_START)
            send(room.sock1, start_cmd)
            send(room.sock2, start_cmd)
            "Generate map"
            map_cmd = Command(Command.CMD_MAP_INFO)
            map_cmd.add_string(Argument.ARG_PLAYER_USERNAME, sock_name_map[room.sock1])
            map_id = random.randint(1, 2)
            # TODO
            map_cmd.add_int(Argument.ARG_MAP_ID, map_id)
            send(room.sock1, map_cmd)
            send(room.sock2, map_cmd)
            pass
        pass
    pass


def analysis_message_player_move(sock, cmd):
    room_id = cmd.get_int(Argument.ARG_ROOM_ID, 0)
    room = room_list.get(room_id)
    if None != room:
        # move_from = cmd.get_int(Argument.ARG_MOVE_FROM)
        move_to = cmd.get_int(Argument.ARG_MOVE_TO)
        send_cmd = Command(Command.CMD_PLAYER_MOVE)
        send_cmd.add_string(Argument.ARG_PLAYER_USERNAME, sock_name_map.get(sock))
        # send_cmd.add_int(Argument.ARG_MOVE_FROM, move_from)
        send_cmd.add_int(Argument.ARG_MOVE_TO, move_to)
        send(room.sock1, send_cmd)
        send(room.sock2, send_cmd)
        pass


def analysis_message_turn_timeout(sock, cmd):
    room_id = cmd.get_int(Argument.ARG_ROOM_ID, 0)
    room = room_list.get(room_id)
    if None != room:
        if sock == room.sock1:
            change_turn = Command(Command.CMD_PLAYER_TURN)
            change_turn.add_string(Argument.ARG_PLAYER_USERNAME, sock_name_map.get(room.sock2))
            send(room.sock1, change_turn)
            send(room.sock2, change_turn)
            pass
        else:
            change_turn = Command(Command.CMD_PLAYER_TURN)
            change_turn.add_string(Argument.ARG_PLAYER_USERNAME, sock_name_map.get(room.sock1))
            send(room.sock1, change_turn)
            send(room.sock2, change_turn)
            pass
        pass


def analysis_message_player_drop(sock, cmd):
    room_id = cmd.get_int(Argument.ARG_ROOM_ID, 0)
    room = room_list.get(room_id)
    if None != room:
        rotation = cmd.get_string(Argument.ARG_DROP_ROTATION, "")
        vel_x = cmd.get_int(Argument.ARG_DROP_VEL_X, 0)
        vel_y = cmd.get_int(Argument.ARG_DROP_VEL_Y, 0)
        send_cmd = Command(Command.CMD_PLAYER_DROP)
        send_cmd.add_string(Argument.ARG_PLAYER_USERNAME, sock_name_map.get(sock))
        send_cmd.add_int(Argument.ARG_DROP_VEL_X, vel_x)
        send_cmd.add_int(Argument.ARG_DROP_VEL_Y, vel_y)
        send_cmd.add_string(Argument.ARG_DROP_ROTATION, rotation)
        if sock == room.sock1:
            send(room.sock1, send_cmd)
            send(room.sock2, send_cmd)
            pass
        else:
            send(room.sock2, send_cmd)
            send(room.sock1, send_cmd)
            pass
        pass
    pass


def analysis_message_player_drop_result(sock, cmd):
    room_id = cmd.get_int(Argument.ARG_ROOM_ID, 0)
    room = room_list.get(room_id)
    if None == room:
        return
    code = cmd.get_int(Argument.ARG_CODE, 0)

    if code == 1:
        obj_type = cmd.get_int(Argument.ARG_MAP_OBJ_TYPE, 0)
        add_score = Command(Command.CMD_ADD_SCORE)
        add_score.add_string(Argument.ARG_PLAYER_USERNAME, sock_name_map.get(sock))
        if obj_type == -1:
            if room.sock1 == sock:
                if room.score[0] > 100:
                    room.score[0] += -100
                else:
                    room.score[0] = 0
                pass
            else:
                if room.score[1] > 100:
                    room.score[1] += 100
                else:
                    room.score[1] = 0
                pass
            add_score.add_int(Argument.ARG_SCORE, -100)
            pass
        else:
            if room.sock1 == sock:
                add = 0
                if obj_type == 1:
                    add = 10
                    pass
                elif obj_type == 2:
                    add = 50
                    pass
                elif obj_type == 3:
                    add = 250
                    pass
                elif obj_type == 4:
                    add = 500
                    pass
                elif obj_type == 5:
                    add = 660
                    pass
                room.score[0] += add
                add_score.add_int(Argument.ARG_SCORE, add)
                pass
            else:
                add = 0
                if obj_type == 1:
                    add = 10
                    pass
                elif obj_type == 2:
                    add = 50
                    pass
                elif obj_type == 3:
                    add = 250
                    pass
                elif obj_type == 4:
                    add = 500
                    pass
                elif obj_type == 5:
                    add = 660
                    pass
                room.score[1] += add
                add_score.add_int(Argument.ARG_SCORE, add)
                pass
        send(room.sock1, add_score)
        send(room.sock2, add_score)
        pass
    "Change player turn"
    if room.sock1 == sock:
        change_turn = Command(Command.CMD_PLAYER_TURN)
        change_turn.add_string(Argument.ARG_PLAYER_USERNAME, sock_name_map.get(room.sock2))
        send(room.sock1, change_turn)
        send(room.sock2, change_turn)
        pass
    elif room.sock2 == sock:
        change_turn = Command(Command.CMD_PLAYER_TURN)
        change_turn.add_string(Argument.ARG_PLAYER_USERNAME, sock_name_map.get(room.sock1))
        send(room.sock1, change_turn)
        send(room.sock2, change_turn)
        pass
    pass


def analysis_message_game_finish(sock, cmd):
    room_id = cmd.get_int(Argument.ARG_ROOM_ID, 0)
    room_info = room_list.get(room_id)
    if None != room_info:
        finish_cmd = Command(Command.CMD_GAME_FINISH)
        if room_info.score[0] > room_info.score[1]:
            finish_cmd.add_int(Argument.ARG_CODE, 1)
            finish_cmd.add_string(Argument.ARG_PLAYER_USERNAME, str(sock_name_map.get(room_info.sock1)))
            pass
        elif room_info.score[0] < room_info.score[1]:
            finish_cmd.add_int(Argument.ARG_CODE, 1)
            finish_cmd.add_string(Argument.ARG_PLAYER_USERNAME, str(sock_name_map.get(room_info.sock2)))
            pass
        else:
            finish_cmd.add_int(Argument.ARG_CODE, 0)
            pass
        send(room_info.sock1, finish_cmd)
        send(room_info.sock2, finish_cmd)

        "Send match result"
        "Player 1"
        player1_result = Command(Command.CMD_PLAYER_GAME_RESULT)
        player1_result.add_string(Argument.ARG_PLAYER_USERNAME, str(sock_name_map.get(room_info.sock1)))
        player1_result.add_int(Argument.ARG_SCORE, room_info.score[0])
        if room_info.score[0] > room_info.score[1]:
            player1_result.add_int(Argument.ARG_PLAYER_BONUS_CUP, 5)
            player1_result.add_int(Argument.ARG_PLAYER_BONUS_LEVELUP_POINT, room_info.score[0] / 10)
            db.update_player_cup(sock_name_map.get(room_info.sock1), 5)
            db.update_player_level_up_point(sock_name_map.get(room_info.sock1), room_info.score[0] / 10)
            pass
        elif room_info.score[0] < room_info.score[1]:
            player1_result.add_int(Argument.ARG_PLAYER_BONUS_CUP, -5)
            player1_result.add_int(Argument.ARG_PLAYER_BONUS_LEVELUP_POINT, room_info.score[0] / 10)
            db.update_player_cup(sock_name_map.get(room_info.sock1), -5)
            db.update_player_level_up_point(sock_name_map.get(room_info.sock1), room_info.score[0] / 10)
            pass
        else:
            player1_result.add_int(Argument.ARG_PLAYER_BONUS_CUP, 2)
            player1_result.add_int(Argument.ARG_PLAYER_BONUS_LEVELUP_POINT, room_info.score[0] / 10)
            db.update_player_cup(sock_name_map.get(room_info.sock1), 2)
            db.update_player_level_up_point(sock_name_map.get(room_info.sock1), room_info.score[0] / 10)
        send(room_info.sock1, player1_result)
        send(room_info.sock2, player1_result)
        "Player 2"
        player2_result = Command(Command.CMD_PLAYER_GAME_RESULT)
        player2_result.add_string(Argument.ARG_PLAYER_USERNAME, str(sock_name_map.get(room_info.sock2)))
        player2_result.add_int(Argument.ARG_SCORE, room_info.score[1])
        if room_info.score[1] > room_info.score[0]:
            player2_result.add_int(Argument.ARG_PLAYER_BONUS_CUP, 5)
            player2_result.add_int(Argument.ARG_PLAYER_BONUS_LEVELUP_POINT, room_info.score[1] / 10)
            db.update_player_cup(sock_name_map.get(room_info.sock2), 5)
            db.update_player_level_up_point(sock_name_map.get(room_info.sock2), room_info.score[1] / 10)
            pass
        elif room_info.score[1] < room_info.score[0]:
            player2_result.add_int(Argument.ARG_PLAYER_BONUS_CUP, -5)
            player2_result.add_int(Argument.ARG_PLAYER_BONUS_LEVELUP_POINT, room_info.score[1] / 10)
            db.update_player_cup(sock_name_map.get(room_info.sock2), -5)
            db.update_player_level_up_point(sock_name_map.get(room_info.sock2), room_info.score[1] / 10)
            pass
        else:
            player2_result.add_int(Argument.ARG_PLAYER_BONUS_CUP, 2)
            player2_result.add_int(Argument.ARG_PLAYER_BONUS_LEVELUP_POINT, room_info.score[1] / 10)
            db.update_player_cup(sock_name_map.get(room_info.sock2), 2)
            db.update_player_level_up_point(sock_name_map.get(room_info.sock2), room_info.score[1] / 10)
        send(room_info.sock1, player2_result)
        send(room_info.sock2, player2_result)
        "Send updated player info to player 1"
        info = db.get_user_info(str(sock_name_map.get(room_info.sock1)))
        send_cmd2 = Command(Command.CMD_PLAYER_INFO)
        send_cmd2.add_int(Argument.ARG_PLAYER_LEVEL, int(info["level"]))
        send_cmd2.add_int(Argument.ARG_PLAYER_LEVEL_UP_POINT, int(info["levelup_point"]))
        send_cmd2.add_int(Argument.ARG_PLAYER_CUP, int(info["cup"]))
        send_cmd2.add_int(Argument.ARG_PLAYER_LEVEL_UP_REQUIRE, int(info["require_point"]))
        send_cmd2.add_int(Argument.ARG_PLAYER_SPEED_MOVE, int(info["speed_move"]))
        send_cmd2.add_int(Argument.ARG_PLAYER_SPEED_DROP, int(info["speed_drop"]))
        send_cmd2.add_int(Argument.ARG_PLAYER_SPEED_DRAG, int(info["speed_drag"]))
        send(room_info.sock1, send_cmd2)
        "Send updated player info to player 2"
        info2 = db.get_user_info(str(sock_name_map.get(room_info.sock2)))
        send_cmd3 = Command(Command.CMD_PLAYER_INFO)
        send_cmd3.add_int(Argument.ARG_PLAYER_LEVEL, int(info2["level"]))
        send_cmd3.add_int(Argument.ARG_PLAYER_LEVEL_UP_POINT, int(info2["levelup_point"]))
        send_cmd3.add_int(Argument.ARG_PLAYER_CUP, int(info2["cup"]))
        send_cmd3.add_int(Argument.ARG_PLAYER_LEVEL_UP_REQUIRE, int(info2["require_point"]))
        send_cmd3.add_int(Argument.ARG_PLAYER_SPEED_MOVE, int(info["speed_move"]))
        send_cmd3.add_int(Argument.ARG_PLAYER_SPEED_DROP, int(info["speed_drop"]))
        send_cmd3.add_int(Argument.ARG_PLAYER_SPEED_DRAG, int(info["speed_drag"]))
        send(room_info.sock2, send_cmd3)
        # room_list.pop(room_id)
        log.log("Removed room. Current number of room is " + len(room_list))
    else:
        log.log("Can't find room")


def analysis_message_game_force_finish(sock, cmd):
    pass


def check_player_online(username=""):
    if username in name_sock_map.keys():
        return True
    else:
        return False


def thread_game_matching(sleep_time=0):
    room_id = 0
    while reading:
        time.sleep(sleep_time)
        # In one time, send message matched game for 2 user.
        # After that pop that from waiting_list
        if len(waiting_list) >= 2:
            "Increment room_id 1 unit"
            room_id += 1
            "Create RoomInfo object and add to RoomList"
            room_info = RoomInfo(room_id, waiting_list[len(waiting_list) - 1], waiting_list[len(waiting_list) - 2])
            room_list[room_id] = room_info
            "Send message join room to user 1"
            matching_cmd = Command(Command.CMD_GAME_MATCHING)
            matching_cmd.add_int(Argument.ARG_CODE, 1)
            send(waiting_list[len(waiting_list) - 1], matching_cmd)

            cmd1 = Command(Command.CMD_ROOM_INFO)
            cmd1.add_string(Argument.ARG_PLAYER_USERNAME, str(sock_name_map.get(room_info.sock1)))
            cmd1.add_int(Argument.ARG_ROOM_ID, room_id)
            cmd1.add_int(Argument.ARG_CUP_WIN, 5)
            cmd1.add_int(Argument.ARG_CUP_LOST, -5)

            send(waiting_list[len(waiting_list) - 1], cmd1)
            "Send other player info"
            user2_name = sock_name_map.get(waiting_list[len(waiting_list) - 2])
            info = db.get_user_info(user2_name)
            user2_info = Command(Command.CMD_FRIEND_INFO)
            user2_info.add_string(Argument.ARG_PLAYER_USERNAME, str(info["username"]))
            user2_info.add_int(Argument.ARG_PLAYER_LEVEL, int(info["level"]))
            user2_info.add_int(Argument.ARG_PLAYER_LEVEL_UP_POINT, int(info["levelup_point"]))
            user2_info.add_int(Argument.ARG_PLAYER_CUP, int(info["cup"]))
            user2_info.add_int(Argument.ARG_PLAYER_LEVEL_UP_REQUIRE, int(info["require_point"]))
            user2_info.add_int(Argument.ARG_PLAYER_SPEED_MOVE, int(info["speed_move"]))
            user2_info.add_int(Argument.ARG_PLAYER_SPEED_DRAG, int(info["speed_drag"]))
            user2_info.add_int(Argument.ARG_PLAYER_SPEED_DROP, int(info["speed_drop"]))
            user2_info.add_int(Argument.ARG_FRIEND_TYPE,
                               db.get_friend_type(sock_name_map.get(waiting_list[len(waiting_list) - 1]),
                                                  sock_name_map.get(waiting_list[len(waiting_list) - 2])))
            send(waiting_list[len(waiting_list) - 1], user2_info)

            "Send message join room to user2"
            cmd2 = Command(Command.CMD_GAME_MATCHING)
            cmd2.add_int(Argument.ARG_CODE, 1)
            send(waiting_list[len(waiting_list) - 2], cmd2)
            cmd2 = Command(Command.CMD_ROOM_INFO)
            cmd2.add_string(Argument.ARG_PLAYER_USERNAME, str(sock_name_map.get(room_info.sock1)))
            cmd2.add_int(Argument.ARG_ROOM_ID, room_id)
            cmd2.add_int(Argument.ARG_CUP_WIN, 5)
            cmd2.add_int(Argument.ARG_CUP_LOST, -5)
            send(waiting_list[len(waiting_list) - 2], cmd2)
            "Send other player info"
            user1_name = sock_name_map.get(waiting_list[len(waiting_list) - 1])
            info = db.get_user_info(user1_name)
            user1_info = Command(Command.CMD_FRIEND_INFO)
            user1_info.add_string(Argument.ARG_PLAYER_USERNAME, str(info["username"]))
            user1_info.add_int(Argument.ARG_PLAYER_LEVEL, int(info["level"]))
            user1_info.add_int(Argument.ARG_PLAYER_LEVEL_UP_POINT, int(info["levelup_point"]))
            user1_info.add_int(Argument.ARG_PLAYER_CUP, int(info["cup"]))
            user1_info.add_int(Argument.ARG_PLAYER_LEVEL_UP_REQUIRE, int(info["require_point"]))
            user1_info.add_int(Argument.ARG_PLAYER_SPEED_MOVE, int(info["speed_move"]))
            user1_info.add_int(Argument.ARG_PLAYER_SPEED_DRAG, int(info["speed_drag"]))
            user1_info.add_int(Argument.ARG_PLAYER_SPEED_DROP, int(info["speed_drop"]))
            user1_info.add_int(Argument.ARG_FRIEND_TYPE,
                               db.get_friend_type(sock_name_map.get(waiting_list[len(waiting_list) - 2]),
                                                  sock_name_map.get(waiting_list[len(waiting_list) - 1])))
            send(waiting_list[len(waiting_list) - 2], user1_info)
            "Add to room_list"
            room_list[room_id] = RoomInfo(room_id, waiting_list[len(waiting_list) - 1],
                                          waiting_list[len(waiting_list) - 2])
            log.log("Apend new room")
            "Remove from Waiting_List"
            waiting_list.pop(len(waiting_list) - 1)
            waiting_list.pop(len(waiting_list) - 1)
            log.log("Remove from waiting_list; Now waiting list size = " + str(len(waiting_list)))
            pass
    pass


def remove_sock(sock):
    try:
        sock.close()
        """Remove client from list user"""
        if sock in sock_name_map.keys():
            name_sock_map.pop(sock_name_map[sock])
            sock_name_map.pop(sock)
        "Remove client if it waiting join game"
        if sock in waiting_list:
            waiting_list.remove(sock)
        "Remove user if user being room"
        for room in room_list.values():
            if sock == room.sock1:
                cmd = message_helper.gen_msg_room_exit()
                if None != room.sock2:
                    send(room.sock2, cmd)
            elif sock == room.sock2:
                cmd = message_helper.gen_msg_room_exit()
                if None != room.sock1:
                    send(room.sock1, cmd)
            """Remove room"""
            # room_list.pop(room.room_id)
            log.log("Remove room")
            break
        connection_list.remove(sock)
    except KeyError:
        pass


def send(s, send_cmd):
    try:
        s.sendall(send_cmd.get_bytes())
        log.log(">>>>>>>Send to  " + str(sock_name_map.get(s)) + ":" + send_cmd.get_log())
    except Exception as inst:
        print str(inst.message)
    pass


"""Database"""
db = DBManager()
# db.connect('127.0.0.1', 'root', '', 'gold_miner_online')
db.connect('127.0.0.1', 'root', 'oneofthem0107', 'gold_miner_online')
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.setblocking(0)
server_socket.listen(5)
connection_list.append(server_socket)
log.log("Game server started on port " + str(PORT))
log.log("Start thread matching")
thread.start_new_thread(thread_game_matching, (0.05, ))
while reading:
    # Get the list sockets which are ready to be read through select
    try:
        read_sockets, write_sockets, error_sockets = select.select(connection_list, [], [])
    except Exception as ints:
        print "Exception------"
        pass
    for sock in read_sockets:
        # New connection
        if sock == server_socket:
            # Handle the case in which there is a new connection received through server_socket
            sockfd, addr = server_socket.accept()
            connection_list.append(sockfd)
            log.log("Have connection from :" + str(addr))
        # Some incoming message from a client
        else:
            # Data received from client, process it
            try:
                #In Windows, sometimes when a TCP program closes abruptly,
                # a "Connection reset by peer" exception will be thrown
                data = sock.recv(RECV_BUFFER)
                if data:
                    read(sock, data)
            except IOError as err:
                print('My exception occurred, value:', err.message)
                print("Client (%s, %s) is offline" % addr)

                sock.close()
                try:
                    """Remove client from list user"""
                    if sock in sock_name_map.keys():
                        name_sock_map.pop(sock_name_map[sock])
                        sock_name_map.pop(sock)
                    "Remove client if it waiting join game"
                    if sock in waiting_list:
                        waiting_list.remove(sock)
                    "Remove user if user being room"
                    for room in room_list.values():
                        if sock == room.sock1:
                            cmd = message_helper.gen_msg_room_exit()
                            if None != room.sock2:
                                send(room.sock2, cmd)

                        elif sock == room.sock2:
                            cmd = message_helper.gen_msg_room_exit()
                            if None != room.sock1:
                                send(room.sock1, cmd)
                        """Remove room"""
                        # room_list.pop(room.room_id)
                        break
                    connection_list.remove(sock)
                    continue
                except Exception as inst:
                    log.log("Exception---------")
                    pass

reading = False
server_socket.close()

