from flask import Flask

import app.views as views

app = Flask(__name__)

app.add_url_rule('/<address>', view_func=views.address)
