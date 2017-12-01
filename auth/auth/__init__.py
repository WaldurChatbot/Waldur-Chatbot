from flask import Flask, request, render_template
from requests import post, exceptions
from configparser import ConfigParser
import os
app = Flask(__name__)


# If config file location is setup in environment variables
# then read conf from there, otherwise from project root
if 'WALDUR_CONFIG' in os.environ:
    config_path = os.environ['WALDUR_CONFIG']
else:
    config_path = '../configuration.ini'

config = ConfigParser()
config.read(config_path)

backend_url = config['backend']['url'] + ':' + config['backend']['port']


@app.route("/auth/<user_id>", methods=['GET', 'POST'])
def auth(user_id):
    if request.method == 'GET':
        return render_template('index.html', user_id=user_id)

    if request.method == 'POST':
        # Send the token to Waldur Chatbot

        try:
            response = post(f"{backend_url}/auth/{user_id}", data={
                'token': request.form['token']
            })

            if response.ok:
                message = "Authenticated!"
            else:
                message = "Couldn't authenticate."

        except exceptions.ConnectionError:
            message = "Couldn't connect to Waldur Chatbot."

        return render_template('sent.html', message=message)


if __name__ == '__main__':
    app.run(port=1234)
