from toon_format import decode, encode

data = {
    'tool_message': {
        'basic': {
            'schema': 'ai_compute_modeller',
            'name': 'user_roles',
            'type': 'table',
        },
        'columns': [
            {
                'column': 'user_role_id',
                'data_type': 'integer',
                'is_nullable': 'NO',
                'default': "nextval('ai_compute_modeller.user_roles_user_role_id_seq'::regclass)",
            },
            {
                'column': 'user_id',
                'data_type': 'integer',
                'is_nullable': 'YES',
                'default': None,
            },
            {
                'column': 'role_id',
                'data_type': 'integer',
                'is_nullable': 'YES',
                'default': None,
            },
            {
                'column': 'created_on',
                'data_type': 'timestamp without time zone',
                'is_nullable': 'YES',
                'default': None,
            },
            {
                'column': 'created_by',
                'data_type': 'text',
                'is_nullable': 'YES',
                'default': None,
            },
            {
                'column': 'updated_on',
                'data_type': 'timestamp without time zone',
                'is_nullable': 'YES',
                'default': None,
            },
            {
                'column': 'updated_by',
                'data_type': 'text',
                'is_nullable': 'YES',
                'default': None,
            },
            {
                'column': 'is_default',
                'data_type': 'boolean',
                'is_nullable': 'YES',
                'default': 'false',
            },
            {
                'column': 'organization_id',
                'data_type': 'integer',
                'is_nullable': 'YES',
                'default': None,
            },
        ],
        'constraints': [
            {
                'name': 'user_roles_pkey',
                'type': 'PRIMARY KEY',
                'columns': ['user_role_id'],
            },
            {
                'name': 'user_roles_user_id_unique',
                'type': 'UNIQUE',
                'columns': ['user_id'],
            },
            {
                'name': 'fk_role_user_roles',
                'type': 'FOREIGN KEY',
                'columns': ['role_id'],
            },
            {
                'name': 'fk_user_roles_user_id',
                'type': 'FOREIGN KEY',
                'columns': ['user_id'],
            },
            {
                'name': 'user_roles_role_id_fkey',
                'type': 'FOREIGN KEY',
                'columns': ['role_id'],
            },
            {
                'name': 'user_roles_user_id_fkey',
                'type': 'FOREIGN KEY',
                'columns': ['user_id'],
            },
            {'name': '16438_16684_1_not_null', 'type': 'CHECK', 'columns': []},
        ],
        'indexes': [
            {
                'name': 'user_roles_pkey',
                'definition': 'CREATE UNIQUE INDEX user_roles_pkey ON ai_compute_modeller.user_roles USING btree (user_role_id)',
            },
            {
                'name': 'user_roles_user_id_unique',
                'definition': 'CREATE UNIQUE INDEX user_roles_user_id_unique ON ai_compute_modeller.user_roles USING btree (user_id)',
            },
        ],
    }
}
print(type(data))
encoded = encode(data)
# print(type(encoded))
decoded = decode(encoded)
print("__ " * 45)
print(decoded)
print(encoded)
