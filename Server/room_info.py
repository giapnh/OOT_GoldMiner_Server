__author__ = 'GiapNH'


class RoomInfo:
    STATE_WAITING = 0
    STATE_PLAYING = 1
    STATE_FINISH = 2
    TYPE_RANDOM = 1
    TYPE_INVITE = 2

    def __init__(self, room_id, sock1, sock2, r_type=0):
        self.room_id = room_id
        self.sock1 = sock1
        self.sock2 = sock2
        self.ready = []
        self.ready.append(False)
        self.ready.append(False)
        "Player score"
        self.score = []
        self.score.append(0)
        self.score.append(0)

        """Initial game state: Waiting!"""
        self.game_state = RoomInfo.STATE_WAITING
        self.room_type = r_type
        pass

    def ready(self, sock, is_ready):
        if sock == self.sock1:
            if is_ready == 1:
                self.ready[0] = True
            else:
                self.ready[0] = False
        elif sock == self.sock2:
            if is_ready == 1:
                self.ready[1] = True
            else:
                self.ready[1] = False
        pass

    def start_game(self):
        self.game_state = RoomInfo.STATE_PLAYING

    def finish_game(self):
        self.game_state = RoomInfo.STATE_FINISH

    def waiting_game(self):
        self.game_state = RoomInfo.STATE_WAITING
        self.ready[0] = False
        self.ready[1] = False

    def is_all_ready(self):
        if True == self.ready[0] and True == self.ready[1]:
            return True
        return False
