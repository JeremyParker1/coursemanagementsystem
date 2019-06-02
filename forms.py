from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, EqualTo


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AssignmentForm(FlaskForm):
    type = SelectField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    number = IntegerField('Assignment Number', validators=[DataRequired()])
    submit = SubmitField('Create')


class PasswordForm(FlaskForm):
    password = PasswordField('Current Password', validators=[DataRequired()])
    newPassword = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm',
                                                                                    message='Passwords must match')])
    confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class GradeForm(FlaskForm):
    newGrade = StringField('New Grade', validators=[DataRequired()])
    email = SelectField('Email', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CapstoneGradeForm(FlaskForm):
    newGrade = StringField('New Grade',validators=[DataRequired()])
    teamNum = SelectField('Team Number', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Submit')


class ChangeProfForm(FlaskForm):
    course = SelectField('Class', validators=[DataRequired()])
    section = SelectField('Section', validators=[DataRequired()], coerce=int)
    professor = SelectField('Professor', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SectionChangeForm(FlaskForm):
    #course = SelectField('Class', validators=[DataRequired()])
    section = SelectField('Section', validators=[DataRequired()], coerce=int)
    email = SelectField('Section', validators=[DataRequired()])
    submit = SubmitField('Submit')


class DropForm(FlaskForm):
    email = SelectField('Section', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EnrollmentForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    course = SelectField('Class', validators=[DataRequired()])
    section = SelectField('Section', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Submit')


class DeleteForm(FlaskForm):
    delete = SubmitField('Delete Assignment')
