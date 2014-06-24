__author__ = 'Nguyen Huu Giap'
import socket
from struct import *
from command import Command
from argument import Argument
import message_helper
from help import log


def read(data):
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
    print "Received: "+cmd.get_log()
    pass

def send(sock, cmd):
    log.log("Send: "+cmd.get_log())
    sock.sendall(cmd.get_bytes())
    pass

HOST, PORT = "192.168.1.179", 9090
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
# cmd = Command(Command.CMD_ADD_FRIEND)
# cmd.add_string(Argument.ARG_PLAYER_USERNAME, "giapnh")

cmd = Command(Command.CMD_LOGIN)
# username = raw_input("Username:")
# password = raw_input("Password:")
username = "giapnh"
password = "kachimasu"
cmd.add_string(Argument.ARG_PLAYER_USERNAME, username)
cmd.add_string(Argument.ARG_PLAYER_PASSWORD, password)
sock.sendall(cmd.get_bytes())
data = sock.recv(1024)
read(data)
data = sock.recv(1024)
read(data)
send(sock, message_helper.gen_msg_join(username))
data = sock.recv(1024)
read(data)
data = sock.recv(1024)
read(data)
data = sock.recv(1024)
read(data)
cmd = Command(Command.CMD_GAME_READY)
cmd.add_int(Argument.ARG_CODE, 1)
sock.sendall(cmd.get_bytes())
data = sock.recv(1024)
read(data)
"""
while True:
    chat_with = raw_input("You want chat with?")
    message = raw_input("Message:")
    cmd = Command(Command.CMD_PLAYER_CHAT)
    cmd.add_string(Argument.ARG_PLAYER_USERNAME, chat_with)
    cmd.add_string(Argument.ARG_MESSAGE, message)
    sock.sendall(cmd.get_bytes())
    print "Send: "+cmd.get_log()
    data = sock.recv(1024)
    read(data)
"""
