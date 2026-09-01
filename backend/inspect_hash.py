h = '$2b$12$R8HvY2IlfkyaiBS1h/d3keddNtl6VrlqrS7uz2HZ4MDomWGhXPZz2'
print('len', len(h))
print('hash', h)
try:
    import bcrypt
    print('ok')
except Exception as e:
    print('bcrypt err', e)
