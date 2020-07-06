import secrets
from flask import Flask, render_template, request, url_for, flash, redirect,abort
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, InputRequired, ValidationError
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import time
from threading import Thread
from g_api import _generate_token_, append_sheet

app = Flask(__name__)

app.secret_key = '36d37ff024c80147d78bdd5401aa7f76f55690c5a422ac129040379a64ec8939'

def generate_token(form, expires_in=3600):
    s = Serializer(app.config['SECRET_KEY'], expires_in)
    token_data = s.dumps({'form': form}).decode('utf-8')
    return token_data

def verify_token(form, token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        token_data = s.loads(token.encode('utf-8'))
    except:
        return False
    if token_data.get('form') == form:
        return True
    return False


class Form(FlaskForm):
    f_name = StringField('First Name', validators=[InputRequired(), Length(min=2)])
    l_name = StringField('Last Name', validators=[InputRequired(), Length(min=2)])
    address = StringField('Address', validators=[InputRequired(),])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[InputRequired()])
    dob = DateField('Birth Date')
    gender = SelectField('Gender', choices=[(0,'Choose gender'), (1,'Male'), (-1,'Female')], coerce=int)
    submit = SubmitField('Submit')

@app.route('/authorize')
def authorize():
    return f"""<h1>code: {request.args.get('code')}</h1>"""

def async_append_sheet(row):
    _generate_token_()
    append_sheet(row)

def append_to_sheet(row):
    thr = Thread(target=async_append_sheet, args=[row])
    print("thr")
    thr.start()
    print("thr.start()")
    return thr

@app.route('/', methods=['POST','GET'])
def forms():
    form = Form()
    if form.validate_on_submit():
        row=(form.f_name.data,form.l_name.data,form.address.data,form.email.data.lower(),form.phone.data,form.dob.data.strftime('%Y/%B/%d'))
        print(row)
        append_to_sheet(row)
        flash('Success!. Your response has been recorded.', 'success')
        return redirect(url_for('forms'))
    return render_template('index.html',form=form)


if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)