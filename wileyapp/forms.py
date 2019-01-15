from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, FieldList, FormField, FloatField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange

class TextForm(FlaskForm):
    text = TextAreaField('Raw Copied Text', validators=[DataRequired()])

    submit = SubmitField('Process Information')

class SelectCourseForm(FlaskForm):
    course = SelectField(label="Course", choices=[])

    submit = SubmitField(label="Submit")


class CategoryWeightForm(FlaskForm):
    weight = FloatField('Category Weight', validators=[DataRequired(), NumberRange(min=1.0, max=100.0)])

class CategoryWeightsForm(FlaskForm):
    weights = FieldList(FormField(CategoryWeightForm))
    submit = SubmitField('Submit')