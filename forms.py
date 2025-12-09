# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, URL

class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=250)])
    brand = StringField("Brand", validators=[Optional(), Length(max=100)])

    price = DecimalField("Price (£)", places=2,
                         validators=[DataRequired(), NumberRange(min=0)])
    stock_quantity = IntegerField("Stock Quantity",
                                  validators=[DataRequired(), NumberRange(min=0)])

    condition = SelectField(
        "Condition",
        choices=[("new", "New"), ("used", "Used"), ("refurbished", "Refurbished")],
        validators=[Optional()],
    )

    image_url = StringField("Image URL", validators=[Optional(), Length(max=255)])
    category_id = SelectField("Category", coerce=int, validators=[Optional()])

    submit = SubmitField("Save Product")
