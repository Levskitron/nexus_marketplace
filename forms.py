from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, DecimalField,
    IntegerField, SelectField, SubmitField
)
from wtforms.validators import DataRequired, NumberRange, Optional, InputRequired
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

    image_upload = FileField(
        "Upload Image",
        validators=[
            Optional(),
            FileAllowed(['jpg', 'jpeg', 'png', 'webp'], "Images only!")
        ]
    )

    image_url = StringField("Image URL (optional)", validators=[Optional()])

    submit = SubmitField("Save Product")


class ReviewForm(FlaskForm):
    rating = SelectField(
        "Rating",
        coerce=int,
        validators=[InputRequired()],
        choices=[
            (5, "★★★★★ (5)"),
            (4, "★★★★☆ (4)"),
            (3, "★★★☆☆ (3)"),
            (2, "★★☆☆☆ (2)"),
            (1, "★☆☆☆☆ (1)"),
        ],
    )
    review_text = TextAreaField("Comment (optional)", validators=[Optional()])
    submit = SubmitField("Submit Review")

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, DecimalField,
    IntegerField, SelectField, SubmitField
)
from wtforms.validators import DataRequired, NumberRange, Optional, Length
from flask_wtf.file import FileField, FileAllowed


class ProductForm(FlaskForm):

    name = StringField(
        "Product Name",
        validators=[
            DataRequired(),
            Length(max=100, message="Product name must be 100 characters or fewer.")
        ]
    )

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

    # IMPORTANT — this field was missing (causing your error)
    image = FileField(
        "Upload Image",
        validators=[
            Optional(),
            FileAllowed(['jpg', 'jpeg', 'png', 'webp'], "Images only!")
        ]
    )

    image_url = StringField("Image URL (optional)", validators=[Optional()])

    submit = SubmitField("Save Product")
