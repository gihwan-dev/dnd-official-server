import certifi
from pydantic import BaseSettings
from pymongo import MongoClient
from app.const.const import DB_URL


def connect_database():
    # 드라이버를 통해 연결할 데이터베이스 URL

    DATABASE_URL = DB_URL

    ca = certifi.where()

    # 데이터베이스에 연결
    return MongoClient(DATABASE_URL, tlsCAFile=ca)


# 이렇게하면 재사용 가능하게 된다고 함
if __name__ == "__main__":
    dbname = connect_database()

