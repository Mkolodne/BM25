from BM25 import BM25
from flask import Flask
from flask_restful import Api, Resource, reqparse

filenames = ['/home/mkolod/BM25API/BM25/CS106B-fa2020-threads-anon.json',
                 '/home/mkolod/BM25API/BM25/CS106B-sp2020-threads-anon.json']
APP = Flask(__name__)
API = Api(APP)
model = BM25(filenames)


class Search(Resource):
    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument('Query')
        parser.add_argument('k')
        args = parser.parse_args()
        out = model.run(args['Query'], int(args['k']))
        return out, 200
    
API.add_resource(Search, '/search')
        
    
    
if __name__ == '__main__':
    APP.run(debug=True, port = '1080')
