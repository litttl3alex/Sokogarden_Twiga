# import flask
from flask import *
import pymysql
import pymysql.cursors
import os
# create flask app
app = Flask(__name__)
# configure our upload folder
app.config['UPLOAD_FOLDER'] = 'static/images'
@app.route('/api/signup',methods = ['POST'])
def signup():
    # extract values posted by the user
    username  =  request.form['username']
    email  =  request.form['email']
    password  = request.form['password']
    phone  = request.form['phone']
    # connection DataBase
    connection  =  pymysql.connect(host='localhost',user='root',password='',database='Dailyyoghurt_Twiga')
    # create a cursor to initialize the connection
    cursor = connection.cursor()
    # wtite sql querry
    sql ='INSERT INTO users(username,password,email,phone)VALUES(%s,%s,%s,%s)'

    # PREPARE DATA TO REPLACE PLACEHOLDER
    data = (username,password,email,phone)
    # execute the data and the sql using the cursor
    cursor.execute(sql,data)
    # commit./save changes to the database
    connection.commit()

    return jsonify({'success':'Thanks for joining'})
      
    #  SIGN IN ROUTE
@app.route('/api/signin',methods = ['POST'])
def sign():
    # Extract post data
    username = request.form['username']
    password = request.form['password']

    # Connection to database
    connection = pymysql.connect(host = 'localhost', user = 'root', password = '', database = 'Dailyyoghurt_Twiga')

    # Create a cursor object database
    cursor = connection.cursor(pymysql.cursors.DictCursor)
      
    # SQL QUERY
    sql = 'Select * from users where username = %s AND password = %s' 
    Data = (username , password)
    cursor.execute (sql , Data)

    # count as the cursor returns zero or row
    count = cursor.rowcount

    if count == 0: # if rows is zero == invalid credatials
        return jsonify ({'message' : 'log in failed'})
    else:
        # if the cursor as returned a valid user or atleast a row
        user = cursor.fetchone()
        user.pop('password', None)
        return jsonify({'message': 'log in successfully','user': user}) 

# Add a Product
@app.route('/api/add_products',methods = ['POST'])
def add_products():
    # extract data value from database
    product_name = request.form['product_name']
    product_description = request.form['product_description']
    product_cost = request.form['product_cost']

    # Extracting image data
    product_photo = request.files['product_photo']

    # get the image file name
    filename = product_photo.filename

    # specify where the image will be saved(path)
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)

    # save your images to the path specified above
    product_photo.save(photo_path)

    # Database connection
    Connection = pymysql.connect(host = 'localhost', user = 'root',password='', database='Dailyyoghurt_Twiga')

    # cursor Connection 
    cursor = Connection.cursor()

    # sql query
    sql = 'INSERT INTO product_details(product_name,product_description,product_cost,product_photo)VALUES(%s,%s,%s,%s)'

    # prepare data
    data = (product_name,product_description,product_cost,filename)

    cursor.execute(sql , data)
    Connection.commit()

    return jsonify({'message':'products added successful'}) 
    
@app.route('/api/get_products_details')
def get_products_details():

    # connection
    connection = pymysql.connect(host='localhost',user='root',password='',database='Dailyyoghurt_Twiga')

    cursor = connection.cursor(pymysql.cursors.DictCursor) 

    # sql query
    sql = 'select * from product_details'

    # execute the sql alone
    cursor.execute(sql)

    # get the records in dictonary format
    product_details = cursor.fetchall()

    return jsonify(product_details)

if __name__ == '__main__':
    app.run(debug=True)