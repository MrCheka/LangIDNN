from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from src.helpers.NNHelper import NNHelper
from src.responses.GetLangsResponse import GetLangsResponse
from src.responses.DetectLangResponse import DetectLangResponse
from src.helpers.JSONHelper import JSONHelper
import logging
import json

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)

class Controller:
    def __init__(self, sess, model):
        self.app = Flask(__name__)
        CORS(self.app)
        self.app.add_url_rule('/getLangs', view_func=self.get_langs)
        self.app.add_url_rule('/detectLang', methods=['POST'], view_func=self.detect_lang)

        self.helper = NNHelper(sess, model)

        self.get_langs_response = GetLangsResponse(self.helper.langs)

    def run(self, host, port):
        CORS(self.app)
        self.app.run(host, port)

    def get_langs(self):
        return json.dumps(self.get_langs_response, default=JSONHelper.serializeGetLangsResponse)

    def detect_lang(self):
        detect_lang_request = json.loads(request.data, object_hook=JSONHelper.deserializeDetectLangRequest)

        lang, acc = self.helper.detect_lang(detect_lang_request.text)

        detect_lang_response = DetectLangResponse(lang, round(acc * 100, 2))

        return json.dumps(detect_lang_response, default=JSONHelper.serializeDetectLangResponse)
