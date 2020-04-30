from flask import Flask, render_template, url_for, redirect, request
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, FileField, PasswordField
from wtforms.validators import DataRequired
from data import db_session
from data.jobs import Jobs
from data.users import User
from hashlib import sha1
import os
import json

app = Flask(__name__)

app.config['SECRET_KEY'] = 'yandushkin_secret_key'


@app.route("/")
@app.route("/index")
def index():
    return render_template("base.html", title="Заготовка")


class RegisterForm(FlaskForm):
    email = StringField("Login/Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    repeat_password = PasswordField("Repeat Password", validators=[DataRequired()])
    surname = StringField("Surname", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    age = IntegerField("Age", validators=[DataRequired()])
    position = StringField("Position", validators=[DataRequired()])
    speciality = StringField("Speciality", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        form = RegisterForm()
        return render_template("register.html", form=form)
    else:
        email = request.form["email"]
        password = request.form["password"]
        repeat_password = request.form["repeat_password"]
        surname = request.form["surname"]
        name = request.form["name"]
        age = request.form["age"]
        position = request.form["position"]
        speciality = request.form["speciality"]
        address = request.form["address"]

        if password != repeat_password:
            return "You didn't enter the same password"

        db_session.global_init("db/blogs.sqlite")
        session = db_session.create_session()

        user = User()
        user.email = email
        user.hashed_password = sha1(password.encode()).hexdigest()
        user.surname = surname
        user.name = name
        user.age = age
        user.position = position
        user.speciality = speciality
        user.address = address

        session.add(user)
        session.commit()

        return redirect("/success")


@app.route("/show_jobs")
def show_jobs():
    db_session.global_init("db/blogs.sqlite")
    session = db_session.create_session()
    users = []
    for user in session.query(User).all():
        users.append(user.surname + " " + user.name)

    job_data = []
    for job in session.query(Jobs).all():
        part = {
            "title": job.job,
            "team_leader": users[job.team_leader - 1],
            "work_size": job.work_size,
            "collaborators": job.collaborators,
            "is_finished": ("is finished" if job.is_finished else "is not finished")
        }
        job_data.append(part)

    return render_template("passengers.html", job_data=job_data)


@app.route("/training/<profession>")
def training(profession):
    if "строитель" in profession or "инженер" in profession:
        picture = "img/building_simulator.jpg"
        heading = "Строительный симулятор"
    else:
        picture = "img/science_simulator.jpg"
        heading = "Научный симулятор"
    return render_template(
        "training.html",
        picture_path=url_for("static", filename=picture),
        heading=heading,
        title="Научный симулятор"
        )


@app.route("/list_prof/<list_name>")
def list_prof(list_name):
    return render_template("list_prof.html", list_name=list_name)


@app.route("/answer")
@app.route("/auto_answer")
def answer():
    user_data = {
        "title": "Анкета",
        "surname": "Wathy",
        "name": "Mark",
        "education": "Выше среднего",
        "profession": "Киберинженер",
        "sex": "male",
        "motivation": "остаться на  Марсе",
        "ready": True,
    }
    return render_template("auto_answer.html", user_data=user_data, title=user_data["title"])


class LoginForm(FlaskForm):
    spaceman_id = IntegerField("id астронавта", validators=[DataRequired()])
    spaceman_name = StringField("Имя астронавта", validators=[DataRequired()])
    captain_id = IntegerField("id капитана", validators=[DataRequired()])
    captain_name = StringField("Имя капитана", validators=[DataRequired()])
    submit = SubmitField("Доступ")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect("/success")
    return render_template("login.html", title="Аварийный доступ", form=form)


@app.route("/success")
def success():
    return "Success"


@app.route("/distribution")
def distribution():
    passengers = [
        "Ридли Скотт", "Эндрю Уир", "Анатолий Вассерман", "Альберт Эйнштейн", "Анатолий Перельман"
    ]
    return render_template("distribution.html", passengers=passengers, title="По каютам")


@app.route("/table/<string:sex>/<int:age>")
def table(sex, age):
    image = ""
    if age >= 21:
        image = url_for("static", filename="img/adult_martian.jpg")
    else:
        image = url_for("static", filename="img/child_martian.jpg")

    color = (0, 0, 0)
    if sex == "male":
        color = (max(224 - age * 3, 0), max(224 - age * 3, 0), 255)
    elif sex == "female":
        color = (255, max(224 - age * 3, 0), max(224 - age * 3, 0))

    hex_color = "#"
    for i in range(3):
        hex_color += hex(color[i])[2:].rjust(2, "0")
    return render_template("cabin.html", title="Оформление кабины", color=hex_color, image=image)


class GetFileForm(FlaskForm):
    filename = FileField("Добавить картинку", validators=[DataRequired()])
    submit = SubmitField("Отправить")


@app.route("/gallery", methods=["GET", "POST"])
def gallery():
    form = GetFileForm()
    directory = "static/img/mars_images"
    paths = os.listdir(directory)

    if form.validate_on_submit():
        file = request.files["filename"]
        new_photo_index = str(len(paths) + 1)
        path = os.path.join("static", "img", "mars_images", "photo" + new_photo_index + ".jpg")
        file.save(path)

    full_paths = []
    for path in paths:
        full_paths.append(os.path.join(directory, path))
    return render_template("carousel.html",
                           photo_paths=full_paths, title="Красная планета", form=form)


@app.route("/member")
def member():
    with open("templates/member_data.json", encoding="utf-8") as json_file:
        all_members = json.loads(json_file.read())
    return render_template("member.html", title="Случайный пользователь", members=all_members["members"])


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="8080")
