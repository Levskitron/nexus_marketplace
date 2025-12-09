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
    stock_quantity = IntegerField("Stock Qty", validators=[NumberRange(min=0)], default=1)

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

    # Upload image
    image_upload = FileField(
        "Upload Image",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only!")
        ]
    )

    # OR image URL
    image_url = StringField("Image URL (optional)", validators=[Optional()])

    submit = SubmitField("Save Product")

    # ---------------------------
    # CUSTOM VALIDATION:
    # Must provide either upload or URL
    # ---------------------------
    def validate(self, extra_validators=None):
        # Run default validators
        initial_validation = super().validate(extra_validators)
        if not initial_validation:
            return False

        # Require: at least one image source must exist
        has_upload = self.image_upload.data and getattr(self.image_upload.data, "filename", "")
        has_url = self.image_url.data and self.image_url.data.strip()

        if not has_upload and not has_url:
            self.image_url.errors.append("You must upload an image OR provide an image URL.")
            return False

        return True


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

class CheckoutForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    postcode = StringField("Postcode", validators=[DataRequired()])
    country = StringField("Country", validators=[DataRequired()])

    card_number = StringField("Card Number", validators=[DataRequired()])
    card_expiry = StringField("Expiry Date (MM/YY)", validators=[DataRequired()])
    card_cvv = StringField("CVV", validators=[DataRequired()])
    card_name = StringField("Name on Card", validators=[DataRequired()])

    submit = SubmitField("Complete Purchase")
