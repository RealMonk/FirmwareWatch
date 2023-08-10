import sqlite3


class Memory:
    _conn = sqlite3.connect('chat_list.db')

    # create a connection and initialize DB
    def init_db(self):
        self._conn = sqlite3.connect('chat_list.db')
        c = self._conn.cursor()
        c.execute('''
                 CREATE TABLE IF NOT EXISTS chat_list
                ([chat_id] INTEGER PRIMARY KEY, [user_name] TEXT)
                ''')

        c.execute('''CREATE TABLE IF NOT EXISTS current_implemented_version
                ([firmware] TEXT PRIMARY KEY, [version_number] INTEGER)
                ''')
        c.execute('''
                INSERT OR IGNORE INTO current_implemented_version (firmware, version_number)
                VALUES ('BMC', 0)
        ''')
        c.execute('''
                INSERT OR IGNORE INTO current_implemented_version (firmware, version_number)
                VALUES ('BIOS', 0)
        ''')
        c.execute('pragma encoding')
        self._conn.commit()

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

    def get_user(self, chat_id):
        c = self._conn.cursor()
        c.execute('''
                SELECT * FROM chat_list
                WHERE chat_id = ?
                ''', (chat_id,))
        return c.fetchone()

    def implement_bmc(self, version_number):
        c = self._conn.cursor()
        c.execute('''
                UPDATE current_implemented_version
                SET version_number = ?
                WHERE firmware = ?
                ''', (version_number, 'BMC'))
        self._conn.commit()

    def implement_bios(self, version_number):
        c = self._conn.cursor()
        c.execute('''
                UPDATE current_implemented_version
                SET version_number = ?
                WHERE firmware = ?
                ''', (version_number, 'BIOS'))
        self._conn.commit()

    def deimplement_bmc(self):
        c = self._conn.cursor()
        c.execute('''
                UPDATE current_implemented_version
                SET version_number = ?
                WHERE firmware = ?
                ''', (0, 'BMC'))
        self._conn.commit()

    def deimplement_bios(self):
        c = self._conn.cursor()
        c.execute('''
                UPDATE current_implemented_version
                SET version_number = ?
                WHERE firmware = ?
                ''', (0, 'BIOS'))
        self._conn.commit()

    def get_bmc_version(self):
        c = self._conn.cursor()
        c.execute('''
                SELECT * FROM current_implemented_version
                WHERE firmware = 'BMC'
                ''')
        return c.fetchone()[1]

    def get_bios_version(self):
        c = self._conn.cursor()
        c.execute('''
                SELECT * FROM current_implemented_version
                WHERE firmware = 'BIOS'
                ''')
        return c.fetchone()[1]

if __name__ == '__main__':
    pass
