from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, DecimalField,
    IntegerField, SelectField, SubmitField
)
from wtforms.validators import DataRequired, NumberRange, Optional
from flask_wtf.file import FileField, FileAllowed


class ProductForm(FlaskForm):

    name = StringField("Product Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional()])
    brand = StringField("Brand", validators=[Optional()])

    price = DecimalField("Price (£)", validators=[DataRequired(), NumberRange(min=0)])
    stock_quantity = IntegerField("Stock Quantity", validators=[NumberRange(min=0)], default=1)

    category_id = SelectField("Category", coerce=int, validators=[Optional()])

    condition = SelectField(
        "Condition",
        choices=[
            ("new", "New"),
            ("used", "Used"),
            ("refurbished", "Refurbished"),
        ],
        validators=[Optional()],
    )

    image = FileField(
        "Product Image",
        validators=[
            Optional(),
            FileAllowed(['jpg', 'jpeg', 'png', 'webp'], "Images only!")
        ]
    )

    image_url = StringField("Image URL (optional)", validators=[Optional()])

    submit = SubmitField("Save Product")
