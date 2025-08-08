from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["school_db"]
students_collection = db["students"]

# ----------------------
# Grade Calculation Logic
# ----------------------
def calculate_grade(marks):
    average = sum(marks.values()) / len(marks)
    if average >= 90:
        grade = "A+"
    elif average >= 80:
        grade = "A"
    elif average >= 70:
        grade = "B"
    elif average >= 60:
        grade = "C"
    else:
        grade = "F"
    return average, grade

# ----------------------
# Routes
# ----------------------

@app.route('/')
def index():
    students = students_collection.find()
    return render_template("index.html", students=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        marks = {
            'math': int(request.form['math']),
            'science': int(request.form['science']),
            'english': int(request.form['english']),
        }

        avg, grade = calculate_grade(marks)

        student = {
            'name': name,
            'roll': roll,
            'marks': marks,
            'average': avg,
            'grade': grade
        }

        students_collection.insert_one(student)
        return redirect(url_for('index'))
    
    return render_template("add_student.html")

@app.route('/update/<roll>', methods=['GET', 'POST'])
def update_student(roll):
    student = students_collection.find_one({'roll': roll})
    if not student:
        return "Student not found", 404

    if request.method == 'POST':
        marks = {
            'math': int(request.form['math']),
            'science': int(request.form['science']),
            'english': int(request.form['english']),
        }
        avg, grade = calculate_grade(marks)

        students_collection.update_one(
            {'roll': roll},
            {'$set': {
                'marks': marks,
                'average': avg,
                'grade': grade
            }}
        )
        return redirect(url_for('index'))
    
    return render_template("update_student.html", student=student)

@app.route('/delete/<roll>')
def delete_student(roll):
    students_collection.delete_one({'roll': roll})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
