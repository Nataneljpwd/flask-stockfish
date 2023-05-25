from flask import Flask, request, jsonify, session, make_response
from stockfish import Stockfish

from sys import platform
import os
import string

app = Flask(__name__)
# change to the location of stockfish

path = ""
# if platform == "linux" or platform == "linux2":
#     path = os.path.abspath("linux-ai")
if platform == "darwin":
    path = os.path.abspath("mac-arm")
elif platform == "win32":
    path = os.getcwd() + "/stockfish_15.1_win_x64_avx2/stockfish-windows-2022-x86-64-avx2.exe"
else:
    path = os.getcwd() + "/stockfish_15.1_linux_x64_avx2/stockfish-ubuntu-20.04-x86-64-avx2" 

stockfish = Stockfish(path)
app.secret_key = 'BAD_SERET_KEY'


@app.route("/ai", methods=["POST"])
def get_best_move():
    move = request.get_json()
    if (session.get("moves") is None):
        session["moves"] = [move]
    elif not session["moves"][-1] == move:
        session["moves"].append(move)
        session.modified = True

    print(session["moves"])
    stockfish.set_position(session.get("moves"))

    # # or get top n moves using stockfish.get_top_moves(3)
    # best_move = stockfish.get_best_move()
    # best_move.sp
    print(stockfish.get_best_move())
    return make_response(to2DArrayIndex(stockfish.get_best_move()), 200)
# return jsonify(best_move):w


@app.route("/clear", methods=["POST"])
def clear_session():
    session.pop("moves", None)
    return make_response("success!", 200)


def to2DArrayIndex(algebraicNotation):
    file1, rank1, file2, rank2 = algebraicNotation[0], algebraicNotation[
        1], algebraicNotation[2], algebraicNotation[3]

    file1 = string.ascii_lowercase.index(file1)
    file2 = string.ascii_lowercase.index(file2)

    rank1 = int(rank1)-1
    rank2 = int(rank2)-1
    rank1, rank2 = 7-rank1, 7-rank2

    square = f"{file1},{rank1}:{file2},{rank2}"

    return square


if __name__ == "__main__":
    app.run(port=8080, debug=True)
