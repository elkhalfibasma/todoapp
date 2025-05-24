from flask import Flask, render_template, request, redirect, url_for
import pyodbc
import os

app = Flask(__name__)

# Chaîne de connexion Azure SQL Database
connection_string = (
    "Server=tcp:taskbasma.database.windows.net,1433;"
    "Initial Catalog=TaskDB;"
    "Persist Security Info=False;"
    "User ID=basma;"
    "Password=Hamza@1234;"  # Vérifie que ce mot de passe est correct
    "MultipleActiveResultSets=False;"
    "Encrypt=True;"
    "TrustServerCertificate=False;"
    "Connection Timeout=30;"
)

def get_db_connection():
    """Crée et retourne une connexion à la base de données."""
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        raise Exception(f"Erreur de connexion à la base de données : {e}")

@app.route('/test')
def test():
    """Route de test sans dépendance à la base de données."""
    return "L'application fonctionne !"

@app.route('/')
def home():
    return redirect(url_for('task_list'))

@app.route('/tasks')
def task_list():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tasks")
        tasks = [{'id': row[0], 'description': row[1], 'completed': row[2]} for row in cursor.fetchall()]  # Ajuste les indices selon ta table
        cursor.close()
        conn.close()
        return render_template('tasks.html', tasks=tasks)
    except Exception as e:
        return f"Erreur lors de la récupération des tâches : {e}", 500

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        desc = request.form['description']
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Tasks (description) VALUES (?)", (desc,))
            conn.commit()
            cursor.close()
            conn.close()
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
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Tasks SET description=?, completed=? WHERE id=?", (new_desc, completed, id))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('task_list'))
        except Exception as e:
            return f"Erreur lors de la mise à jour de la tâche : {e}", 500
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tasks WHERE id=?", (id,))
        row = cursor.fetchone()
        task = {'id': row[0], 'description': row[1], 'completed': row[2]} if row else None  # Ajuste les indices
        cursor.close()
        conn.close()
        return render_template('edit.html', task=task)
    except Exception as e:
        return f"Erreur lors de la récupération de la tâche : {e}", 500

@app.route('/delete/<int:id>')
def delete(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Tasks WHERE id=?", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('task_list'))
    except Exception as e:
        return f"Erreur lors de la suppression de la tâche : {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))