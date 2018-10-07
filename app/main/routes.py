from flask import Blueprint, flash, render_template, request, redirect, url_for, Markup
from app.main.forms import SearchForm
from app.main.utils import search_hash

types = ['address','bundle','tag','transaction']

main = Blueprint('main', __name__)

@main.route('/', methods=['GET','POST'])
@main.route('/search/', methods=['GET','POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        hash=form.input.data.upper()
    elif request.method == 'POST':
        hash=request.form['hash'].upper()
    else:
        return render_template('main/index.html', form=form)
    return redirect(url_for('main.result', type='search', hash=hash))

@main.route('/<string:type>/<string:hash>', methods=['GET','POST'])
def result(type, hash):
    ctype, results = search_hash(type, hash)

    if ctype in types:
        return render_template(f'main/{ctype}.html', type=ctype, hash=hash, results=results)
    else:
        return render_template('errors.html', error=results)
