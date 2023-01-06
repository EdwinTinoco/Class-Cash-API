from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_heroku import Heroku
import bcrypt
import os

app = Flask(__name__)
CORS(app)  
heroku = Heroku(app)

app.config['MYSQL_HOST'] = os.environ.get('HOST')
app.config['MYSQL_USER'] = os.environ.get('USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('DB')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


# Enpoints for Home page ------------------------------------------------------------------------------
@app.route('/')
def home():    
    return "<h1>Class Cash API</h1>"


# Enpoints for Students table------------------------------------------------------------------------
# POST STUDENT
@app.route('/add-student', methods=['POST'])
def add_student():   
   students_first_name = request.json['students_first_name']
   students_last_name = request.json['students_last_name']
   students_gender = request.json['students_gender']
   students_image_url = request.json['students_image_url']
   students_grades_id = request.json['students_grades_id']
   students_grades_groups_id = request.json['students_grades_groups_id']
   bank_current_total = request.json['bank_current_total']
   
   cur = mysql.connection.cursor()
   cur.callproc("spInsertNewStudent",
   [students_first_name, students_last_name, students_gender, students_image_url, 
   students_grades_id, students_grades_groups_id, bank_current_total])

   mysql.connection.commit()
   cur.close()

   return jsonify('Student inserted successfully')

# GET STUDENTS BY GRADE AND GROUP
@app.route('/students/<id>', methods=["GET"])
def get_all_students(id):    
   cur = mysql.connection.cursor()
   cur.callproc("spGetStudents", [id])
   all_students = cur.fetchall()

   cur.close()

   return jsonify(all_students)

# GET ONE STUDENT
@app.route('/student/<id>', methods=['GET'])
def get_student(id):
   cur = mysql.connection.cursor()
   cur.callproc("spGetStudentById", [id])
   student = cur.fetchall()

   cur.close()
   
   return jsonify(student)   

# PUT STUDENT
@app.route('/student-update/<id>', methods=['PUT'])
def update_student(id):
   students_first_name = request.json['students_first_name']
   students_last_name = request.json['students_last_name']
   students_image_url = request.json['students_image_url']
   students_gender = request.json['students_gender']
   bank_current_total = request.json['bank_current_total']

   cur = mysql.connection.cursor()
   cur.callproc("spUpdateStudentById",
   [id, students_first_name, students_last_name, students_image_url, students_gender, bank_current_total])

   mysql.connection.commit()
   cur.close()

   return jsonify('Student updated successfully')

# DELETE STUDENT
@app.route('/delete-student/<id>', methods=['DELETE'])
def delete_student(id):
   cur = mysql.connection.cursor()
   cur.callproc("spDelStudentById", [id])
   mysql.connection.commit()

   cur.close()    

   return jsonify('Student deleted succesfully!') 


# Enpoints for Bank table------------------------------------------------------------------------
# PATCH
@app.route('/update-bank/<id>', methods=['PATCH'])
def update_bank_current_total(id):
   bank_current_total = request.json['bank_current_total']

   cur = mysql.connection.cursor()
   cur.callproc("spUpdateBankCurrentTotalByStudentId", [id, bank_current_total])

   mysql.connection.commit()
   cur.close()

   return jsonify('bank_current_total updated successfully')


# Enpoints for Users table------------------------------------------------------------------------
# POST TO REGISTER USER
@app.route('/register', methods=['POST'])
def register_user():   
   users_first_name = request.json['users_first_name']
   users_last_name = request.json['users_last_name']
   users_phone_number = request.json['users_phone_number']
   users_grades_id = request.json['users_grades_id']
   users_email = request.json['users_email']
   users_password = request.json['users_password']
   users_active = request.json['users_active']

   cur = mysql.connection.cursor()
   cur.callproc("spCheckEmailExist", ())
   emails = cur.fetchall()
   cur.close() 

   ban = False
   for row in emails:
      if row['users_email'] == users_email:
         ban = True

   if ban:
      return 'A user with that email already exist'
   else:
      hashed = bcrypt.hashpw(users_password.encode('utf-8'), bcrypt.gensalt())
      
      cur = mysql.connection.cursor()
      cur.callproc("spInsertNewUser",
      [users_first_name, users_last_name, users_phone_number, users_grades_id, users_email, 
      hashed, users_active])

      mysql.connection.commit()
      cur.close()

      return jsonify('User registered successfully')

# POST LOGIN USER
@app.route('/login', methods=['POST'])
def login_user():
   users_email = request.json['email']
   users_password = request.json['password']  

   cur = mysql.connection.cursor()
   cur.callproc("spCheckEmailExist", ())
   emails = cur.fetchall()
   cur.close() 

   ban = False
   for row in emails:
      if row['users_email'] == users_email:
         ban = True
         hash_password = row["users_password"]

   if ban:      
      if bcrypt.checkpw(users_password.encode('utf-8'), hash_password.encode('utf-8')):
         cur = mysql.connection.cursor()
         cur.callproc("spLoginUser", [users_email, hash_password])
         user = cur.fetchall()
         cur.close()

         return jsonify(user)         
      else:
         return "Email or password is wrong"
   else:
      return "Email or password is wrong"

# GET CURRENT USER
@app.route('/user/<id>', methods=['GET'])
def get_user(id):
   cur = mysql.connection.cursor()
   cur.callproc("spGetUserById", [id])
   user = cur.fetchall()

   cur.close()

   return jsonify(user)

# DELETE USER
@app.route('/delete-user/<id>', methods=['DELETE'])
def delete_user(id):
   cur = mysql.connection.cursor()
   cur.callproc("spDeleteUserById", [id])
   mysql.connection.commit()

   cur.close()    

   return jsonify('User deleted')


# Enpoints for grades table------------------------------------------------------------------------------
# GET ALL GRADES 
@app.route('/grades', methods=['GET'])
def get_all_grades():
   cur = mysql.connection.cursor()
   cur.callproc("spGetAllGrades", ())
   all_grades = cur.fetchall()

   cur.close()
  
   return jsonify(all_grades)  


# Enpoints for grades_groups table------------------------------------------------------------------------
# GET GROUPS BY USER ID
@app.route('/grades-groups/<id>', methods=['GET'])
def get_grades_groups(id):
   cur = mysql.connection.cursor()
   cur.callproc("spGetGradesGroupsByUserId", [id])
   grades_groups = cur.fetchall()

   cur.close()
  
   return jsonify(grades_groups)   

# GET GROUPS BY GRADES ID
@app.route('/groups/<id>', methods=['GET'])
def get_grades_groups_by_gradesId(id):
   cur = mysql.connection.cursor()
   cur.callproc("spGetGradesGroupsByGradesId", [id])
   groups = cur.fetchall()

   cur.close()
  
   return jsonify(groups) 

# POST ADD GROUP
@app.route('/grades-groups/add-group', methods=['POST'])
def add_group():
   grades_groups_name = request.json['grades_groups_name']
   grades_groups_grades_id = request.json['grades_groups_grades_id']
   grades_groups_users_id = request.json['grades_groups_users_id']

   cur = mysql.connection.cursor()
   cur.callproc("spInsertNewGroup", [grades_groups_name, grades_groups_grades_id, grades_groups_users_id])
   mysql.connection.commit()

   cur.callproc("spGetLastGroupInserted", ())
   group = cur.fetchall()

   cur.close()
   
   return jsonify(group)

# PATCH UPDATE GROUP NAME
@app.route('/update-group/<id>', methods=['PATCH'])
def update_group_name(id):
   grades_groups_name = request.json['grades_groups_name']

   cur = mysql.connection.cursor()
   cur.callproc("spUpdateGroupNameById", [id, grades_groups_name])
   mysql.connection.commit()

   cur.close()    

   return jsonify('Group name updated succesfully')

# DELETE GROUP BY ID
@app.route('/delete-group/<id>', methods=['DELETE'])
def delete_group(id):
   cur = mysql.connection.cursor()
   cur.callproc("spDeleteGroupById", [id])
   mysql.connection.commit()

   cur.close()    

   return jsonify('Group deleted')


# Enpoints for profile_image table------------------------------------------------------------------------
# GET ALL PROFILES IMAGES
@app.route('/profile-image', methods=["GET"])
def get_all_profile_images():    
   cur = mysql.connection.cursor()
   cur.callproc("spGetAllProfileImages", ())
   all_profile_images = cur.fetchall()

   cur.close()

   return jsonify(all_profile_images)




if __name__ == '__main__':
    app.run(debug=True)