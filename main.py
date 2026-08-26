import base64
import json
from flask import Flask, render_template, request
from processor import text_to_speech, gemini_process_message
from flask_cors import CORS
import os
import wave

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
file_index = 0


def play_audio_blob(blob):
    global file_index
    file_index += 1
    fname = f'audio_{file_index}.wav'
    with wave_file(fname) as wav:
        wav.writeframes(blob.data)

    return Audio(fname, autoplay=True)


def play_audio(response):
    return play_audio_blob(response.candidates[0].content.parts[0].inline_data)


def wave_file(filename, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        yield wf


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/process-message', methods=['POST'])
def process_message_route():
    user_message = request.json['userMessage']  # Get user's message from their request
    print('user_message', user_message)
    # voice = request.json['voice'] Get user's preferred voice from their request
    # print('voice', voice)
    # Call gemini_process_message function to process the user's message and get a response back
    gemini_response_text = gemini_process_message(user_message)
    # Clean the response to remove any empty lines
    gemini_response_text = os.linesep.join([s for s in gemini_response_text.splitlines() if s])
    print(gemini_response_text)
    # Call our text_to_speech function to convert gemini's response to speech
    gemini_response_speech = text_to_speech(gemini_response_text)
    # convert gemini_response_speech to base64 string, so it can be sent back in the JSON response
    gemini_response_speech = base64.b64encode(gemini_response_speech).decode('utf-8')
    # Send a JSON response back to the user containing their message's response both in text and speech formats
    response = app.response_class(
        response=json.dumps({"geminiResponseText": gemini_response_text, "geminiResponseSpeech": gemini_response_speech}),
        status=200,
        mimetype='application/json'
    )
    print(response)
    return response


if __name__ == "__main__":
    app.run(port=8000, host='0.0.0.0')

