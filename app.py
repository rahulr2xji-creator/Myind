from flask import Flask, request, jsonify
import requests
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii
import like_count_pb2
import uid_generator_pb2

app = Flask(__name__)

# 🔑 tokens file load
def load_tokens():
    with open("token_ind.json","r") as f:
        return json.load(f)

# 🔐 encrypt uid protobuf
def encrypt_message(plaintext):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(plaintext, AES.block_size)).hex()

def create_uid_protobuf(uid):
    msg = uid_generator_pb2.uid_generator()
    msg.saturn_ = int(uid)
    msg.garena = 1
    return msg.SerializeToString()

# 📡 get player info from Free Fire server
def get_player(uid):
    token = load_tokens()[0]["token"]
    enc = encrypt_message(create_uid_protobuf(uid))

    url = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0"
    }

    r = requests.post(url, data=bytes.fromhex(enc), headers=headers, verify=False)

    info = like_count_pb2.Info()
    info.ParseFromString(r.content)

    return {
        "PlayerName": info.AccountInfo.PlayerNickname,
        "PlayerLevel": info.AccountInfo.AccountLevel,
        "PlayerUID": info.AccountInfo.UID
    }

@app.route("/player")
def player():
    uid = request.args.get("uid")
    if not uid:
        return {"error":"uid required"},400
    try:
        return jsonify(get_player(uid))
    except:
        return {"error":"player not found"},404

app.run()
