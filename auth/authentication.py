from bcrypt import hashpw, checkpw, gensalt


class Auth:
    @staticmethod
    def hash_password(password):
        return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

    @staticmethod
    def check_password(password, hashed_password):
        return checkpw(password.encode('utf-8'),
                       hashed_password.encode('utf-8'))


if __name__ == "__main__":
    user_pass = "Subbu"
    hash_password = Auth.hash_password(user_pass)
    print(Auth.check_password(user_pass, hash_password))
