from flask import Blueprint, flash, render_template, request, redirect, url_for, Markup
from app.services.forms import TxForm, AddressForm
from app.services.utils import retry_bundle, track_bundle

services = Blueprint('services', __name__)

@services.route('/node')
def node():
    return render_template('services/node.html')


@services.route('/reattach/', methods=['GET','POST'])
def reattach():
    return reattach_add("")

@services.route('/reattach/<string:transaction>', methods=['GET','POST'])
def reattach_add(transaction):
    form = TxForm()
    if form.validate_on_submit():
        result = retry_bundle(form.tx.data)
        flash(result, 'info')
        return redirect(url_for('services.reattach_add', transaction=form.tx.data))
    elif request.method == 'GET':
        form.tx.data = transaction
    return render_template('services/reattach.html', form=form)

@services.route('/track/', methods=['GET','POST'])
def track():
    return track_add("")

@services.route('/track/<string:address>', methods=['GET','POST'])
def track_add(address):
    form = AddressForm()
    if form.validate_on_submit():
        address, result = track_bundle(form.address.data)
        if address is None:
            flash(result)
        else:
            flash(result)
            flash(address, 'address')
            json = '{"address":"' + address +'", "message":""}'
            flash(json, 'qrcode')
        return redirect(url_for('services.track_add', address=form.address.data))
    elif request.method == 'GET':
        form.address.data = address
    return render_template('services/track.html', form=form)
