import bcrypt
h = '$2b$12$R8HvY2IlfkyaiBS1h/d3keddNtl6VrlqrS7uz2HZ4MDomWGhXPZz2'
for pwd in ['admin123', 'admin1234', 'familia123', 'password123', 'familia', 'admin']:
    print(pwd, bcrypt.checkpw(pwd.encode(), h.encode()))
