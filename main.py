import mysql.connector as connector

class DBHelper:
    def __init__(self):
        self.con = connector.connect(host = 'localhost',
                                     port = '3306',
                                     user = 'root',
                                     password = '',
                                     database = 'testdb')

        query = "create table if not exists user(userId int primary key, userName varchar(200), phone varchar(12))"
        c = self.con.cursor()
        c.execute(query)
        print('Connection Created \n')

    # Insert User data
    def insert_user(self, userid, username, phone):
        query = "insert into user(userId, userName, phone) values({},'{}','{}')".format(userid, username, phone)
        print(query)
        c = self.con.cursor()
        c.execute(query)
        self.con.commit()
        print('User added to DB \n')

    # Fetch User data
    def fetch_all(self):
        query = "select * from user"
        c = self.con.cursor()
        c.execute(query)
        for row in c:
            print('User ID :', row[0])
            print('User Name :', row[1])
            print('Phone :', row[2])
            print()

    # Delete User data
    def delete_user(self, id):
        query = "delete from user where userId = {}".format(id)
        print(query)
        c = self.con.cursor()
        c.execute(query)
        self.con.commit()
        print('User deleted \n')

    # Update User
    def update_user(self, id, newName, newPhone):
        query = "update user set userName = '{}', phone = '{}' where userId = {}".format(newName, newPhone, id)
        print(query)
        c = self.con.cursor()
        c.execute(query)
        self.con.commit()
        print('User updated succesfully \n')


# main coding
helper = DBHelper()             # object for connectivity

# helper.insert_user(1002, 'Danereous Targerean', '1234567890')
# helper.insert_user(1003, 'John Snow', '9876543210')
# helper.insert_user(1004, 'Arya Stark', '2468013579')
# helper.insert_user(1005, 'Dothraki', '1357924680')
# helper.insert_user(1006, 'Khaleesi', '1231231230')

# helper.fetch_all()

# helper.delete_user(1005)
# helper.fetch_all()

# helper.update_user(1006, 'Sansa stark', '1231231230')
# helper.fetch_all()



