from app.control_db.control_db import ControlDB
from app.control_db.control_table import ControlTable

from app.core.config import DBNAME, USER, PASSWORD, HOST, PORT


сontrolDB = ControlDB()

connection, cursor = сontrolDB.connectDB(
                        connectConf={
                        'dbname': 'postgres',
                        'user': USER,
                        'password': PASSWORD,
                        'host': HOST,
                        'port': PORT
                        },
                        autocommit=True
                    )

exists = сontrolDB.checkingDB(DBNAME)
if not exists:
    сontrolDB.createDB(DBNAME)

connection, cursor = сontrolDB.connectDB(
                        connectConf={
                        'dbname': DBNAME,
                        'user': USER,
                        'password': PASSWORD,
                        'host': HOST,
                        'port': PORT
                        },
                        autocommit=True
                    )


сontrolTable = ControlTable(cursor)

сontrolTable.createTable(table_name="users", 
                        fields= [
                        {'name': 'login',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL CHECK (LENGTH(login) >= 3)'},

                        {'name': 'password',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL CHECK (LENGTH(password) >= 6)'}
                        ]
                    )

сontrolTable.createTable(table_name="containers", 
                        fields= [
                        {'name': 'user_id',
                            'dtype': 'INTEGER',
                            'constraints': 'NOT NULL'},
                        {'name': 'containers_name',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL'},
                        {'name': 'repositories_id',
                            'dtype': 'INTEGER',
                            'constraints': 'NOT NULL'},
                        {'name': 'version',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL'}
                        ]
                    )

сontrolTable.createTable(table_name="repositories", 
                        fields= [
                        {'name': 'user_id',
                            'dtype': 'INTEGER',
                            'constraints': 'NOT NULL'},
                        {'name': 'url',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL'},
                        {'name': 'repositories_name',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL'},
                        {'name': 'description',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL'}
                        ]
                    )

сontrolTable.createTable(table_name="version", 
                        fields= [
                        {'name': 'repositories_id',
                            'dtype': 'INTEGER',
                            'constraints': 'NOT NULL'},
                        {'name': 'version',
                            'dtype': 'VARCHAR(255)',
                            'constraints': 'NOT NULL'}
                        ],
                    )