import base64
import requests

def encode_img_base64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

endpoint = 'http://localhost:5000/detect'

def send_request(base64_image):
    response = requests.post(endpoint, json={'image': base64_image})
    # response is image
    with open('response.jpg', 'wb') as f:
        f.write(response.content)

if __name__ == '__main__':
    # send a request with an image
    base64_image = encode_img_base64(r'C:\Users\Bilal Ahmad\Desktop\test\h1.jpg')
    print(send_request(base64_image))