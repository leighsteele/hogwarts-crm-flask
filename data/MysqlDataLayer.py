import mysql.connector
from decouple import config
from data.BaseDataLayer import BaseDataLayer
from people.Student import Student
from skills.Skill import Skill

class MysqlDataLayer(BaseDataLayer):
    def __init__(self):
        super().__init__()
        self.__connect()

    def __connect(self):
        self.__db = mysql.connector.connect(
            host="localhost",
            user=config('MYSQL_USER'),
            password=config('PASSWORD'),
            database="hogwarts"
        )
        self.__db.autocommit = False

    def shutdown(self):
        self.__db.close()

    # get all students with their skills
    def get_all_students(self):
        try:
            cursor = self.__db.cursor(dictionary=True)
            sql = "SELECT * FROM students " \
                  "INNER JOIN student_skills " \
                  "ON students.idstudents = student_skills.student_id " \
                  "INNER JOIN magic_skills " \
                  "ON student_skills.skill_id = magic_skills.idmagic_skills"
            cursor.execute(sql,)
            res = cursor.fetchall()

            students_dict = {}

            for student in res:
                new_student_obj = Student.fromJson(student)
                students_dict[student['idstudents']] = new_student_obj

            for skill in res:
                new_skill_obj = Skill(skill['name'], skill['level'])

                for k, v in students_dict.items():
                    if skill['student_id'] == k:
                        if skill['type'] == 'existing':
                            v.existing_skills.append(new_skill_obj)
                        else:
                            v.desired_skills.append(new_skill_obj)

            # convert nested objects to dicts
            students_list = []
            for k, v in students_dict.items():
                for index, value in enumerate(v.existing_skills):
                    v.existing_skills[index] = value.__dict__

                for index, value in enumerate(v.desired_skills):
                    v.desired_skills[index] = value.__dict__

                students_list.append(v.__dict__)

            return students_list

        finally:
            cursor.close()

    def get_student_by_id(self, id):
        try:
            cursor = self.__db.cursor()
            sql = "SELECT first_name,last_name FROM students WHERE idstudents=%s"
            cursor.execute(sql, (id,))
            res = cursor.fetchone()
            return res
        finally:
            cursor.close()

    def desired_skill_count(self):
        try:
            cursor = self.__db.cursor(dictionary=True)
            sql = "SELECT `skill_id`, count(*) FROM student_skills WHERE `type` LIKE 'desired' GROUP BY `skill_id`"
            cursor.execute(sql,)
            res = cursor.fetchall()
            print(res)

            count_dict = {}

            for skill_count in res:
                skill_name = self.get_skill_name(skill_count['skill_id'])
                count_dict[skill_name] = skill_count['count(*)']

            print(count_dict)
            return count_dict

        except mysql.connector.Error as error:
            print(error)

        finally:
            cursor.close()

    def get_skill_name(self, skill):
        try:
            cursor = self.__db.cursor()
            sql = "SELECT name from magic_skills " \
                  "where idmagic_skills = %s"
            val = (skill,)
            cursor.execute(sql, val)
            res = cursor.fetchone()
            return res[0]

        except mysql.connector.Error as error:
            print(error)

        finally:
            cursor.close()

    # add data to db
    def get_skill_id(self, skill):
        try:
            cursor = self.__db.cursor()
            sql = "SELECT idmagic_skills from magic_skills " \
                  "where name = %s"
            val = (skill.name,)
            cursor.execute(sql, val)
            res = cursor.fetchone()
            return res[0]

        except mysql.connector.Error as error:
            print(error)

        finally:
            cursor.close()

    def insert_student(self, student, existing_skills, desired_skills):
        try:
            cursor = self.__db.cursor()
            sql = "INSERT INTO students (first_name, last_name, email, created_at, last_modified, house) " \
                  "VALUES (%s, %s, %s, %s, %s, %s)"
            val = (student.first_name, student.last_name, student.email, student.created_at, student.last_modified, student.house)
            cursor.execute(sql, val)
            print(cursor.rowcount, "record inserted.")

            student_id = cursor.lastrowid

            for skill in existing_skills:
                ex_skill_type = 'existing'
                skill_id = self.get_skill_id(skill)
                # create the row for student_skill
                skill_sql = "INSERT INTO student_skills (skill_id, student_id, level, type) VALUES (%s, %s, %s, %s)"
                skill_val = (skill_id, student_id, skill.level, ex_skill_type)
                cursor.execute(skill_sql, skill_val)
                print(cursor.rowcount, "skill record inserted.")

            for skill in desired_skills:
                des_skill_type = 'desired'
                skill_id = self.get_skill_id(skill)
                skill_sql = "INSERT INTO student_skills (skill_id, student_id, level, type) VALUES (%s, %s, %s, %s)"
                skill_val = (skill_id, student_id, skill.level, des_skill_type)
                cursor.execute(skill_sql, skill_val)
                print(cursor.rowcount, "skill record inserted.")

            self.__db.commit()

        except mysql.connector.Error as error:
            print("Failed to update record to database rollback: {}".format(error))
            self.__db.rollback()

        finally:
            cursor.close()

    def delete_student_skills(self, id):
        try:
            cursor = self.__db.cursor()
            sql = "DELETE FROM student_skills WHERE student_id = %s"
            val = (id,)
            cursor.execute(sql, val)
            self.__db.commit()

        except mysql.connector.Error as error:
            print("Failed to delete record from table: {}".format(error))

        finally:
            cursor.close()

    # delete a specific row in a table
    def delete_student(self, id):
        try:
            cursor = self.__db.cursor()

            self.delete_student_skills(id)

            sql = "DELETE FROM students WHERE idstudents = %s"
            val = (id,)
            cursor.execute(sql, val)
            self.__db.commit()

            print(cursor.rowcount, "record(s) deleted")
            if cursor.rowcount == 0:
                raise Exception("Failed to delete record")
            else:
                return "OK"

        except mysql.connector.Error as error:
            print("Failed to delete record from table: {}".format(error))
            self.__db.rollback()

        finally:
            cursor.close()

    # delete all rows in a table
    def delete_all_students(self):
        try:
            cursor = self.__db.cursor()
            sql = "DELETE FROM students"
            cursor.execute(sql,)
            print(cursor.rowcount, "record(s) deleted")
            self.__db.commit()

        except mysql.connector.Error as error:
            print(error)

        finally:
            cursor.close()

    # edit student
    def update_student(self, student):
        try:
            cursor = self.__db.cursor()
            sql = "UPDATE students " \
                  "SET first_name=%s, last_name=%s, email=%s, created_at=%s, last_modified=%s, house=%s " \
                  "WHERE idstudents=%s"
            val = (student.first_name, student.last_name, student.email, student.created_at, student.last_modified,
                   student.house, student.ID)
            cursor.execute(sql, val)
            print(cursor.rowcount, "record updated.")

            # delete all skills associated with student
            self.delete_student_skills(student.ID)
            self.__db.commit()

            cursor = self.__db.cursor()
            # insert new skills data
            for skill in student.existing_skills:
                ex_skill_type = 'existing'
                skill_id = self.get_skill_id(skill)
                skill_sql = "INSERT INTO student_skills (skill_id, student_id, level, type) VALUES (%s, %s, %s, %s)"
                skill_val = (skill_id, student.ID, skill.level, ex_skill_type)
                cursor.execute(skill_sql, skill_val)
                print(cursor.rowcount, "skill record inserted.")

            for skill in student.desired_skills:
                des_skill_type = 'desired'
                skill_id = self.get_skill_id(skill)
                skill_sql = "INSERT INTO student_skills (skill_id, student_id, level, type) VALUES (%s, %s, %s, %s)"
                skill_val = (skill_id, student.ID, skill.level, des_skill_type)
                cursor.execute(skill_sql, skill_val)
                print(cursor.rowcount, "skill record inserted.")

            self.__db.commit()

        except mysql.connector.Error as error:
            print("Failed to update record to database rollback: {}".format(error))
            self.__db.rollback()

        finally:
            cursor.close()

    def admin_login(self, email, password):
        try:
            cursor = self.__db.cursor()
            sql = "SELECT * FROM admin_users WHERE email = %s AND password = %s"
            val = (email, password)
            cursor.execute(sql, val)
            cursor.fetchone()

            if cursor.rowcount == 1:
                return "Login successful!"
            else:
                raise Exception("Login unsuccessful")

        except mysql.connector.Error as error:
            print(error)

        finally:
            cursor.close()

    def admin_signup(self, admin):
        try:
            cursor = self.__db.cursor()

            sql = "INSERT INTO admin_users (first_name, last_name, email, password) " \
                  "VALUES (%s, %s, %s, %s)"
            val = (admin.first_name, admin.last_name, admin.email, admin.password)
            cursor.execute(sql, val)
            print(cursor.rowcount, "record inserted.")
            self.__db.commit()

        except mysql.connector.Error as error:
            print("Failed to update record to database rollback: {}".format(error))
            self.__db.rollback()

        finally:
            cursor.close()