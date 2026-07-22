from flask import Flask, request, jsonify
from pymongo import MongoClient
import json  # opcional, jsonify de Flask suele ser suficiente

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/")
db = client["nombre_de_tu_db"]