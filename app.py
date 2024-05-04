from flask import Flask,render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meusers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key' 
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    notes = db.relationship('Note', backref='user', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shared_link = db.Column(db.String(100), unique=True, nullable=True)

db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    logexist_user = User.query.filter_by(username=username,password=password).first()
    if logexist_user:
        session['username'] = username
        return redirect(url_for('home'))
    else:
        return 'TRY AGAIN'

@app.route('/singup', methods=['POST'])
def signup():
    username = request.form['sinusername']
    password = request.form['sinpassword']
    exist_user = User.query.filter_by(username=username).first()
    if exist_user:
        return 'USERNAME ERROR'
    elif exist_user and exist_user.password != password: 
        return 'PASSWORD ERROR'
    else:
        entry = User(username=username, password=password)
        db.session.add(entry)
        db.session.commit()
        return render_template('index.html')

@app.route('/home')
def home():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        if user:
            notes = user.notes
            return render_template('home.html',name=username, notes=notes)

@app.route('/note', methods=['POST'])
def note():
    if 'username' in session:
        username = session['username']
        title = request.form['title']
        message = request.form['message']
        user = User.query.filter_by(username=username).first()
        if user:
            shared_link = generate_shared_link()
            entry_note = Note(title=title, message=message, user_id=user.id, shared_link=shared_link)
            db.session.add(entry_note)
            db.session.commit()
            user_notes = Note.query.filter_by(user_id=user.id).all()
            return redirect(url_for('home'))
        else:
            return 'User not found.'
    else:
        return 'PLEASE LOGIN'

@app.route('/delete/<int:note_id>', methods=['GET'])
def delete(note_id):
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        if user:
            # Find the note by its ID
            note_to_delete = Note.query.get(note_id)
            if note_to_delete:
                db.session.delete(note_to_delete)
                db.session.commit()
            return redirect(url_for('home'))
        else:
            return 'User not found.'
    else:
        return 'PLEASE LOGIN'

@app.route('/shared/<string:shared_link>')
def shared_note(shared_link):
    note = Note.query.filter_by(shared_link=shared_link).first()
    if note:
        return render_template('shared_note.html', note=note)
    else:
        return 'Note not found.'

def generate_shared_link():
    return str(uuid.uuid4())

app.run(debug=True)
