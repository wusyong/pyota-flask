from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from iota import Address, TransactionHash

class TxForm(FlaskForm):
    tx = StringField('tx',
                        validators=[DataRequired(),
                        Length(min=81, max=81, message='Transaction must be 81 charaters long.')])

    submit = SubmitField('Submit')

    def validate_tx(self, tx):
        tx.data = TransactionHash(tx.data.upper())

class AddressForm(FlaskForm):
    address = StringField('address',
                        validators=[DataRequired(),
                        Length(min=81, max=90, message='Address must be either 81 or 90 charaters long.')])

    submit = SubmitField('Submit')

    def validate_address(self, address):
        address.data = Address(address.data.upper())
