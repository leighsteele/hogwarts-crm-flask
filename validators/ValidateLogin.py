from validators.Validator import Validator

class ValidateLogin(Validator):
    def __init__(self):
        super(ValidateLogin, self).__init__()

    def validate(self, data):
        if type(data['email']) is not str:
            raise ValueError("email must be of type string")
        if data["email"] is None or len(data["email"]) == 0:
            raise ValueError("email is missing")

        if type(data['password']) is not str:
            raise ValueError("password must be of type string")
        if data["password"] is None or len(data["password"]) == 0:
            raise ValueError("password is missing")