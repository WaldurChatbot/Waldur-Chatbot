from flask import Flask, request, render_template
from requests import post
import logging

log = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/auth/", methods=['GET', 'POST'])
def auth():
    if request.method == 'GET':
        user_id = request.args.get('user_id')

        if user_id is None:
            return "user_id parameter must be set."

        return render_template('index.html', user_id=user_id)

    if request.method == 'POST':

        # Send the token to Waldur Chatbot
        response = post("http://localhost:4567/authenticate/", data={
            'token': request.form['token'],
            'user_id': request.form['user_id']
        })

        if response.ok:
            return "Authenticated!"
        else:
            return "Error connecting to backend!"


if __name__ == '__main__':
    app.run(port=1234)
