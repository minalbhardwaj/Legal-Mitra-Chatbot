from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from chatbot import generate_response
import json, uuid
from flask import render_template_string
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


#entry point
@app.route("/")
def index():
    # session.clear()  
    if "previous_chats" not in session:
        # session["previous_chats"] = {'1':{"converstion":[{'user':'Hi','bot':"Hiiiii"}],'title':"First question"},'2':{"converstion":[{'user':'Hi2','bot':"Hiiiii2"}],'title':"Second question"}}
        session["previous_chats"] = {}
        session.modified = True
    print(session["previous_chats"])
    return render_template("index.html", previous_chats=session["previous_chats"])

#when click on send btn ajax post method runs
@app.route("/chat", methods=["POST"])
def chat():
    print(request.json)
    user_input = request.json.get("message")#user input
    print(user_input)
    raw_response = generate_response(user_input)# generate reponse by calling this method and pass user input
    print(raw_response)
    html_template = """
    {% for msg in messages %}
    <div class="bot-msg">
        <img src="https://cdn-icons-png.flaticon.com/64/6873/6873405.png" alt="bot" width="40" height="40" style="margin-right: 10px;">
        <div class="chat-bubble">
            <p>{{ msg.answer }}</p>
        </div>
    </div>
    {% endfor %}
    """

    rendered_html = render_template_string(html_template, messages=raw_response)
    if "current_chat" in session and session["current_chat"]:
        print(session["current_chat"])
        session["current_chat"]['converstion'].append({"user": user_input, "bot": raw_response[0]['answer']})
    else:
        session["current_chat"] = {'converstion':[{"user": user_input, "bot": raw_response[0]['answer']}],'title':user_input}


    session.modified = True
    return jsonify({"html": rendered_html})
    # return jsonify({"answer": answer})

@app.route("/new_conversation", methods=["POST"])
def new_conversation():
    if "current_chat" in session and session["current_chat"]:
        if "previous_chats" not in session:
            session["previous_chats"] = {}
        
        msg_id = str(uuid.uuid4()).replace('-', '')
        first_user_msg = next((msg for msg in session["current_chat"] if isinstance(msg, dict) and msg.get("user")), None)
        title = first_user_msg["user"].split()[:4] if first_user_msg else "Untitled"

        session["previous_chats"][msg_id] = session["current_chat"]
    
    session["current_chat"] = []
    session.modified = True
    print("---------------------1----------------------")
    print(session)
    return jsonify({"success": True})

@app.template_filter('get_item')
def get_item(lst, index):
    try:
        print(lst.get(index))
        return lst.get(index)
    except (IndexError, ValueError, TypeError):
        return ''
    
@app.template_filter('get_msg')
def get_msg(lst):
    try:
        print(lst.get('title'))
        return lst.get('title')
    except (IndexError, ValueError, TypeError):
        return ''
    

# @app.template_filter('first_user_message')
# def first_user_message(chat):
#     if isinstance(chat, list):
#         for msg in chat:
#             if "user" in msg:
#                 return msg["user"][:30] + "..."
#     return "Untitled Chat"



if __name__ == "__main__":
    app.run(debug=True)
