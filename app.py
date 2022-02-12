from flask import Flask, render_template, json, request, session, redirect
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

@app.route('/blogs')
def blogs():
    return render_template('blog-list.html')

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

            if len(data) == 0:
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

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')


@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

        # connect to mysql
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin', (_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            if data[0][3] == _password:
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html', error='Wrong Email address or Password.')
        else:
            return render_template('error.html', error='Wrong Email address or Password.')

    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        con.close()

if __name__ == 'main':
    app.run()

