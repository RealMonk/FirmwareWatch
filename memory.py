import sqlite3


class Memory:
    _conn = sqlite3.connect('chat_list.db')

    # create a connection and initialize DB
    ########################################
    def init_db(self):
        self._conn = sqlite3.connect('chat_list.db')
        c = self._conn.cursor()
        c.execute('''
                 CREATE TABLE IF NOT EXISTS chat_list
                ([chat_id] INTEGER PRIMARY KEY, [user_name] TEXT)
                ''')
        self._conn.commit()
    ########################################

    def add_user(self, chat_id, user_name):
        c = self._conn.cursor()
        c.execute('''
                INSERT INTO chat_list (chat_id, user_name)
                VALUES (?, ?)
                ''', (chat_id, user_name))
        self._conn.commit()

    def delete_user(self, chat_id):
        c = self._conn.cursor()
        c.execute('''
                DELETE FROM chat_list
                WHERE chat_id = ?
                ''', (chat_id,))
        self._conn.commit()

    def get_all_users(self):
        c = self._conn.cursor()
        c.execute('''
                SELECT * FROM chat_list
                ''')
        return c.fetchall()


if __name__ == '__main__':
    pass
