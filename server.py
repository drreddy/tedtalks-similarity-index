import os

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado import gen
import sockjs.tornado
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.escape import json_encode, json_decode

import string
from pprint import pprint
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.stem.porter import PorterStemmer

nltk.data.path.append('./nltk_data/')

def sanitizeAndTokenize(text):
    text = text.lower()
    tokens = nltk.word_tokenize(text)
    stems = []
    for item in tokens:
        stems.append(PorterStemmer().stem(item))
    return stems

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")
        
class webSockConnection(sockjs.tornado.SockJSConnection):

    tfidf = TfidfVectorizer(tokenizer=sanitizeAndTokenize, stop_words='english')

    def on_open(self, info):
        pass

    def on_message(self, message):
        # Broadcast message
        if message.split("--")[0] == "compare":
            self.compare(message.split("--")[1])
        elif message.split("--")[0] == "search":
            self.search(message.split("--")[1])
        else:
            pass
            # self.broadcast(self.participants, message)

    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        pass
    
    @gen.coroutine
    def search(self,tags):
        tagsList = tags.split(',')
        http_client = AsyncHTTPClient()
        
        dataBody = {}
        dataBody['query'] = {}
        dataBody['query']['bool'] = {}
        dataBody['query']['bool']['must'] = {}
        dataBody['query']['bool']['must']['terms'] = {}
        dataBody['query']['bool']['must']['terms']['tags'] = tagsList
        dataBody['query']['bool']['must']['terms']['minimum_should_match'] = len(tagsList)
        
        urlBody = json_encode(dataBody)

        dbUrl = "dburluntilttheindex/_search/?size=2000&pretty=1"   # dburl comes here
        
        request_http = HTTPRequest(dbUrl, method="POST", body=urlBody)
        
        response = yield http_client.fetch(request_http)
        
        jsonResp = json.loads(response.body)
        
        data = []
        
        for hit in jsonResp['hits']['hits']:
            temp = {}
            temp['title'] = hit['_source']['name']
            temp['tedid'] = hit['_source']['id']
            temp['url'] = hit['_source']['url']
            temp['speaker'] = hit['_source']['speaker']
            temp['desc'] = hit['_source']['short_summary']
            data.append(temp)
        
        resp = {}
        resp['type'] = "search"
        resp['data'] = data
        
        self.send(resp)

    @gen.coroutine
    def compare(self,ids):
        http_client = AsyncHTTPClient()
        base_url = "http://www.ted.com/talks/subtitles/id/"
        fetchDict = {}
        for id in ids.split(","):
            fetchDict[id] = http_client.fetch(base_url + id + "/lang/eng")
        response_dict = yield fetchDict
        
        transcripts = {}
        
        papaId = ids.split(",")[0]
        papa_transcript = ' '.join(self.extractText(response_dict[papaId].body))

        for id in ids.split(","):
            if id != papaId:
                transcripts[id] = ' '.join(self.extractText(response_dict[id].body))

        tfs = self.tfidf.fit_transform([papa_transcript] + transcripts.values())

        compData = {}

        sim = cosine_similarity(tfs[0:1], tfs)

        compData['results'] = {}

        for k in transcripts.keys():
            compData['results'][k] = sim[0][transcripts.keys().index(k) + 1]

        compData["mainId"] = papaId

        resp = {}
        resp['type'] = "compare"
        resp['data'] = compData
        
        self.send(resp)
        
    def extractText(self,respBody):
        transcriptList = []
        for el in json.loads(respBody)['captions']:
            transcriptList.append(el['content'])
        return transcriptList

def main():
    
    sockRouter = sockjs.tornado.SockJSRouter(webSockConnection, '/wsconn')
    settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True
	)
    application = tornado.web.Application([
        (r"/", MainHandler)
    ] + sockRouter.urls, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    port = int(os.environ.get("PORT", 3000))
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()
    
if __name__ == "__main__":
    main()