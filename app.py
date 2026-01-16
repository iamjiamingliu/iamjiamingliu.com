from flask import Flask, render_template
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
Bootstrap5(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/experience')
def experience():
    return render_template('base.html')

@app.route('/blogs')
def blogs():
    return render_template('base.html')

@app.route('/contact')
def contact():
    return render_template('base.html')


if __name__ == '__main__':
    app.run()
