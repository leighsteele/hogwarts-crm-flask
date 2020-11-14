from people.Person import Person

class Admin(Person):
    def __init__(self, first_name, last_name, password):
        super(Admin, self).__init__(first_name, last_name)
        self.password = password

    def __str__(self):
        return str.format("Admin Name: {}, {}; Email: {}", self.last_name, self.first_name, self.email)

    @classmethod
    def fromJson(cls, json_string):
        admin_data = json_string

        admin = cls(first_name=admin_data['first_name'], last_name=admin_data['last_name'],
                      password=admin_data['password'])

        return admin

