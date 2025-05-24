from flask import Flask, render_template, request, redirect, url_for
import pyodbc

app = Flask(__name__)

# Connexion Azure SQL Database
server = 'taskbasma.database.windows.net'
database = 'TaskDB'
username = 'basma'
password = 'Hamza@1234'
driver = '{ODBC Driver 17 for SQL Server}'

conn = pyodbc.connect(
    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
)
cursor = conn.cursor()

@app.route('/')
def home():
    return redirect(url_for('task_list'))

@app.route('/tasks')
def task_list():
    cursor.execute("SELECT * FROM Tasks")
    tasks = cursor.fetchall()
    return render_template('tasks.html', tasks=tasks)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        desc = request.form['description']
        cursor.execute("INSERT INTO Tasks (description) VALUES (?)", (desc,))
        conn.commit()
        return redirect(url_for('task_list'))
    return render_template('create.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        new_desc = request.form['description']
        completed = 1 if 'completed' in request.form else 0
        cursor.execute("UPDATE Tasks SET description=?, completed=? WHERE id=?", (new_desc, completed, id))
        conn.commit()
        return redirect(url_for('task_list'))
    cursor.execute("SELECT * FROM Tasks WHERE id=?", (id,))
    task = cursor.fetchone()
    return render_template('edit.html', task=task)

@app.route('/delete/<int:id>')
def delete(id):
    cursor.execute("DELETE FROM Tasks WHERE id=?", (id,))
    conn.commit()
    return redirect(url_for('task_list'))

if __name__ == '__main__':
    app.run(debug=True)
