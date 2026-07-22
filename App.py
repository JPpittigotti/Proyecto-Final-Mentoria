# punto de entrada

from flask import Flask, request, jsonify
from pymongo import MongoClient
import json

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/")
db = client["nombre_de_tu_db"]