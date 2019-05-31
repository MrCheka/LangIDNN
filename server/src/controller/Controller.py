from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from src.helpers.NNHelper import NNHelper
from src.responses.GetLangsResponse import GetLangsResponse
from src.responses.DetectLangsResponse import DetectLangsResponse
from src.helpers.JSONHelper import JSONHelper
import logging
import json

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)

class Controller:
    def __init__(self, sess, model):
        self.app = Flask(__name__)
        CORS(self.app)
        self.app.add_url_rule('/getLangs', view_func=self.get_langs)
        self.app.add_url_rule('/detectLangs', methods=['POST'], view_func=self.detect_langs)

        self.helper = NNHelper(sess, model)

        self.get_langs_response = GetLangsResponse(self.helper.langs)

    def run(self, host, port):
        CORS(self.app)
        self.app.run(host, port)

    def get_langs(self):
        return json.dumps(self.get_langs_response, default=JSONHelper.serializeGetLangsResponse)

    def detect_langs(self):
        detect_langs_request = json.loads(request.data, object_hook=JSONHelper.deserializeDetectLangsRequest)
        print(detect_langs_request.text)
        if detect_langs_request.multi:
            count = int(detect_langs_request.count)
        else:
            count = 1

        langs = []

        result = self.helper.detect_langs(detect_langs_request.text, count)

        for key, value in result.items():
            langs.append({'lang':key, 'acc': round(value*100, 2)})

        detect_langs_response = DetectLangsResponse(len(langs), langs)

        return json.dumps(detect_langs_response, default=JSONHelper.serializeDetectLangsResponse)

