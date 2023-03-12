import base64
from datetime import datetime
import os
import uuid

import flask
import detect

app = flask.Flask(__name__)

# static folder for this application
app.static_folder = 'runs' + os.sep + 'detect'


# host simple web page that accepts image files
@app.route('/')
def index():
    msg = flask.request.args.get('msg')
    msg_ = msg
    found = flask.request.args.get('found')
    path = flask.request.args.get('path')
    
    # print(os.path.exists(path), os.listdir(path)[0])
    if path and os.path.exists(path):
        print (msg, '.......................')
        img_path = os.listdir(path)[0]
        img_path = os.path.basename(path) + '/' + img_path
        print (img_path)
        msg = f'<img src="/static/{img_path}" width="500" height="500" alt="detection" />'
    elif found is not None: # color green
        found = int(found)
        if found:
            msg = f'<font color="green">{msg}</font>'
        else: # color red
            msg = f'<font color="red">{msg}</font>'
    else:
        msg = "";
    return f'''
        <!DOCTYPE html>
        <html>
            <body>
                <h1>Upload an image file and check if Hyundai Logo exist</h1>
                <p>{msg}</p>
                <b style="color:red">{msg_}</b>
                <form method="POST" enctype="multipart/form-data" action="/upload">
                    <input type="file" name="image">
                    <input type="submit">
                </form>
            </body>
        </html>
    '''


# an endpoint that accepts image files
@app.route('/upload', methods=['POST'])
def upload():
    # get the image file from the request
    image_file = flask.request.files['image']
    extension = image_file.filename.split('.')[-1]
    allowed = ('bmp', 'dng', 'jpeg', 'jpg', 'mpo', 'png', 'tif', 'tiff', 'webp', 'pfm')
    if extension not in allowed:
        msg = 'Only the following file types are allowed: ' + ', '.join(allowed)
        return flask.redirect(f'/?msg={msg}&found=0')
    # generate random filename
    filename = str(uuid.uuid4()) + '.' + extension
    # save the image file to the server
    image_file.save(filename)

    # run detection
    try:
        detections, _ = detect.run(weights='best.pt', source=filename, nosave=False,
                                save_txt=False, save_conf=False, save_crop=False)
    except Exception as e:
        msg = str(e)
        return flask.redirect(f'/?msg={msg}&found=0')
    finally:
        # delete the image file from the server
        os.remove(filename)
    current_time = datetime.now().strftime("%H:%M:%S")
    # redirect to / with a message
    if detections:
        msg = f'Yes there are detections at {current_time}'
        return flask.redirect(f'/?path={detections}&msg={_}')
    else:
        msg = f'No detections at {current_time}'
        return flask.redirect(f'/?path={detections}&msg={_}')
    
# accept image in the body (base64 encoded) and return detections
@app.route('/detect', methods=['POST'])
def detect_image(): 
    base64_image = flask.request.get_json()['image']
    # get params
    send_confidence = flask.request.args.get('send_confidence') or False
    # save image to server
    filename = str(uuid.uuid4()) + '.jpg'
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(base64_image))
    try:
        detections, _ = detect.run(weights='best.pt', source=filename, nosave=False,
                                save_txt=False, save_conf=False, save_crop=False)
    except Exception as e:
        return flask.jsonify({'error': str(e)}),
    finally:
        # delete the image file from the server
        os.remove(filename)
    print ("DETCTION", detections)
    img_path = os.path.join(detections, os.listdir(detections)[0])
    print ("My Image", detections, img_path)
    # return the image as a response
    
    if send_confidence:
        if _ is None:
            return flask.jsonify({'detections': []}), 500
        return flask.jsonify({'detections': _}), 200
    return flask.send_file(img_path, mimetype='image/jpg')
    
    


# run the app
if __name__ == '__main__':
    app.run(debug=True, port=5000)
