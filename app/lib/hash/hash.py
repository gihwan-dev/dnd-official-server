import bcrypt


def hashPassword(enteredPassword: str):
    encodedPassword = enteredPassword.encode('utf-8')

    salt = bcrypt.gensalt(rounds=12)

    hashedPassword = bcrypt.hashpw(encodedPassword, salt)

    return hashedPassword.decode('utf-8')


def comparePassword(enteredPassword: str, hashed_password: str):
    encodedEnteredPassword = enteredPassword.encode('utf-8')
    encodedHashedPassword = hashed_password.encode('utf-8')

    return bcrypt.checkpw(encodedEnteredPassword, encodedHashedPassword)
