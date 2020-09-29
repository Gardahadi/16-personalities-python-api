from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)

#For WSGI Purposes
application = app

#get credentials for oauth
SERVICE_ACCOUNT_FILE = 'creds/secret.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Get file paths
questions_path = 'questions/double-target-range.json'

@app.route('/questions', methods=['GET'])
def get_questions():
    with open(questions_path, 'r') as question_file :
        data = question_file.read()

        # parse file
        obj = json.loads(data)
        questions = [x['q'] for x in obj['questions']]
    
        return jsonify(questions)

@app.route('/answers', methods=['POST'])
def post_answers():
    with open(questions_path, 'r') as json_file:
        #get questions
        data = json_file.read()
        obj = json.loads(data)
        questions = obj['questions']
    
        #Parse requests 
        body = request.json
        user = body["user"]
        answers = body['answers']

        #Check if user answerd all true or not
        if (all([x == 5 for x in answers]) or all([x == 0 for x in answers]) ) :
            return jsonify({
                'suggestion': "It's still too tricky to find your shade of blue..."
            })

        else :
            array_of_panitia = obj['divisions']
            array_of_score = [0 for i in range(len(array_of_panitia))] 
            score_map = dict(zip(array_of_panitia,array_of_score))

            #code to count answer
            for key,question in zip(answers,questions) :

                #Get result
                result = int(answers[key])
                
                #find out what type it is
                if (question['type'] == 'single') :
                    score_map[question['choices'][result]] += 1

                elif (question['type'] == 'range'):
                    score_map[question['target']] += result

            
            if (user["major"] != "Management") : 
                score_map["Delegate Relations"] = 100
                suggestions_containing_only_3_items = list(sorted(score_map, key=score_map.get, reverse=True))[:3]
            
            else :          
                max_score = max(score_map)
                list_of_max = [key for key in score_map if score_map[key]==max_score]
                if (len(list_of_max) > 3) : 
                    #Sort the suggestions
                    suggestions = [key for key in score_map if score_map[key]==max_score]
                    suggestions_containing_only_3_items = random.choices(suggestions, k=3)
                else : 
                    suggestions_containing_only_3_items = list(sorted(score_map, key=score_map.get, reverse=True))[:3]


            values_to_write = [user["name"], user["email"], user["major"], suggestions_containing_only_3_items[0], suggestions_containing_only_3_items[1], suggestions_containing_only_3_items[2]]
            
            #write to sheets
            SPREADSHEET_ID = '1mOcxMaYsuBY3usrCpcZTrjrhRq0Utd0QZs-qeMW4efQ'
        
            #Create service instance
            service = build('sheets', 'v4', credentials=credentials)

            value_input_option = 'USER_ENTERED'
            body = {
                "majorDimension": "ROWS",
                "values": [values_to_write]
            }

            #Modify range based on "number" input
            range_to_write = "Sheet1!A:A"
            # Append values to spreadheet
            sheet = service.spreadsheets()
            result = sheet.values().append(spreadsheetId=SPREADSHEET_ID,
                                            range=range_to_write,
                                            valueInputOption=value_input_option, 
                                            body=body).execute()
            
            return jsonify({
                'suggestion': suggestions_containing_only_3_items
            })


if __name__ == '__main__':
    app.run()
    
