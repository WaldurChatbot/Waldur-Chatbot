from flask import Flask, request, render_template
from requests import post
app = Flask(__name__)


@app.route("/auth/<user_id>", methods=['GET', 'POST'])
def auth(user_id):
    if request.method == 'GET':
        return render_template('index.html', user_id=user_id)

    if request.method == 'POST':
        # Send the token to Waldur Chatbot
        response = post("http://localhost:4567/authenticate/", data={
            'token': request.form['token'],
            'user_id': user_id
        })

        if response.ok:
            message = "Authenticated!"
        else:
            message = "Error connecting to backend!"

        return render_template('sent.html', message=message)


if __name__ == '__main__':
    app.run(port=1234)
