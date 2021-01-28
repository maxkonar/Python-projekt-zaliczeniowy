from flask import Flask, render_template, request, session, redirect, flash, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=10)
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    informations = db.relationship('Information', backref='user')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Information(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(20))
    surname = db.Column(db.String(30))
    personal_id_number = db.Column(db.String(30))
    phone_number = db.Column(db.String(30))
    temperature = db.Column(db.Boolean, default=False)
    medicine = db.Column(db.Boolean, default=False)
    first_issues = db.Column(db.Boolean, default=False)
    second_issues = db.Column(db.Boolean, default=False)
    third_issues = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, name, surname, personal_id_number, phone_number, temperature, medicine, first_issues, second_issues, third_issues):
        self.user_id = user_id
        self.name = name
        self.surname = surname
        self.personal_id_number = personal_id_number
        self.phone_number = phone_number
        self.temperature = temperature
        self.medicine = medicine
        self.first_issues = first_issues
        self.second_issues = second_issues
        self.third_issues = third_issues

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=25)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=50)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=25)])
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=50)])

class CovidForm(FlaskForm):
    name = StringField('Imię', validators=[InputRequired(), Length(min=4, max=25)])
    surname = StringField('Nazwisko', validators=[InputRequired(), Length(min=1, max=50)])
    personal_id_number = StringField('Pesel', validators=[InputRequired(), Length(min=12, max=20)])
    phone_number = StringField('Tel.kontaktowy')
    temperature = BooleanField('Gorączka 38 ˚C i powyżej')
    medicine = BooleanField('Czy zażywa Pani/Pan leki obniżające temperaturę?')
    first_issues = BooleanField('Kaszel, biegunka, nudności i wymioty, zaburzenia węchu i smaku')
    second_issues = BooleanField('Trudności z oddychaniem/duszności/ trudności w nabraniu powietrza')
    third_issues = BooleanField('Bóle mięśni/zmęczenie')

@app.route('/covid', methods=['GET', 'POST'])
@login_required
def covid():
    form = CovidForm()

    if request.method == "POST":

            new_information = Information(
                user_id=current_user.id,
                name=form.name.data,
                surname=form.surname.data,
                personal_id_number=form.personal_id_number.data,
                phone_number=form.phone_number.data,
                temperature=form.temperature.data,
                medicine=form.medicine.data,
                first_issues=form.first_issues.data,
                second_issues=form.second_issues.data,
                third_issues=form.third_issues.data)
            flash('Dane zostały zapisane!')
            db.session.add(new_information)
            db.session.commit()
            return render_template('covid.html', form=form)

    flash(current_user.username)
    flash(form.validate())
    return render_template('covid.html', form=form)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect('dashboard')
        flash('Podany użytkownik nie istnieje!')
        return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    exist_user = User.query.filter_by(username=form.username.data).first()
    exist_email = User.query.filter_by(email=form.email.data).first()

    if exist_user:
        flash('Podana nazwa użytkownika jest już zajęta')
        return render_template('signup.html', form=form)
    if exist_email:
        flash('Podany email jest już zajęty')
        return render_template('signup.html', form=form)
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Konto zostało utworzone! Proszę się zalogować')
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username, email=current_user.email)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')

if __name__ == '__main__':
 db.create_all()
 app.run(debug=True)
