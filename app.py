from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            branch TEXT,
            year INTEGER
        )
    """)
    conn.commit()
    conn.close()

create_table()

# ---------- HTML TEMPLATE ----------
template = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Management</title>
</head>
<body>
    <h2>Add Student</h2>
    <form method="POST" action="/add">
        Name: <input name="name" required>
        Branch: <input name="branch" required>
        Year: <input name="year" type="number" required>
        <button>Add</button>
    </form>

    <h2>Students List</h2>
    <table border="1">
        <tr><th>ID</th><th>Name</th><th>Branch</th><th>Year</th><th>Action</th></tr>
        {% for s in students %}
        <tr>
            <td>{{s.id}}</td>
            <td>{{s.name}}</td>
            <td>{{s.branch}}</td>
            <td>{{s.year}}</td>
            <td>
                <a href="/edit/{{s.id}}">Edit</a> |
                <a href="/delete/{{s.id}}">Delete</a>
            </td>
        </tr>
        {% endfor %}
    </table>

    {% if edit %}
    <h2>Edit Student</h2>
    <form method="POST" action="/update/{{edit.id}}">
        Name: <input name="name" value="{{edit.name}}">
        Branch: <input name="branch" value="{{edit.branch}}">
        Year: <input name="year" value="{{edit.year}}">
        <button>Update</button>
    </form>
    {% endif %}
</body>
</html>
"""

# ---------- ROUTES ----------
@app.route("/")
def index():
    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template_string(template, students=students, edit=None)

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    branch = request.form["branch"]
    year = request.form["year"]

    conn = get_db()
    conn.execute("INSERT INTO students (name, branch, year) VALUES (?, ?, ?)",
                 (name, branch, year))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/edit/<int:id>")
def edit(id):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template_string(template, students=students, edit=student)

@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    name = request.form["name"]
    branch = request.form["branch"]
    year = request.form["year"]

    conn = get_db()
    conn.execute("UPDATE students SET name=?, branch=?, year=? WHERE id=?",
                 (name, branch, year, id))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
