import flask
import PIL
import os
from PIL import Image, ImageStat
from flask import request, flash, render_template, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads/'

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# to detect color or b&w
def detect_color_image(img, thumb_size=40, MSE_cutoff=22, adjust_color_bias=True):
    # read image from parameter
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


# check whether file is valid image file
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

# to display image
@app.route('/display/<filename>')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/detect', methods=['GET', 'POST'])
def detect():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return render_template('detect.html')
        # return redirect(request.url)

    file = request.files['file']
    print('File name: ', file.filename)

    if file.filename == '':
        flash('No image selected for uploading', 'danger')
        return render_template('detect.html')

    if file and allowed_file(file.filename) and request.method == 'POST':
        filename = secure_filename(file.filename)
        # upload image
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # fetch image
        input_file = Image.open(UPLOAD_FOLDER + filename)
        file_path = UPLOAD_FOLDER + filename
        print('Filepath: ', file_path)
        result = detect_color_image(input_file)
        print(result)
        flash('Image successfully uploaded and displayed', 'success')
        # return render_template('home.html', filename = filename, result = result)

    else:
        flash('Allowed image types are -> png, jpg, jpeg', 'danger')
        return render_template('detect.html')

    return render_template('detect.html', filename = filename, result = result)

    # Test with existing images from folder
    # img = Image.open('TestImage/3.jpeg')
    # img.show()
    # return(detect_color_image(img))
    # return render_template('home.html')
    # if request.method == 'POST':
    # Taking the image
    # Detect color or black or white
    # return 'in detect'
    # return result


app.run()
