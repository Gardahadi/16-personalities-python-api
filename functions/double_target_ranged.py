from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
import os
from google.oauth2 import service_account
from datetime import datetime
from googleapiclient.discovery import build

# Get file paths
root_path = os.path.dirname(os.path.dirname(__file__))
model_path = root_path + "/models/double_target_ranged.json"


def load_models_from_file():
    with open(model_path, "r") as model_file:
        raw_models = model_file.read()

        # Parse file
        quiz_models = json.loads(raw_models)
        questions = quiz_models["questions"]
        targets = quiz_models["targets"]

        return questions, targets


def questions():
    with open(model_path, "r") as model_file:
        raw_models = model_file.read()

        # parse file
        quiz_models = json.loads(raw_models)
        questions = quiz_models["questions"]

        question_array = []
        for idx in questions:
            question_array.append(questions[idx]['q'])

        # questions = [x['q'] for x in obj['questions']]

        return jsonify(question_array)


def answers():
    with open(model_path, "r") as model_file:
        raw_models = model_file.read()

        # parse file
        quiz_models = json.loads(raw_models)
        answers = quiz_models["answers"]

        return jsonify(answers)


def write_to_sheets(values_to_write=["joni", "ENFP"]):

    # get credentials for Google Sheet Service
    SCOPES = [
        "https://www.googleapis.com/auth/sqlservice.admin",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
    ]
    SERVICE_ACCOUNT_FILE = root_path + "/functions/secret.json"
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    # write to sheets
    SPREADSHEET_ID = "1Piqb1ka8cE80jt4eR-yJqcnxRv9XYOVK7tSnD5bnrgQ"

    # Create service instance
    service = build("sheets", "v4", credentials=credentials)

    value_input_option = "USER_ENTERED"
    body = {"majorDimension": "ROWS", "values": [values_to_write]}

    # Modify range based on "number" input
    range_to_write = "Sheet1!A:A"
    # Append values to spreadheet
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_to_write,
            valueInputOption=value_input_option,
            body=body,
        )
        .execute()
    )


def result():
    questions, targets = load_models_from_file()

    # Parse requests
    body = request.json
    user = body["name"]
    answers = body["answers"]

    # Update target scores
    for qid in questions:
        target_id = str(questions[qid]["target"])
        score = answers[qid]
        if score < 0:
            targets[target_id]["left_trait_score"] += abs(score)
        else:
            targets[target_id]["right_trait_score"] += abs(score)

    result = ""
    for idx in targets:
        left_score = targets[idx]["left_trait_score"]
        right_score = targets[idx]["right_trait_score"]
        if left_score > right_score:
            result += targets[idx]["left_trait"]
        elif right_score > left_score:
            result += targets[idx]["right_trait"]
        else:
            result += targets[idx]["left_trait"]

    dateTimeObj = str(datetime.now())

    values_to_write = [dateTimeObj, user, result]

    #write to sheets
    write_to_sheets(values_to_write)


    return jsonify({"result": result})
