from flask import Flask, render_template, request, redirect, url_for
import pyodbc
import os

app = Flask(__name__)

# Connexion Azure SQL Database
server = 'taskbasma.database.windows.net'
database = 'TaskDB'
username = 'basma'
password = 'Hamza@1234'
driver = '{ODBC Driver 17 for SQL Server}'

try:
    conn = pyodbc.connect(
        f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    )
    cursor = conn.cursor()
except Exception as e:
    print(f"Erreur de connexion à la base de données : {e}")
    raise

@app.route('/')
def home():
    return redirect(url_for('task_list'))

@app.route('/tasks')
def task_list():
    try:
        cursor.execute("SELECT * FROM Tasks")
        tasks = cursor.fetchall()
        return render_template('tasks.html', tasks=tasks)
    except Exception as e:
        return f"Erreur lors de la récupération des tâches : {e}", 500

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        desc = request.form['description']
        try:
            cursor.execute("INSERT INTO Tasks (description) VALUES (?)", (desc,))
            conn.commit()
            return redirect(url_for('task_list'))
        except Exception as e:
            return f"Erreur lors de la création de la tâche : {e}", 500
    return render_template('create.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        new_desc = request.form['description']
        completed = 1 if 'completed' in request.form else 0
        try:
            cursor.execute("UPDATE Tasks SET description=?, completed=? WHERE id=?", (new_desc, completed, id))
            conn.commit()
            return redirect(url_for('task_list'))
        except Exception as e:
            return f"Erreur lors de la mise à jour de la tâche : {e}", 500
    try:
        cursor.execute("SELECT * FROM Tasks WHERE id=?", (id,))
        task = cursor.fetchone()
        return render_template('edit.html', task=task)
    except Exception as e:
        return f"Erreur lors de la récupération de la tâche : {e}", 500

@app.route('/delete/<int:id>')
def delete(id):
    try:
        cursor.execute("DELETE FROM Tasks WHERE id=?", (id,))
        conn.commit()
        return redirect(url_for('task_list'))
    except Exception as e:
        return f"Erreur lors de la suppression de la tâche : {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))