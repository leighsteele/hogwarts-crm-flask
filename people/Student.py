from datetime import datetime as datetime_class
import datetime

from people.Person import Person
from skills.Skill import Skill
from validators.ValidateFields import ValidateFields

class Student(Person):
    def __init__(self, first_name, last_name, house):
        super(Student, self).__init__(first_name, last_name)
        self.ID = None
        self.created_at = datetime_class.now().strftime("%Y_%m_%d")
        self.last_modified = None
        self.house = house
        self.existing_skills = []
        self.desired_skills = []

    def __str__(self):
        return str.format("Student ID: {}, Student Name: {}, {}; Existing Skills: {}, Desired Skills: {}", self.ID, self.last_name, self.first_name, self.existing_skills, self.desired_skills)

    def get_last_name(self):
        return self.last_name

    def get_email(self):
        return self.email

    def add_existing_skill(self, skill):
        self.existing_skills.append(skill)

    def add_desired_skill(self, skill):
        self.desired_skills.append(skill)

    def get_existing_skills(self):
        return self.existing_skills

    def get_desired_skills(self):
        return self.desired_skills

    @classmethod
    def fromJson(cls, json_string):
        student_data = json_string

        # validations
        validator = ValidateFields()
        validator.validate(student_data)

        student = cls(first_name=student_data['first_name'], last_name=student_data['last_name'], house=student_data['house'])

        # existing skill instance
        for key, value in student_data.items():
            if key == 'existing_skills':
                for skill in value:
                    existing_skill_obj = Skill(name=skill['name'], level=skill['level'])
                    student.existing_skills.append(existing_skill_obj)

        # desired skill instance
        for key, value in student_data.items():
            if key == 'desired_skills':
                for skill in value:
                    desired_skill_obj = Skill(name=skill['name'], level=skill['level'])
                    student.desired_skills.append(desired_skill_obj)

        # to not override previous created_at / last_updated time
        for key, value in student_data.items():
            if key == 'created_at':
                if value is not None:
                    student.created_at = student_data['created_at']
                else:
                    student.created_at = datetime.now().strftime("%d_%m_%Y")

            if key == 'last_updated':
                if value is not None:
                    student.last_updated = student_data['last_updated']
                else:
                    student.last_updated = datetime.now().strftime("%d_%m_%Y, %H:%M:%S")

            if key == 'idstudents':
                if value is not None:
                    student.ID = student_data['idstudents']
                else:
                    student.ID = None

            if key == 'ID':
                if value is not None:
                    student.ID = student_data['ID']
                else:
                    student.ID = None

        return student
