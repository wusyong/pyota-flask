from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from iota import Address, Tag, Hash

class SearchForm(FlaskForm):
    input = StringField('input',
                        validators=[DataRequired(),
                        Length(max=90, message='Please enter an address, transaction hash, bundle or tag.')])

    submit = SubmitField('Search')

    def validate_search(self, input):
        if not Tag(input.data):
            if not Hash(input.data):
                if not Address(input.data):
                    raise ValidationError('Please enter an address, transaction hash, bundle or tag.')
                else:
                    input.data = Address(input.data)
            else:
                input.data = Hash(input.data)
        else:
            input.data = Tag(input.data)
