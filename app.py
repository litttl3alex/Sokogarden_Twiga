# import flask
from flask import *
import pymysql
import pymysql.cursors
import os
from flask_cors import CORS
# create flask app
app = Flask(__name__)
CORS(app)
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

# mpesa payment
# Mpesa Payment Route 
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    if request.method == 'POST':
        # Extract POST Values sent
        amount = request.form['amount']
        phone = request.form['phone']

        # Provide consumer_key and consumer_secret provided by safaricom
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        # Authenticate Yourself using above credentials to Safaricom Services, and Bearer Token this is used by safaricom for security identification purposes - Your are given Access
        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        # Provide your consumer_key and consumer_secret 
        response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        # Get response as Dictionary
        data = response.json()
        # Retrieve the Provide Token
        # Token allows you to proceed with the transaction
        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')  # Current Time
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Passkey(Safaricom Provided)
        business_short_code = "174379"  # Test Paybile (Safaricom Provided)
        # Combine above 3 Strings to get data variable
        data = business_short_code + passkey + timestamp
        # Encode to Base64
        encoded = base64.b64encode(data.encode())
        password = encoded.decode()

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password":password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": "1",  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://coding.co.ke/api/confirm.php",
            "AccountReference": "SokoGarden Online",
            "TransactionDesc": "Payments for Products"
        }

        # POPULAING THE HTTP HEADER, PROVIDE THE TOKEN ISSUED EARLIER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        # Specify STK Push  Trigger URL
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  
        # Create a POST Request to above url, providing headers, payload 
        # Below triggers an STK Push to the phone number indicated in the payload and the amount.
        response = requests.post(url, json=payload, headers=headers)
        print(response.text) # 
        # Give a Response
        return jsonify({"message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"})

if __name__ == '__main__':
    app.run(debug=True)