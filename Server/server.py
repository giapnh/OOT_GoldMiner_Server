# -*- coding: utf-8 -*-
from smtpd import usage
from database.dbmanager import DBManager
from help import log
import message_helper

__author__ = 'Nguyen Huu Giap'
from command import Command
from argument import Argument
from struct import *
import thread
import socket
import select
import Message
from room_info import RoomInfo

"""
@author: giapnh
"""

HOST, PORT, RECV_BUFFER = "192.168.1.179", 9090, 4096
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
            arg_code = int(unpack("<H", data[read_count:read_count+2])[0])
            read_count += 2
            #Argument type
            arg_type = int(unpack("B", data[read_count:read_count + 1])[0])
            read_count += 1
            if arg_type == Argument.STRING:
                #string len
                str_len = int(unpack("<I", data[read_count:read_count + 4])[0])
                read_count += 4
                str_val = str(unpack(str(str_len)+"s", data[read_count:read_count + str_len])[0])
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
                int_val = int(unpack("<I", data[read_count:read_count + 4])[0])
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
    log.log("Receive:   " + cmd.get_log())
    if cmd.code == Command.CMD_LOGIN:
        analysis_message_login(sock, cmd)
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
    elif cmd.code == Command.CMD_ADD_FRIEND:
        analysis_message_add_friend(sock, cmd)
        pass
    elif cmd.code == Command.CMD_ACCEPT_FRIEND:
        analysis_message_accept_friend(sock, cmd)
        pass
    elif cmd.code == Command.CMD_REMOVE_FRIEND:
        analysis_message_remove_friend(sock, cmd)
        pass
        """Game Action"""
    elif cmd.code == Command.CMD_GAME_MATCHING:
        analysis_message_game_join(sock, cmd)
        pass
    elif cmd.code == Command.CMD_GAME_MATCHING_CANCEL:
        analysis_message_game_join_cancel(sock, cmd)
        pass
    elif cmd.code == Command.CMD_GAME_READY:
        analysis_message_game_ready(sock, cmd)
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
            #Send message disconnect to old client
            old_sock = name_sock_map[cmd.get_string(Argument.ARG_PLAYER_USERNAME)]
            disconnect_cmd = Command(Command.CMD_DISCONNECT)
            disconnect_cmd.add_int(Argument.ARG_CODE, 1)
            disconnect_cmd.add_string(Argument.ARG_MESSAGE, Message.MSG_DISCONNECT)
            send(old_sock, disconnect_cmd)
            #Send message login success to new client
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
            #TODO need modify
            send_cmd.add_int(Argument.ARG_PLAYER_LEVEL_UP_REQUIRE, 1000)
            send_cmd.add_int(Argument.ARG_PLAYER_SPEED_MOVE, int(info["speed_move"]))
            send_cmd.add_int(Argument.ARG_PLAYER_SPEED_DROP, 10)
            send_cmd.add_int(Argument.ARG_PLAYER_SPEED_DRAG, 10)
            send(sock, send_cmd)
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
            #TODO need modify
            send_cmd.add_int(Argument.ARG_PLAYER_LEVEL_UP_REQUIRE, 1000)
            send_cmd.add_int(Argument.ARG_PLAYER_SPEED_MOVE, 10)
            send_cmd.add_int(Argument.ARG_PLAYER_SPEED_DROP, 10)
            send_cmd.add_int(Argument.ARG_PLAYER_SPEED_DRAG, 10)
            send(sock, send_cmd)
    else:
        send_cmd = Command(Command.CMD_LOGIN)
        send_cmd.add_int(Argument.ARG_CODE, 0)
        send_cmd.add_string(Argument.ARG_MESSAGE, "Invalid login info, please check again or register first!")
        send(sock, send_cmd)
pass


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
        name_sock_map[to_user].sendall(send_cmd.get_bytes())
    pass


def analysis_message_list_friend(sock, cmd):
    """
    Get list friend
    @param sock:
    @param cmd:
    @return:
    """
    #TODO

    # sock.sendall(cmd.get_bytes())
    pass


def analysis_message_add_friend(sock, cmd):
    """
    Add friend message
    @param sock:
    @param cmd:
    @return:
    """
    send_cmd = Command(Command.CMD_ADD_FRIEND)
    if db.invite_friend(cmd.get_string(Argument.ARG_PLAYER_USERNAME), cmd.get_string(Argument.ARG_PLAYER_USERNAME)):
        send_cmd.add_int(Argument.ARG_CODE, 1)
        send_cmd.add_string(Argument.ARG_MESSAGE, "Send invite friend successful!")
        #TODO send to friend invite message
    else:
        send_cmd.add_int(Argument.ARG_CODE, 0)
        send_cmd.add_string(Argument.ARG_MESSAGE, "Send invite friend failure! Please try again!")
    sock.sendall(send_cmd.get_bytes())


def analysis_message_accept_friend(sock, cmd):
    db.accept_friend(cmd.get_string(Argument.ARG_PLAYER_USERNAME), cmd.get_string(Argument.ARG_PLAYER_USERNAME))
    pass


def analysis_message_remove_friend(sock, cmd):
    db.un_friend(cmd.get_string(Argument.ARG_PLAYER_USERNAME), cmd.get_string(Argument.ARG_PLAYER_USERNAME))
    pass


"""====================GAME MESSAGE================"""


def analysis_message_game_join(sock, cmd):
    waiting_list.append(sock)
    log.log("Add client to Waiting List")
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
            #Send to opponent sock
            ready_cmd = Command(Command.CMD_GAME_READY)
            ready_cmd.add_string(Argument.ARG_PLAYER_USERNAME, sock_name_map.get(sock, "no name"))
            ready_cmd.add_byte(Argument.ARG_CODE, is_ready)
            send(room.sock2, ready_cmd)
            if is_ready == 1:
                room.ready[0] = True
            else:
                room.ready[0] = False
            return
        elif room.sock2 == sock:
            ready_cmd = Command(Command.CMD_GAME_READY)
            ready_cmd.add_string(Argument.ARG_PLAYER_USERNAME, sock_name_map.get(sock, "no name"))
            ready_cmd.add_byte(Argument.ARG_CODE, is_ready)
            send(room.sock1, ready_cmd)
            #Send to opponent sock
            if is_ready == 1:
                room.ready[1] = True
            else:
                room.ready[1] = False
            return
    pass


def check_player_online(username=""):
    if username in name_sock_map.keys():
        return True
    else:
        return False


def thread_game_matching(sleep_time=0):
    room_id = 0
    #TODO
    while reading:
        #In one time, send message matched game for 2 user.
        # After that pop that from waiting_list
        if len(waiting_list) >= 2:
            "Increment room_id 1 unit"
            room_id += 1
            "Create RoomInfo object and add to RoomList"
            room_info = RoomInfo(room_id, waiting_list[0], waiting_list[1])
            room_list[room_id] = room_info
            "Send message join room to user 1"
            cmd1 = Command(Command.CMD_GAME_MATCHING)
            cmd1.add_int(Argument.ARG_CODE, 1)
            send(waiting_list[0], cmd1)

            cmd1 = Command(Command.CMD_ROOM_INFO)
            cmd1.add_int(Argument.ARG_ROOM_ID, room_id)
            cmd1.add_int(Argument.ARG_CUP_WIN, 100)
            cmd1.add_int(Argument.ARG_CUP_LOST, 10)

            send(waiting_list[0], cmd1)
            "Send other player info"
            user2_name = sock_name_map.get(waiting_list[1])
            info = db.get_user_info(user2_name)
            user2_info = Command(Command.CMD_FRIEND_INFO)
            user2_info.add_string(Argument.ARG_PLAYER_USERNAME, str(info["username"]))
            user2_info.add_int(Argument.ARG_PLAYER_LEVEL, int(info["level"]))
            user2_info.add_int(Argument.ARG_PLAYER_LEVEL_UP_POINT, int(info["levelup_point"]))
            user2_info.add_int(Argument.ARG_PLAYER_CUP, int(info["cup"]))
            user2_info.add_int(Argument.ARG_PLAYER_LEVEL_UP_REQUIRE, 1000)
            user2_info.add_int(Argument.ARG_PLAYER_SPEED_MOVE, int(info["speed_move"]))
            user2_info.add_int(Argument.ARG_PLAYER_SPEED_DRAG, int(info["speed_drag"]))
            user2_info.add_int(Argument.ARG_PLAYER_SPEED_DROP, int(info["speed_drop"]))
            send(waiting_list[0], user2_info)
            "Send message join room to user2"
            cmd2 = Command(Command.CMD_GAME_MATCHING)
            cmd2.add_int(Argument.ARG_CODE, 1)
            send(waiting_list[1], cmd2)
            cmd2 = Command(Command.CMD_ROOM_INFO)
            cmd2.add_int(Argument.ARG_ROOM_ID, room_id)
            cmd2.add_int(Argument.ARG_CUP_WIN, 100)
            cmd2.add_int(Argument.ARG_CUP_LOST, 100)
            send(waiting_list[1], cmd2)
            "Send other player info"
            user1_name = sock_name_map.get(waiting_list[0])
            info = db.get_user_info(user1_name)
            user1_info = Command(Command.CMD_FRIEND_INFO)
            user1_info.add_string(Argument.ARG_PLAYER_USERNAME, str(info["username"]))
            user1_info.add_int(Argument.ARG_PLAYER_LEVEL, int(info["level"]))
            user1_info.add_int(Argument.ARG_PLAYER_LEVEL_UP_POINT, int(info["levelup_point"]))
            user1_info.add_int(Argument.ARG_PLAYER_CUP, int(info["cup"]))
            user1_info.add_int(Argument.ARG_PLAYER_LEVEL_UP_REQUIRE, 1000)
            user1_info.add_int(Argument.ARG_PLAYER_SPEED_MOVE, int(info["speed_move"]))
            user1_info.add_int(Argument.ARG_PLAYER_SPEED_DRAG, int(info["speed_drag"]))
            user1_info.add_int(Argument.ARG_PLAYER_SPEED_DROP, int(info["speed_drop"]))
            send(waiting_list[1], user1_info)
            "Add to room_list"
            room_list[room_id] = RoomInfo(room_id, waiting_list[0], waiting_list[1])
            log.log("Apend new room")
            "Remove from Waiting_List"
            waiting_list.pop(0)
            waiting_list.pop(0)
            log.log("Remove from waiting_list; Now waiting list size = " + str(len(waiting_list)))
            pass
    pass


def send(sock, send_cmd):
    sock.sendall(send_cmd.get_bytes())
    log.log("Send:   "+send_cmd.get_log())
    pass

"""Database"""
db = DBManager()
db.connect('127.0.0.1', 'root', '', 'gold_miner_online')
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.setblocking(0)
server_socket.listen(5)
connection_list.append(server_socket)
log.log("Game server started on port " + str(PORT))
log.log("Start thread matching")
thread.start_new_thread(thread_game_matching, (0, ))
while reading:
    # Get the list sockets which are ready to be read through select
    read_sockets, write_sockets, error_sockets = select.select(connection_list, [], [])
    for sock in read_sockets:
        #New connection
        if sock == server_socket:
            # Handle the case in which there is a new connection received through server_socket
            sockfd, addr = server_socket.accept()
            connection_list.append(sockfd)
            log.log("Have connection from :" + str(addr))
        #Some incoming message from a client
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
                        room_list.pop(room.room_id)
                        break
                    connection_list.remove(sock)
                    continue
                except KeyError:
                    pass
reading = False
server_socket.close()

