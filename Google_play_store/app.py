import os
from flask import Flask
from src.dal.repository import SqlAlchemyRepository
from src.bll.services import GooglePlayService
from src.core.config import Config

app = Flask(__name__, 
            template_folder='src/web/templates', 
            static_folder='src/web/static')

app.secret_key = os.urandom(24) 

repository = SqlAlchemyRepository()

service = GooglePlayService(repository=repository)

from src.web.routes import *

if __name__ == "__main__":

    print("🌍 Сервер запускається на http://127.0.0.1:5000")
    app.run(debug=True)