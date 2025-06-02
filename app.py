# app.py
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

# If you want to serve other static files from the root, you can add them here
# For example, if you have an icon at static/images/icon.png and want to serve it from /icon.png
# @app.route('/icon.png')
# def icon():
#     return send_from_directory('static/images', 'icon.png')

if __name__ == '__main__':
    app.run(debug=True)