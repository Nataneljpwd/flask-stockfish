from flask import Flask, request, jsonify, session, make_response
from stockfish import Stockfish
import chess

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
    path = (
        os.getcwd()
        + "/stockfish_15.1_win_x64_avx2/stockfish-windows-2022-x86-64-avx2.exe"
    )
else:
    path = (
        os.getcwd()
        + "/stockfish_15.1_linux_x64_avx2/stockfish-ubuntu-20.04-x86-64-avx2"
    )

stockfish = Stockfish(path)
app.secret_key = "BAD_SERET_KEY"


@app.route("/ai", methods=["POST"])
def get_best_move():
    move = request.data.decode("UTF-8")
    if move is None or move == "":
        mv = to2DArrayIndex(stockfish.get_best_move())
        return make_response(mv, 200)
    # we convert all the moves to the list
    moves = move.split()
    if moves[-1] == "":
        moves.pop()
    if moves[-1].isdigit():
        stockfish.set_elo_rating(moves.pop())
    print(moves)
    board = chess.Board()
    stockfish.set_position(moves)
    for mov in moves:
        board.push(chess.Move.from_uci(mov))
    best_move = stockfish.get_best_move()
    board.push(chess.Move.from_uci(best_move))
    outcome = board.outcome()
    if outcome is not None:
        res = outcome.result()
        print(res)
        if res == "1/2-1/2":
            # its a draw
            if board.is_stalemate():
                print("STALEMATE")
                return jsonify("STALEMATE+" + to2DArrayIndex(best_move))
            if board.is_insufficient_material():
                print("INSUFFICIENT_MATERIAL")
                return jsonify("MATERIAL+" + to2DArrayIndex(best_move))
            if board.is_fivefold_repetition():
                print("FIVEFOLD_REP")
                return jsonify("REPETITION+" + to2DArrayIndex(best_move))
            if board.is_fifty_moves():
                print("FIFTY_MOVE " + best_move)
                return jsonify("FIFTY_MOVE+" + to2DArrayIndex(best_move))
        elif res == "1-0":
            # the white won
            print("WHITE_WON")
            return jsonify(
                "MATE-WHITE+" + to2DArrayIndex(best_move)
            )  # means the white won
        elif res == "0-1":
            print("BLACK_WON")
            return jsonify(
                "MATE-BLACK+" + to2DArrayIndex(best_move)
            )  # means the black won
    # or get top n moves using stockfish.get_top_moves(3)
    print(stockfish.get_board_visual())
    return jsonify(to2DArrayIndex(best_move))


# return jsonify(best_move):w


def to2DArrayIndex(algebraicNotation):
    file1, rank1, file2, rank2 = (
        algebraicNotation[0],
        algebraicNotation[1],
        algebraicNotation[2],
        algebraicNotation[3],
    )
    promotion = ""
    if len(algebraicNotation) == 5:
        promotion = algebraicNotation[4]

    file1 = string.ascii_lowercase.index(file1)
    file2 = string.ascii_lowercase.index(file2)

    rank1 = int(rank1) - 1
    rank2 = int(rank2) - 1
    rank1, rank2 = 7 - rank1, 7 - rank2

    square = f"{rank1},{file1}:{rank2},{file2}" + (
        f":{promotion}" if len(algebraicNotation) == 5 else ""
    )

    return square


if __name__ == "__main__":
    app.debug = True
    app.run(port=8080)
