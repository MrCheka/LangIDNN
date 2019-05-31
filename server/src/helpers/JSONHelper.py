from src.requests.DetectLangsRequest import DetectLangsRequest
from src.responses.DetectLangsResponse import DetectLangsResponse
from src.responses.GetLangsResponse import GetLangsResponse

class JSONHelper:
    @staticmethod
    def serializeDetectLangsRequest(obj):
        return {
            'text': obj.text,
            'multi': obj.multi,
            'count': obj.count
        }

    @staticmethod
    def deserializeDetectLangsRequest(dict):
        text = dict['text']
        multi = dict['multi']
        count = dict['count']

        return DetectLangsRequest(text, multi, count)

    @staticmethod
    def serializeDetectLangsResponse(obj):
        return {
            'count': obj.count,
            'result': obj.result
        }

    @staticmethod
    def deserializeDetectLangsResponse(dict):
        result = dict['result']
        count = dict['count']

        return DetectLangsResponse(count, result)

    @staticmethod
    def serializeGetLangsResponse(obj):
        return {
            'langs': obj.langs
        }

    @staticmethod
    def deserializeGetLangsResponse(dict):
        langs = dict['langs']

        return GetLangsResponse(langs)
