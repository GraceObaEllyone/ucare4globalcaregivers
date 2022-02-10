from flask import Flask, render_template, json, request
from flaskext.mysql import MySQL


mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'grace'
app.config['MYSQL_DATABASE_PASSWORD'] = 'grace'
app.config['MYSQL_DATABASE_DB'] = 'GraceBlogApp'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)



@app.route('/')
def homePage(title="Iam-Global CareGiver"):  # put application's code here
    return render_template("index.html", title=title)


@app.route('/about')
def aboutPage(title="About Page"):
    return render_template("about.html", title=title)

@app.route('/blog/<title_blog>')
def blogPage(title_blog=None):
    return render_template("blog-post.html", title_blog=title_blog)

@app.route('/grace')
def grace():
    return "This is grace page"


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:

            # All Good, let's call MySQL

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_createUser', (_name, _email, _password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message': 'User created successfully !'})
            else:
                return json.dumps({'error': str(data[0])})
        else:
            return json.dumps({'html': '<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

if __name__ == 'main':
    app.run()
