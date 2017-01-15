# Inspired by https://gist.github.com/bonzanini/af0463b927433c73784d

import sys
from tweepy.streaming import StreamListener
import json
import time

class MyListener(StreamListener):
    """ Custom Listener for streaming data """

    def __init__(self, outDir, outFileJson):
        self.outfile = "%s/%s" % (outDir, outFileJson)

    def on_data(self, data):
        try:
            with open(self.outfile, 'a') as f:
                # f.write(data)
                # Pretty print variant
                jsonObject = json.loads(data)
                json.dump(jsonObject, f, indent=2)
                print >> sys.stderr, "@%s: %s" % (jsonObject['user']['screen_name'], jsonObject['text'])
                return True
        except BaseException as e:
            print >> sys.stderr, "Error on_data: %s" % str(e)
            time.sleep(3)
        return True

    def on_error(self, status):
        print >> sys.stderr, status
        return True

    @classmethod
    def parse(cls, api, raw):
        status = cls.first_parse(api, raw)
        setattr(status, 'json', json.dumps(raw))
        return status
