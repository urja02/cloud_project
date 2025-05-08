from flask import Flask, render_template, jsonify, request, Response
import sqlite3


app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/api',methods=["POST"])
def getImage():

    
    user_inp = request.files['file'].filename
    db = sqlite3.connect('face_image.db')
    if user_inp[-4:] == ".jpg" or user_inp[-4:] == ".png":
        res = user_inp[:-4]
        

        c =  db.cursor()
        c.execute("SELECT name FROM database WHERE input_img=:input_img",{'input_img': res}) 
        output = c.fetchone() 
        op = {res:output[0]}
        return jsonify(op)
    else:
        return jsonify({'error': 'Bad Request', 'message': 'Invalid data provided'}), 400

# def u
if __name__ == '__main__':
    app.run()