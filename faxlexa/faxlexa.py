# coding=utf-8

# Faxlexa
# By Alastair Flynn <alastair.flynn@metaswtitch.com>
#
# Alexa speech to fax
from PIL import Image, ImageFont, ImageDraw
import logging
import base64
import os
import time
import subprocess
from datetime import datetime
from flask import Flask, json, render_template
from flask_ask import Ask, request, session, question, statement


app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger("flask_ask").setLevel(logging.DEBUG)
text = []
HEADER = """Return-path: fax-admin@mbox.datcon.co.uk
Received:  by iaburouter3.datcon.co.uk for <FAX=273@mbox.datcon.co.uk> (with Cisco NetWorks); Mon, 13 Nov 2006 14:33:03 +0000
To: "273" <FAX=273@mbox.datcon.co.uk>
Message-ID: <00322006143303358@iaburouter3.datcon.co.uk>
Date: Mon, 13 Nov 2006 14:33:03 +0000
Subject: Fax (2 pages)
X-Mailer: Technical Support: http://www.cisco
MIME-Version: 1.0
Content-Type: multipart/fax-message;
 boundary="yradnuoB=_00312006143303130.iaburouter3.datcon.co.uk"
From: "01316621345" <fax-admin@mbox.datcon.co.uk>
X-Account-Id: 0

--yradnuoB=_00312006143303130.iaburouter3.datcon.co.uk
Content-ID: <00332006143327371@iaburouter3.datcon.co.uk>
Content-Type: image/tiff; name="Cisco_fax.tif"; application=faxbw
Content-Transfer-Encoding: base64

"""
FOOTER="--yradnuoB=_00312006143303130.iaburouter3.datcon.co.uk--"
# Session starter
#
# This intent is fired automatically at the point of launch (= when the session starts).
# Use it to register a state machine for things you want to keep track of, such as what the last intent was, so as to be
# able to give contextual help.

@ask.on_session_started
def start_session():
    """
    Fired at the start of the session, this is a great place to initialise state variables and the like.
    """
    logging.debug("Session started at {}".format(datetime.now().isoformat()))

# Launch intent
#
# This intent is fired automatically at the point of launch.
# Use it as a way to introduce your Skill and say hello to the user. If you envisage your Skill to work using the
# one-shot paradigm (i.e. the invocation statement contains all the parameters that are required for returning the
# result

@ask.launch
def handle_launch():
    """
    (QUESTION) Responds to the launch of the Skill with a welcome statement and a card.

    Templates:
    * Initial statement: 'welcome'
    * Reprompt statement: 'welcome_re'
    * Card title: 'Faxlexa
    * Card body: 'welcome_card'
    """

    welcome_text = render_template('welcome')
    welcome_re_text = render_template('welcome_re')
    welcome_card_text = render_template('welcome_card')

    return question(welcome_text).reprompt(welcome_re_text).standard_card(title="Faxlexa",
                                                                          text=welcome_card_text)


# Built-in intents
#
# These intents are built-in intents. Conveniently, built-in intents do not need you to define utterances, so you can
# use them straight out of the box. Depending on whether you wish to implement these in your application, you may keep
# or delete them/comment them out.
#
# More about built-in intents: http://d.pr/KKyx

@ask.intent('AMAZON.StopIntent')
def handle_stop():
    """
    (STATEMENT) Handles the 'stop' built-in intention.
    """
    farewell_text = render_template('stop_bye')
    return statement(farewell_text)


@ask.intent('AMAZON.CancelIntent')
def handle_cancel():
    """
    (STATEMENT) Handles the 'cancel' built-in intention.
    """
    farewell_text = render_template('cancel_bye')
    return statement(farewell_text)


@ask.intent('AMAZON.HelpIntent')
def handle_help():
    """
    (QUESTION) Handles the 'help' built-in intention.

    You can provide context-specific help here by rendering templates conditional on the help referrer.
    """

    help_text = render_template('help_text')
    return question(help_text)


@ask.launch
def start_skill():
    msg = "Ok Grandpa"
    return question(msg)

@ask.intent('MessageContentIntent', mapping={'message': 'FaxPhrase'})
def handle_cont_message(message):
    global text
    text.append(message)
    print("\n\n\n\n" + message)
    speech_text = 'Go on'
    return question(speech_text).reprompt("Come on, I haven't got all day")

@ask.intent('EndMessageIntent')
def handle_end_message():
    global text
    print(text)
    speech_text = 'Sending fax ' + " ".join(text)
    img = Image.new("RGB", (595, 842), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("comicsans.ttf", 50)
    draw.text((0, 0),"\n".join(text),(0,0,0),font=font)
    img.save('faxypic.png', "PNG")
    bashCommand1 = "convert faxypic.png fax.pdf"
    os.system(bashCommand1)
    time.sleep(0.5)
    res = subprocess.check_output('mail -s "fakesubject" 442083632300@myfax.com -A fax.pdf < message.txt', shell=True)
    print(str(res))
    return statement(speech_text)

@ask.session_ended
def session_ended():
    return statment("Fine, don't send a fax then")

@app.route("/")
def hello():
    return "Hello World!"


    

# Ending session
#
# This intention ends the session.

@ask.session_ended
def session_ended():
    """
    Returns an empty for `session_ended`.

    .. warning::

    The status of this is somewhat controversial. The `official documentation`_ states that you cannot return a response
    to ``SessionEndedRequest``. However, if it only returns a ``200/OK``, the quit utterance (which is a default test
    utterance!) will return an error and the skill will not validate.

    """
    return statement("")


if __name__ == '__main__':
    app.run(debug=True)
