from flask import Flask

import app.views as views

app = Flask(__name__)
app.add_url_rule('/<address>', view_func=views.base)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
