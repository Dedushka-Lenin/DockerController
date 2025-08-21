tables = {
    'users':[
    {'name': 'login',
        'dtype': 'VARCHAR(255)',
        'constraints': 'NOT NULL CHECK (LENGTH(login) >= 3)'},
    {'name': 'password',
        'dtype': 'VARCHAR(255)',
        'constraints': 'NOT NULL CHECK (LENGTH(password) >= 6)'}
    ],
    'containers':[
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
    ],
    'containers':[
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
    ],
    'version':[
    {'name': 'repositories_id',
        'dtype': 'INTEGER',
        'constraints': 'NOT NULL'},
    {'name': 'version',
        'dtype': 'VARCHAR(255)',
        'constraints': 'NOT NULL'}
    ]
}