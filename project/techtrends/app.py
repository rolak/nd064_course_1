from datetime import datetime
import sqlite3
import subprocess
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

DATABASE_DB = 'database.db'


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect(DATABASE_DB)
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


def get_db_connection_count():
    try:
        p = subprocess.Popen("lsof -w " + DATABASE_DB + " | wc -l", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        p_status = p.wait()
        return int(output)
    except:
        print("Unexpected error")
        return int(0)


def get_db_post_count():
    connection = get_db_connection()
    rowcount = connection.execute('SELECT COUNT(*) FROM posts').fetchone()
    connection.close()
    return rowcount[0]


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info(
            datetime.today().strftime(
                '%Y/%m/%d %H:%M:%S') + ', A non-existing article is accessed and a 404 page is returned.')
        return render_template('404.html'), 404
    else:
        app.logger.info(
            datetime.today().strftime('%Y/%m/%d %H:%M:%S') + ', Article "' + tuple(post)[2] + '" retrieved!')
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    app.logger.info(
        datetime.today().strftime(
            '%Y/%m/%d %H:%M:%S') + ', The "About Us" page is retrieved.')
    return render_template('about.html')


def check_application():
    try:
        connection = get_db_connection()
        connection.execute('SELECT * FROM posts').fetchall()
        connection.close()
        return True
    except:
        return False


@app.route('/healthz')
def healthy():
    app.logger.info('Healthz request')

    if not check_application():
        return app.response_class(
            response=json.dumps({"result": "ERROR - unhealthy"}),
            status=500,
            mimetype='application/json'
        )

    return app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )


@app.route('/metrics')
def metrics():
    response = app.response_class(
        response=json.dumps({"db_connection_count": get_db_connection_count(), "post_count": get_db_post_count()}),
        status=200,
        mimetype='application/json'
    )

    app.logger.info('Metrics request successfull')
    return response


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()

            app.logger.info(
                datetime.today().strftime(
                    '%Y/%m/%d %H:%M:%S') + ', A new article is created. The title of the new article should be recorded in the logline.')

            return redirect(url_for('index'))

    return render_template('create.html')


# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S')
    app.run(host='0.0.0.0', port='3111')
