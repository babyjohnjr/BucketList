from flask import Flask, render_template, json, request, redirect, session
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('signin.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html', error='Unauthorised Access')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

        # connect to mysql
        conn = pymysql.connect(host='localhost', user='root', password='Psychedelic212(', db='BucketList')
        cursor = conn.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            conn.commit()
            if check_password_hash(str(data[0][3]),_password):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password')

    except Exception as e:
        return render_template('error.html', error = str(e))
    finally:
        cursor.close()
        conn.close()


@app.route('/signUp',methods=['POST','GET'])
def signUp():
    conn = pymysql.connect(host='localhost', user='root', password='Psychedelic212(', db='BucketList')
    cursor = conn.cursor()
    try:
    
    # create user code
    # read the posted values from the UI
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
    
    # validate the received values
        if _name and _email and _password:

        # All good, let's call MySQL
                _hashed_password = generate_password_hash(_password)
                print("length hashed password: ", len(_hashed_password))
                cursor.callproc('sp_createUser', (_name,_email,_hashed_password))
                data = cursor.fetchall()

                if len(data) is 0:
                    conn.commit()
                    return json.dumps({'message':'User created successfully !'})
                else:
                    return json.dumps({'error':str(data[0])})
        else:
                return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
            cursor.close()
            conn.close()

if __name__== "__main__":
    app.run(debug=5002)