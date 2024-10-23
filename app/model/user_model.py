class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __str__(self):
        return f'{self.email}, {self.password}'