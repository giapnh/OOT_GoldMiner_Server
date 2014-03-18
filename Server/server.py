# -*- coding: utf-8 -*-
from database.dbmanager import DBManager
from help import log

__author__ = 'Nguyen Huu Giap'
from command import Command
from argument import Argument
from struct import *
import thread
import socket
import select
import Message

"""
@author: giapnh
"""


def read(sock, data):
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
            send_cmd.add_int(Argument.ARG_PLAYER_LEVEL, int(info["u_level"]))
            send_cmd.add_int(Argument.ARG_PLAYER_LEVEL_UP_POINT, int(info["u_levelup_point"]))
            send_cmd.add_int(Argument.ARG_PLAYER_CUP, int(info["u_cup"]))
            #TODO need modify
            send_cmd.add_int(Argument.ARG_PLAYER_LEVEL_UP_REQUIRE, 1000)
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
            send_cmd.add_int(Argument.ARG_PLAYER_LEVEL, int(info["u_level"]))
            send_cmd.add_int(Argument.ARG_PLAYER_LEVEL_UP_POINT, int(info["u_levelup_point"]))
            send_cmd.add_int(Argument.ARG_PLAYER_CUP, int(info["u_cup"]))
            #TODO need modify
            send_cmd.add_int(Argument.ARG_PLAYER_LEVEL_UP_REQUIRE, 1000)
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
    to_user = cmd.get_string(Argument.ARG_FRIEND_USERNAME, "no name")
    message = cmd.get_string(Argument.ARG_MESSAGE, "no content")
    send_cmd = Command(Command.CMD_PLAYER_CHAT)
    send_cmd.add_string(Argument.ARG_FRIEND_USERNAME, from_user)
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
    if db.invite_friend(cmd.get_string(Argument.ARG_PLAYER_USERNAME), cmd.get_string(Argument.ARG_FRIEND_USERNAME)):
        send_cmd.add_int(Argument.ARG_CODE, 1)
        send_cmd.add_string(Argument.ARG_MESSAGE, "Send invite friend successful!")
        #TODO send to friend invite message
    else:
        send_cmd.add_int(Argument.ARG_CODE, 0)
        send_cmd.add_string(Argument.ARG_MESSAGE, "Send invite friend failure! Please try again!")
    sock.sendall(send_cmd.get_bytes())


def analysis_message_accept_friend(sock, cmd):
    db.accept_friend(cmd.get_string(Argument.ARG_PLAYER_USERNAME), cmd.get_string(Argument.ARG_FRIEND_USERNAME))
    pass


def analysis_message_remove_friend(sock, cmd):
    db.un_friend(cmd.get_string(Argument.ARG_PLAYER_USERNAME), cmd.get_string(Argument.ARG_FRIEND_USERNAME))
    pass


"""====================GAME MESSAGE================"""


def analysis_message_game_join(sock, cmd):
    waiting_list[len(waiting_list)] = sock
    pass


def check_player_online(username=""):
    if username in name_sock_map.keys():
        return True
    else:
        return False


def thread_game_matching():
    while reading:
        pass
    pass

def send(sock, send_cmd):
    sock.sendall(send_cmd.get_bytes())
    print "Send:   "+send_cmd.get_log()
    pass


HOST, PORT, RECV_BUFFER = "localhost", 9090, 4096
data = None
reading = True
"""Connection List"""
connection_list = []
waiting_list = []
playing_list = []
"""List player loged in"""
name_sock_map = {}
sock_name_map = {}
"""Database"""
db = DBManager()
db.connect('127.0.0.1', 'root', '', 'gold_miner_online')
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.setblocking(0)
server_socket.listen(5)
connection_list.append(server_socket)
print "Game server started on port " + str(PORT)
print "Start thread matching"
thread.start_new_thread(thread_game_matching)
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
                print 'My exception occurred, value:', err.message
                print "Client (%s, %s) is offline" % addr
                sock.close()
                try:
                    """Remove client from list user"""
                    if sock in sock_name_map.keys():
                        name_sock_map.pop(sock_name_map[sock])
                        sock_name_map.pop(sock)
                    connection_list.remove(sock)
                    continue
                except KeyError:
                    pass
reading = False
server_socket.close()

