import os

""" Порт сервера """
PORT = 8000

""" Файл для хранения данных """
STORAGE_FILE = "storage.json"

""" Хост сервера """
HOST = ""

""" Кодировка """
ENCODING = "utf-8"

"""Пути API"""
CREATE = "/create"           # POST /create - создание записи
GET_LIST = "/get_list"       # GET /get_list - получение всех записей
GET_DETAIL = "/get_detail"   # GET /get_detail/{id}