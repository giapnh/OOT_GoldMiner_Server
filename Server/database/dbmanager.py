# -*- coding: utf-8 -*-
__author__ = 'Nguyen Huu Giap'
import MySQLdb
import hashlib

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
        c = self.db.cursor()
        c.execute("""SELECT * FROM user where u_username = %s""",
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
        c.execute("""SELECT * FROM user where u_username = %s and u_password = %s""",
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
        c.execute("""INSERT INTO user(u_username, u_password) VALUES(%s, %s)""",
                  (username, hashlib.md5(password).hexdigest()))
        self.db.commit()
        pass
    """
    Get player information: username, level, ...
    """
    def get_user_info(self, username=""):
        c = self.db.cursor()
        c.execute("""SELECT u_username,u_level,u_levelup_point
         ,u_cup FROM user where u_username = %s""", (username, ))
        if c.rowcount == 1:
            row = c.fetchone()
            info = {"u_username": row[0], "u_level": row[1], "u_levelup_point": row[2], "u_cup": row[3]}
            return info
        else:
            return None

    def get_list_friend_mutual(self, username=""):
        c = self.db.cursor()
        c.execute("""SELECT *""")
        pass

    def get_list_friend_sent_invite(self, username=""):
        #TODO
        pass

    def get_list_friend_received_invite(self, username=""):
        #TODO
        pass

    def invite_friend(self, current_user="", friend=""):
        c = self.db.cursor()
        if not self.check_user_exits(current_user) or not self.check_user_exits(friend):
            return False
        else:
            c.execute("""SELECT u_id FROM user where u_username = %s""", (current_user, ))
            row = c.fetchone()
            from_id = int(row[0])
            c.execute("""SELECT u_id FROM user where u_username = %s""", (friend,))
            row2 = c.fetchone()
            to_id = int(row2[0])
            c.execute("""SELECT friendship_from, friendship_to FROM pending_friendship
            where friendship_from = %s and friendship_to = %s""",
                      (str(from_id), str(to_id)))
            if c.rowcount == 0:
                #Add to pending_friendship
                c.execute("""INSERT INTO pending_friendship(friendship_from, friendship_to)
                VALUES(%s, %s)""", (str(from_id), str(to_id)))
                self.db.commit()
                return True
            else:
                return False

    def accept_friend(self, current_user="", friend=""):
        c = self.db.cursor()
        if not self.check_user_exits(current_user) or not self.check_user_exits(friend):
            return False
        else:
            c.execute("""SELECT u_id FROM user where u_username = %s""", (current_user, ))
            row = c.fetchone()
            from_id = int(row[0])
            c.execute("""SELECT u_id FROM user where u_username = %s""", (friend,))
            row2 = c.fetchone()
            to_id = int(row2[0])
            #Add to pending_friendship
            c.execute("""INSERT INTO friendship(user1_id, user2_id)
            VALUES(%s, %s)""", (str(from_id), str(to_id)))
            self.db.commit()
            c.execute("""INSERT INTO friendship(user1_id, user2_id)
            VALUES(%s, %s)""", (str(to_id), str(from_id)))
            self.db.commit()
            return True

    def un_friend(self, current_user="", friend=""):
        c = self.db.cursor()
        if not self.check_user_exits(current_user) or not self.check_user_exits(friend):
            return False
        else:
            c.execute("""SELECT u_id FROM user where u_username = %s""", (current_user, ))
            row = c.fetchone()
            from_id = int(row[0])
            c.execute("""SELECT u_id FROM user where u_username = %s""", (friend,))
            row2 = c.fetchone()
            to_id = int(row2[0])
            #Add to pending_friendship
            c.execute("""DELETE FROM friendship WHERE user1_id = %s""", (from_id,))
            self.db.commit()
            c.execute("""DELETE FROM friendship WHERE user1_id = %s""", (to_id,))
            self.db.commit()
            return True

    """
    Close connection to mysql
    """
    def close(self):
        self.db.close()


