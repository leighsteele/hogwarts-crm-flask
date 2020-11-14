from flask import Flask, json, request
from flask_cors import CORS
import atexit

from decouple import config
from data.MysqlDataLayer import MysqlDataLayer
from people.Admin import Admin
from people.Student import Student
from skills.Skill import Skill

app = Flask(__name__)

CORS(app)

if config("DB") == "Mysql":
    datalayer = MysqlDataLayer()
# # to do
# else:
#     datalayer = MongoDataLayer()

@app.route("/")
def main():
    return app.response_class(response=json.dumps({"status": "ok"}), status=200, mimetype="application/json")

# GET REQUESTS
@app.route("/students")
def get_all_students():
    students = datalayer.get_all_students()
    return app.response_class(response=json.dumps({"students": students}))

@app.route("/students/datecount")
def get_count_per_day():
    count = datalayer.get_count_by_date()
    return app.response_class(response=json.dumps({"count": count}))

@app.route('/students/desiredskills')
def get_desired_skills_count():
    count = datalayer.desired_skill_count()
    return app.response_class(response=json.dumps(count))

@app.route('/students/existingskills')
def get_existing_skills_count():
    count = datalayer.count_existing_skills_by_type()
    return app.response_class(response=json.dumps({"skill_count": count}))

@app.route("/student/<id>")
def get_by_id(id):
    student = datalayer.get_student_by_id(id)
    return app.response_class(response=json.dumps({"students": student}))

# POST REQUESTS
@app.route('/skill', methods=['POST'])
def insert_skill():
    data = request.json
    datalayer.insert_skill(data["name"])
    return app.response_class(response=json.dumps({"status": "ok"}))

# insert student with skills
@app.route('/student', methods=['POST'])
def insert_student():
    data = request.json
    new_student = Student(data["first_name"], data["last_name"], data["house"])

    student_existing_skills = []
    student_desired_skills = []

    for key, value in data.items():
        if key == "existing_skills":
            for skill in value:
                existing_skill_obj = Skill(name=skill['name'], level=skill['level'])
                student_existing_skills.append(existing_skill_obj)

        if key == "desired_skills":
            for skill in value:
                desired_skill_obj = Skill(name=skill['name'], level=skill['level'])
                student_desired_skills.append(desired_skill_obj)

    datalayer.insert_student(new_student, student_existing_skills, student_desired_skills)

    return app.response_class(response=json.dumps({"status": "ok"}))

@app.route('/login', methods=['POST'])
def admin_login():
    try:
        data = request.json
        res = datalayer.admin_login(data['email'], data['password'])
        return app.response_class(response=json.dumps(res))
    except Exception as e:
        return str(e)

@app.route('/signup', methods=['POST'])
def admin_signup():
    try:
        data = request.json
        new_admin = Admin(data['firstName'], data['lastName'], data['password'])
        datalayer.admin_signup(new_admin)
        return app.response_class(response=json.dumps("Signup successful!"))
    except Exception as e:
        return str(e)

# PUT REQUESTS
@app.route('/student', methods=['PUT'])
def edit_student():
    try:
        data = request.json
        student_with_skills = Student.fromJson(data)
        datalayer.update_student(student_with_skills)
        return app.response_class(response=json.dumps("Student updated!"))
    except Exception as e:
        return str(e)

# DELETE REQUESTS
@app.route('/student/<id>', methods=['DELETE'])
def delete_student(id):
    try:
        datalayer.delete_student(id)
        return "Student deleted!"
    except Exception as e:
        return str(e)

@app.route('/students', methods=['DELETE'])
def delete_all_students():
    try:
        datalayer.delete_all_students()
        return "All students deleted"
    except Exception as e:
        return str(e)

@atexit.register
def goodbye():
    datalayer.shutdown()


if __name__ == "__main__":
    app.run()
