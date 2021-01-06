import flask
import PIL
from PIL import Image, ImageStat
from flask import request, jsonify
import base64
import requests
from io import BytesIO

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def detect_color_image(img, thumb_size=40, MSE_cutoff=22, adjust_color_bias=True):
    # Decode image
    img = Image.open(BytesIO(base64.b64decode(img)))
    # img = Image.open(io.BytesIO(img))

    bands = img.getbands()
    if bands == ('R','G','B') or bands== ('R','G','B','A'):
        thumb = img.resize((thumb_size,thumb_size))
        SSE, bias = 0, [0,0,0]
        if adjust_color_bias:
            bias = ImageStat.Stat(thumb).mean[:3]
            bias = [b - sum(bias)/3 for b in bias ]
        for pixel in thumb.getdata():
            mu = sum(pixel)/3
            SSE += sum((pixel[i] - mu - bias[i])*(pixel[i] - mu - bias[i]) for i in [0,1,2])
        MSE = float(SSE)/(thumb_size*thumb_size)
        if MSE <= MSE_cutoff:
            return ("Black and white\t")
        else:
            return ("Color\t\t\t")
    else:
        return ("Black and white", bands)

@app.route('/', methods=['GET'])
def home():
    return 'Happy Holiday!!'

@app.route('/detect', methods=['GET', 'POST'])
def add_face():
    if request.method == 'POST':
        print('In detect : post')
        # Taking the image
        message = request.get_json(force=True)
        print(message)
        img = message['img']
        # Detect color or black or white
        res = detect_color_image(img)
        return jsonify({'content': res})

    # response for get
    return 'In detect : get'

app.run()
