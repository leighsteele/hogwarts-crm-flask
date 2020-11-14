from validators.Validator import Validator

class ValidateFields(Validator):
    def __init__(self):
        super(ValidateFields, self).__init__()

    def validate(self, data):
        if type(data['first_name']) is not str:
            raise ValueError("first_name must be of type string")
        if data["first_name"] is None or len(data["first_name"]) == 0:
            raise ValueError("first_name is missing")

        if type(data['last_name']) is not str:
            raise ValueError("last_name must be of type string")
        if data["last_name"] is None or len(data["last_name"]) == 0:
            raise ValueError("last_name is missing")