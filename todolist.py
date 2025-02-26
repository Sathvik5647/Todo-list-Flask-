from flask import Flask,render_template,request,redirect,url_for,session
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app=Flask(__name__)

password=quote_plus('ms290171')
app.secret_key = 'sathvik123'
app.config['SQLALCHEMY_DATABASE_URI']=f'mysql+pymysql://root:{password}@localhost/todo_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)


class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(50),nullable=False)
    password=db.Column(db.String(50),nullable=False)
    
class Entry(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)

def is_logged_in():
    return 'user_id' in session

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    if not is_logged_in():
        return redirect(url_for('login'))
    user_id = session['user_id']
    user=User.query.get(user_id)
    entries = Entry.query.filter_by(user_id=user_id).order_by(Entry.date_created.desc()).all()
    return render_template('index.html', entries=entries, user=user.username)

@app.route("/signup",methods=['GET','POST'])
def signup():
    message=None
    username=None
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        repassword=request.form.get('repassword')
        if not username or not password:
            message="Enter email and password"
        elif password!=repassword:
            message="Passwords do not match"
        else:
            existing_user=User.query.filter_by(username=username).first()
            if existing_user:
                message="You already have an account"
                return redirect('login')
            else:
                new_user=User(username=username,password=password)
                db.session.add(new_user)
                db.session.commit()
                return redirect('login')
    return render_template('signup.html',alert_message=message,username=username)

@app.route("/login",methods=['GET','POST'])
def login():
    message=None
    username=None
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')

        if not username or not password:
            message="Enter both email and password"

        else:
            existing_user=User.query.filter_by(username=username,password=password).first()
            if existing_user:
                session['user_id'] = existing_user.id
                return redirect(url_for('home'))
            else:
                message="Invalid username or password"
    return render_template('login.html',alert_message=message,username=username)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    message = None
    if request.method == 'POST':
        username = request.form.get('username')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        user = User.query.filter_by(username=username).first()
        if not user:
            message = "User not found"
        elif new_password != confirm_password:
            message = "Passwords do not match"
        elif new_password == user.password:
            message = "The password is already in use for this user"
        else:
            user.password = new_password
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('forgot_password.html', alert_message=message)



@app.route('/add', methods=['POST'])
def add_entry():
    if not is_logged_in():
        return redirect(url_for('login'))

    title = request.form['title']
    desc = request.form['desc']
    user_id = session['user_id']

    new_entry = Entry(title=title, desc=desc, user_id=user_id)
    db.session.add(new_entry)
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/delete/<int:srno>')
def delete_entry(srno):
    if not is_logged_in():
        return redirect(url_for('login'))

    entry = Entry.query.filter_by(srno=srno, user_id=session['user_id']).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()

    return redirect(url_for('home'))

@app.route('/complete/<int:srno>')
def complete_task(srno):
    if 'user_id' not in session:
        return redirect('/login')
    entry = Entry.query.get(srno)
    if entry and entry.user_id == session['user_id']:
        entry.completed = not entry.completed
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/update/<int:srno>', methods=['GET','POST'])
def update(srno):
    if 'user_id' not in session:  
        return redirect(url_for('login'))

    entry = Entry.query.filter_by(srno=srno, user_id=session['user_id']).first() 

    if not entry: 
        return redirect(url_for('home'))
    if request.method=='POST':
        title=request.form['title']
        desc=request.form['desc']
        entry.title=title
        entry.desc=desc
        db.session.commit()
        return redirect(url_for('home'))
    entry=Entry.query.filter_by(srno=srno).first()
    return render_template('update.html',entry=entry)



if __name__ == '__main__':
    app.run(debug=True,use_reloader=True)
