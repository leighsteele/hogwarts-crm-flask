from json import JSONEncoder

class JsonEnc(JSONEncoder):
    def default(self, o):
        return o.__dict__