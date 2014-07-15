# -*- coding: utf-8 -*-
__author__ = 'Nguyen Huu Giap'
import MySQLdb
import hashlib
from help import log

class DBManager:
    #Static instance
    db = None

    def __init__(self):
        pass

    def connect(self, host, user, password, db_name):
        try:
            self.db = MySQLdb.connect(host, user, password, db_name)
            print "Init database manager successful"
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
    """
    Check user exits?
    """
    def check_user_exits(self, username=""):
        username = str.lower(username)
        c = self.db.cursor()
        c.execute("""SELECT * FROM user where username = %s""",
                  (username, ))
        if c.rowcount == 1:
            print "Check user: " + username + ": Exits!!!"
            return True
        else:
            print "Check user: " + username + ": Not Exits!!!"
            return False
    """
    Check if account is valid
    """
    def check_user_login(self, username="", password=""):
        c = self.db.cursor()
        c.execute("""SELECT * FROM user where username = %s and password = %s""",
                  (username, hashlib.md5(password).hexdigest(), ))
        if c.rowcount == 1:
            print "Check user: " + username + ": Exits!!!"
            return True
        else:
            print "Check user: " + username + ":Not Exits!!!"
            return False
    """
    Add user to database when has user register
    """
    def add_user(self, username="", password=""):
        c = self.db.cursor()
        c.execute("""INSERT INTO user(username, password) VALUES(%s, %s)""",
                  (username, hashlib.md5(password).hexdigest()))
        self.db.commit()
        pass
    """
    Get player information: username, level, ...
    """
    def get_user_info(self, username=""):
        c = self.db.cursor()
        c.execute("""SELECT username,user.level,levelup_point
         ,cup,speed_move,speed_drop,speed_drag,require_point FROM user,level_up_require WHERE username = %s
         AND user.level = level_up_require.level""", (username, ))
        self.db.commit()
        if c.rowcount >= 1:
            row = c.fetchone()
            info = {"username": row[0], "level": row[1], "levelup_point": row[2], "cup": row[3],
                    "speed_move": row[4], "speed_drop": row[5], "speed_drag": row[6], "require_point": row[7]
                    }
            return info
        else:
            return None

    def get_friend_type(self, your_name="", friend_name=""):
        c = self.db.cursor()
        if not self.check_user_exits(your_name) or not self.check_user_exits(friend_name):
            return 0
        else:
            c.execute("""SELECT id FROM user where username = %s""", (your_name, ))
            row = c.fetchone()
            userid_1 = int(row[0])
            c.execute("""SELECT id FROM user where username = %s""", (friend_name,))
            row2 = c.fetchone()
            userid_2 = int(row2[0])
            c.execute("""SELECT * FROM friendship WHERE userid_1 = %s and userid_2 = %s""",
                      (str(userid_1), str(userid_2), ))
            if c.rowcount > 0:
                return 1
            c.execute("""SELECT * FROM pending_friendship WHERE friendship_from = %s and friendship_to = %s
            """, (str(userid_1), str(userid_2), ))
            if c.rowcount > 0:
                return 2
            c.execute("""SELECT * FROM pending_friendship WHERE friendship_from = %s and friendship_to = %s
            """, (str(userid_2), str(userid_1), ))
            if c.rowcount > 0:
                return 3
            pass
        return 0

    def get_list_friend_mutual(self, username="", limit=0, offset=0):
        try:
            c = self.db.cursor()
            u_id = 0
            c.execute("""select id from user where username = %s""", (username, ))
            if c.rowcount >= 1:
                row = c.fetchone()
                u_id = int(row[0])
                pass
            c = self.db.cursor()
            c.execute("""SELECT username,level,cup
            FROM user, friendship WHERE user.id = friendship.userid_1
            and friendship.userid_2 = %s ORDER BY cup DESC LIMIT %s OFFSET %s
            """, (u_id, limit, offset, ))
            list_friend = {}
            for row in c:
                list_friend[row[0]] = {"level": row[1], "cup": row[2]}
                pass
            return list_friend
        except Exception as inst:
            print inst.message
            return None

    def get_list_friend_sent_invite(self, username=""):
        #TODO
        pass

    def get_list_friend_received_invite(self, username=""):
        #TODO
        pass

    def add_friend(self, current_user="", friend=""):
        c = self.db.cursor()
        if not self.check_user_exits(current_user) or not self.check_user_exits(friend):
            return False
        else:
            c.execute("""SELECT id FROM user where username = %s""", (current_user, ))
            row = c.fetchone()
            from_id = int(row[0])
            c.execute("""SELECT id FROM user where username = %s""", (friend,))
            row2 = c.fetchone()
            to_id = int(row2[0])
            c.execute("""SELECT * FROM friendship WHERE userid_1 = %s and userid_2 = %s""",
                      (str(from_id), str(to_id), ))
            if c.rowcount > 0:
                return False
            c.execute("""SELECT friendship_from, friendship_to FROM pending_friendship
            where friendship_from = %s and friendship_to = %s""",
                      (str(from_id), str(to_id), ))
            if c.rowcount == 0:
                #Add to pending_friendship
                c.execute("""INSERT INTO pending_friendship(friendship_from, friendship_to)
                VALUES(%s, %s)""", (str(from_id), str(to_id), ))
                self.db.commit()
                log.log("Insert into pending list..........")
                return True
            else:
                return False

    def accept_friend(self, current_user="", friend=""):
        c = self.db.cursor()
        if not self.check_user_exits(current_user) or not self.check_user_exits(friend):
            return False
        else:
            c.execute("""SELECT id FROM user where username = %s""", (current_user, ))
            row = c.fetchone()
            from_id = int(row[0])
            c.execute("""SELECT id FROM user where username = %s""", (friend,))
            row2 = c.fetchone()
            to_id = int(row2[0])
            c.execute("""INSERT INTO friendship(userid_1, userid_2)
            VALUES(%s, %s)""", (str(from_id), str(to_id), ))
            self.db.commit()
            c.execute("""INSERT INTO friendship(userid_1, userid_2)
            VALUES(%s, %s)""", (str(to_id), str(from_id), ))
            self.db.commit()
            #remove from pending
            c.execute("""DELETE FROM pending_friendship WHERE friendship_from = %s and friendship_to = %s
            or friendship_from = %s and friendship_to = %s""", (from_id, to_id, to_id, from_id, ))
            self.db.commit()
            return True

    def denied_friend(self, current_user="", friend=""):
        c = self.db.cursor()
        if not self.check_user_exits(current_user) or not self.check_user_exits(friend):
            return False
        else:
            c.execute("""SELECT id FROM user where username = %s""", (current_user, ))
            row = c.fetchone()
            from_id = int(row[0])
            c.execute("""SELECT id FROM user where username = %s""", (friend,))
            row2 = c.fetchone()
            to_id = int(row2[0])
            #remove from pending
            c.execute("""DELETE FROM pending_friendship WHERE friendship_from = %s and friendship_to = %s
            or friendship_from = %s and friendship_to = %s""", (from_id, to_id, to_id, from_id, ))
            self.db.commit()
            return True
        pass

    def un_friend(self, current_user="", friend=""):
        try:
            c = self.db.cursor()
            if not self.check_user_exits(current_user) or not self.check_user_exits(friend):
                return False
            else:
                c.execute("""SELECT id FROM user where username = %s""", (current_user, ))
                row = c.fetchone()
                from_id = int(row[0])
                c.execute("""SELECT id FROM user where username = %s""", (friend,))
                row2 = c.fetchone()
                to_id = int(row2[0])
                c.execute("""DELETE FROM friendship WHERE userid_1 = %s and userid_2 = %s""", (from_id, to_id,))
                self.db.commit()
                c.execute("""DELETE FROM friendship WHERE userid_2 = %s and userid_1 = %s""", (from_id, to_id,))
                self.db.commit()
                return True
            pass
        except Exception:
            return False
            pass

    def cancel_request(self, current_user="", friend=""):
        try:
            c = self.db.cursor()
            if not self.check_user_exits(current_user) or not self.check_user_exits(friend):
                return False
            else:
                c.execute("""SELECT id FROM user where username = %s""", (current_user, ))
                row = c.fetchone()
                from_id = int(row[0])
                c.execute("""SELECT id FROM user where username = %s""", (friend,))
                row2 = c.fetchone()
                to_id = int(row2[0])
                c.execute("""DELETE FROM pending_friendship WHERE friendship_from = %s and friendship_to =
                %s""", (from_id, to_id,))
                self.db.commit()
                return True
        except Exception:
            return False
            pass
        return False

    def update_player_cup(self, username="", bonus=0):
        info = self.get_user_info(username)
        cup = int(info["cup"])
        if cup + bonus > 0:
            c = self.db.cursor()
            c.execute("""UPDATE user SET cup = cup + %s WHERE username = %s""", (bonus, username, ))
            self.db.commit()
            return True
            pass
        else:
            c = self.db.cursor()
            c.execute("""UPDATE user SET cup = 0 WHERE username = %s""", (username, ))
            self.db.commit()
            return True
            pass

    def update_player_level_up_point(self, username="", bonus=0):
        info = self.get_user_info(username)
        level = int(info["level"])
        level_up_point = int(info["levelup_point"])
        c = self.db.cursor()
        c.execute("""SELECT require_point FROM level_up_require WHERE level = %s""", (level, ))
        if c.rowcount > 0:
            row = c.fetchone()
            level_up_point_require = int(row[0])
            pass
        else:
            return False
        if level_up_point + bonus > level_up_point_require:
            #level up
            level += 1
            level_up_point = level_up_point + bonus - level_up_point_require
            pass
        else:
            level_up_point += bonus
            pass
        c2 = self.db.cursor()
        c2.execute("""UPDATE user SET level = %s, levelup_point = %s WHERE username = %s""",
                   (level, level_up_point, username,))
        self.db.commit()
        return True

    """
    Upgrade
    """
    def upgrade(self, username="", kind=0, amount=0):
        c = self.db.cursor()
        if not self.check_user_exits(username):
            return
        c.execute("""SELECT upgrade_avai FROM user WHERE username = %s""", (username,))
        if c.rowcount > 0:
            row = c.fetchone()
            upgrade_avai = int(row[0])
            if upgrade_avai == 0:
                return
            else:
                if kind == 1:
                    c.execute("""UPDATE user SET speed_move = speed_move + %s, upgrade_avai = upgrade_avai - %s
                    WHERE username = %s""", (amount, amount, username, ))
                    self.db.commit()
                    pass
                elif kind == 2:
                    c.execute("""UPDATE user SET speed_drop = speed_drop + %s, upgrade_avai = upgrade_avai - %s
                    WHERE username = %s""", (amount, amount, username, ))
                    self.db.commit()
                    pass
                elif kind == 3:
                    c.execute("""UPDATE user SET speed_drag = speed_drag + %s, upgrade_avai = upgrade_avai - %s
                    WHERE username = %s""", (amount, amount, username, ))
                    self.db.commit()
                    pass
            pass
        pass
    """
    Close connection to mysql
    """
    def close(self):
        self.db.close()


