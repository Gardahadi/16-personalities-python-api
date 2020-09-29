import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from functions.double_target_ranged import questions, result

project_root = os.path.dirname(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

# For WSGI Purposes
application = app


@app.route('/questions', methods=['GET'])
def get_question_function():
    return questions()


@app.route('/answers', methods=['POST'])
def post_answers():
    return result()


if __name__ == '__main__':
    print(sys.path)
    app.run()
