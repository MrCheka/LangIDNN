from src.requests.DetectLangRequest import DetectLangRequest
from src.responses.DetectLangResponse import DetectLangResponse
from src.responses.GetLangsResponse import GetLangsResponse

class JSONHelper:
    @staticmethod
    def serializeDetectLangRequest(obj):
        return {
            'text': obj.text
        }

    @staticmethod
    def deserializeDetectLangRequest(dict):
        text = dict['text']

        return DetectLangRequest(text)

    @staticmethod
    def serializeDetectLangResponse(obj):
        return {
            'lang': obj.lang,
            'acc': obj.acc
        }

    @staticmethod
    def deserializeDetectLangResponse(dict):
        lang = dict['lang']
        acc = dict['acc']

        return DetectLangResponse(lang, acc)

    @staticmethod
    def serializeGetLangsResponse(obj):
        return {
            'langs': obj.langs
        }

    @staticmethod
    def deserializeGetLangsResponse(dict):
        langs = dict['langs']

        return GetLangsResponse(langs)
