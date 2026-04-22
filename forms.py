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
from wtforms.validators import DataRequired, NumberRange, Optional, Length, Email
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


class ConsultationForm(FlaskForm):
    """Form for hardware/PC consultation requests."""
    name = StringField("Full Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField("Phone (optional)", validators=[Optional(), Length(max=30)])
    consultation_type = SelectField(
        "What do you need help with?",
        choices=[
            ("build_advice", "New build advice"),
            ("parts_recommendation", "Parts recommendation / compatibility"),
            ("troubleshooting", "Troubleshooting existing PC"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )
    current_setup = TextAreaField(
        "Current setup (optional)",
        validators=[Optional(), Length(max=500)],
        render_kw={"rows": 3, "placeholder": "e.g. CPU, GPU, RAM, what you use it for"},
    )
    goals_budget = TextAreaField(
        "Goals / budget (optional)",
        validators=[Optional(), Length(max=500)],
        render_kw={"rows": 3, "placeholder": "What you want to achieve and rough budget"},
    )
    contact_method = SelectField(
        "Preferred contact method",
        choices=[
            ("email", "Email"),
            ("phone", "Phone"),
            ("either", "Either"),
        ],
        validators=[DataRequired()],
    )
    message = TextAreaField(
        "Additional details",
        validators=[DataRequired(), Length(max=1000)],
        render_kw={"rows": 4, "placeholder": "Tell us more about what you need..."},
    )
    submit = SubmitField("Request Consultation")


class RepairUpgradeForm(FlaskForm):
    """Form for repair and upgrade service requests."""
    name = StringField("Full Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField("Phone (optional)", validators=[Optional(), Length(max=30)])
    service_type = SelectField(
        "Service needed",
        choices=[
            ("repair", "Repair"),
            ("upgrade", "Upgrade"),
            ("both", "Repair & upgrade"),
        ],
        validators=[DataRequired()],
    )
    device_type = SelectField(
        "Device type",
        choices=[
            ("desktop", "Desktop PC"),
            ("laptop", "Laptop"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )
    description = TextAreaField(
        "Issue description or upgrade goals",
        validators=[DataRequired(), Length(max=1000)],
        render_kw={"rows": 4, "placeholder": "Describe the problem or what you want upgraded..."},
    )
    urgency = SelectField(
        "When do you need it?",
        choices=[
            ("asap", "As soon as possible"),
            ("week", "Within a week"),
            ("flexible", "Flexible / no rush"),
        ],
        validators=[DataRequired()],
    )
    contact_method = SelectField(
        "Preferred contact method",
        choices=[
            ("email", "Email"),
            ("phone", "Phone"),
            ("either", "Either"),
        ],
        validators=[DataRequired()],
    )
    notes = TextAreaField(
        "Additional notes (optional)",
        validators=[Optional(), Length(max=500)],
        render_kw={"rows": 2},
    )
    submit = SubmitField("Submit Request")
