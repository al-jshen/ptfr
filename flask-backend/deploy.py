import flask
from flask import Flask, request, render_template
from flask_cors import CORS, cross_origin
import numpy as np
from collections import OrderedDict
import torch
from torch import nn
from torchvision import transforms, models, datasets
from PIL import Image
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/")
def index():
    return flask.render_template('index.html')

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route('/predict', methods=['POST'])
def local_prediction():
    if request.method == 'POST':

        # get uploaded image
        file = request.files['file']
        if not file:
            return render_template('index.html', label="No file uploaded")
        label = make_prediction(file)

        #return render_template('index.html', label=label)
        return f'It\'s a {label}.'

@app.route('/test', methods=['POST'])
def remote_prediction():
    file = request.files['file']
    return make_prediction(file)

def make_prediction(file):
    # read file as pil image
    # apply transforms and convert into tensor
    img = Image.open(file)
    img = transforms.functional.resize(img, 250)
    img = transforms.functional.ten_crop(img, 224)
    f = lambda crops: torch.stack([transforms.ToTensor()(crop) for crop in img])
    feature = f(img)

    # feed through network
    output = model(feature)
    # take average of ten crops
    output = output.mean(0)
    # get class with highest activation
    prediction = output.exp().max(dim=0)[1]
    # convert result into string indicating flower type
    label = cat_to_name[testdat.classes[prediction]]
    return label

def init_model():
    resnet = models.resnet152(pretrained=False)
    class net(nn.Module):
        def __init__(self, in_dims, out_dims):
            super(net, self).__init__()
            self.fc1 = nn.Linear(in_dims, 1024)
            self.fc2 = nn.Linear(1024, 512)
            self.fc3 = nn.Linear(512, out_dims)
            self.lsm = nn.LogSoftmax(dim=1)
            self.lrelu = nn.LeakyReLU()
            self.drop = nn.Dropout(p=0.7)
        def forward(self, x):
            x = self.drop(self.lrelu(self.fc1(x)))
            x = self.drop(self.lrelu(self.fc2(x)))
            x = self.drop(self.lrelu(self.fc3(x)))
            x = self.lsm(x)
            return(x)
    resnet_clf = net(2048, 102)
    resnet.fc = resnet_clf
    resnet.load_state_dict(torch.load('resnet.pt', map_location='cpu'))
    for param in resnet.parameters():
        param.requires_grad = False
    resnet.eval()
    return resnet


if __name__ == '__main__':
    # initialize model
    model = init_model()
    # initialize labels
    testdat = datasets.ImageFolder('valid')
    with open('cat_to_name.json', 'r') as f:
        cat_to_name = json.load(f)
    # start app
    app.run(host='0.0.0.0', port=8000, debug=True)
