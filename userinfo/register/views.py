
import json
from rest_framework.decorators import APIView
from django.shortcuts import render
from django.http import JsonResponse
import pymongo
from pymongo import MongoClient
import bcrypt
import jwt
from django.conf import settings
from collections import deque
from django.core.files.storage import default_storage
from .NER_model import data
from .ner_09 import create_json
import requests
import logging




secret_key =settings.SECRET_KEY

client = pymongo.MongoClient('mongodb+srv://ansarafitha:root@cluster0.vgtdfso.mongodb.net/test')
# Creating database and collection objects
mydb = client['username']
mycol = mydb['registeration']
mycol.create_index('email', unique=True)


# View function to load the upload form
def insert_details(request): 
    try:
        # Loading the template file
        return render(request,'index.html',status=200)
    except Exception as e:
        # Handle the exception or log the error
        logger = logging.getLogger(__name__)
        logger.exception(str(e))
        return render(request, 'error.html', {'message': 'An error occurred. Please try again later.'}, status=500)

        # # Handle the exception or log the error
        # return render(request, 'error.html', {'message': str(e)},status=500)
        
    
        
    
class takeprofile(APIView):
    # POST method to handle the file upload
    def post(self, request, format=None):
        try:
            # Creating a list of form data and the uploaded file
            data = request.POST
            email=data['email']
            password=data['password']
            # Hash the password before storing it
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
             # Check if the email already exists in the database
            existing_user = mycol.find_one({"email": email})
            # If the email exists, display a message to the user
            if existing_user is not None:
                    return render(request,'index.html',{'message':'An account with this email already exists. Please sign in.'},status=400) 
            # Prepare the data to be inserted into the database    
            mylist={'name':data['name'],'email':email,'phone':data['phone'],'password':hashed_password}
            # Inserting the data into MongoDB
            x = mycol.insert_one(mylist)
            user = mycol.find_one({'email': email})
            if user is not None:
                # Prepare the data to be inserted into the database  
                myflag={'name':data['name'],'email':email,'register_success':"True"}
                 # Inserting the data into MongoDB
                x = mydb.flag.insert_one(myflag)
            else:
                myflag={'name':data['name'],'email':email,'register_success':"False"}
                 # Inserting the data into MongoDB
                x = mydb.flag.insert_one(myflag)
            # Rendering the success page with a success message
            return render(request,'index.html',status=200) 
        except Exception as e:
            # Handle the exception or log the error
            logger = logging.getLogger(__name__)
            logger.exception(str(e))
            return render(request, 'error.html', {'message': 'An error occurred. Please try again later.'}, status=500)

            # return render(request, 'error.html', {'message': str(e)},status=500)
            
    


class reguserprofile(APIView):  
     # GET method to retrieve a profile by name 
    def get(self,request,name):
        try:
            if not name:
                return JsonResponse({"error": "Name parameter is missing."},status=400)
            # Find the profile in the database by name and exclude the ID field
            mydoc = mycol.find({"name": name}, {"_id": 0,"password":0,"token":0})
            result = []
            for x in mydoc:
                result.append(x)
            # Return the profile as a JSON response
            return JsonResponse(result, safe=False)
        except Exception as e:
            # Handle the exception or log the error
            logger = logging.getLogger(__name__)
            logger.exception(str(e))
            return render(request, 'error.html', {'message': 'An error occurred. Please try again later.'}, status=500)

            # return render(request, 'error.html', {'message': str(e)},status=500)
            
    
    
    # DELETE method to delete a profile by name  
    def delete(self,request,name):
        try:
            if not name:
                return JsonResponse({"error": "Name parameter is missing."},status=400)
            # Delete the profile in the database by name
            mydoc= mycol.delete_one({"name":name})
            mydic = mycol.find({},{"_id": 0,"password":0,"token":0})
            result = []
            for x in mydic:
                result.append(x)
            # Return all profiles as a JSON response
            return JsonResponse(result, safe=False)
        except Exception as e:
            # Handle the exception or log the error
            logger = logging.getLogger(__name__)
            logger.exception(str(e))
            return render(request, 'error.html', {'message': 'An error occurred. Please try again later.'}, status=500)

            # return render(request, 'error.html', {'message': str(e)},status=500)
            
        

        
        
def login_view(request):
    try:
        if request.method =='POST':
            email = request.POST['emailid']
            password = request.POST['password']
            # Query the user collection for the provided email
            user = mycol.find_one({'email': email})
            if user is not None:
                hashed_password = user['password']
                # Check if the provided password matches the hashed password in the database
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    # Authentication successful
                    # Generate a token
                    token = jwt.encode({'email': email},settings.SECRET_KEY, algorithm='HS256')
                    # Store the token in the user document in MongoDB
                    mycol.update_one({'email': email}, {'$set': {'token': token}})
                    users = mycol.find_one({'email': email})
                    # Check if the 'token' field exists in the user document
                    if 'token' in users:
                        # 'token' field exists
                        # update the database  
                        mydb.flag.update_one({'email': email}, {'$set': {'login_success': "True"}})
                    else:
                        # 'token' field does not exist
                        mydb.flag.update_one({'email': email}, {'$set': {'login_success': "False"}})
                    # Render the upload template with the email variable
                    return render(request,'upload.html',{'email':email})
                # Render the index template with an error message
            return render(request, 'index.html',{'error':'Invalid email or password.'},status=401)
        
    except Exception as e:
        # Handle the exception or log the error
        logger = logging.getLogger(__name__)
        logger.exception(str(e))
        return render(request, 'error.html', {'message': 'An error occurred. Please try again later.'}, status=500)

        # return render(request, 'error.html', {'message': str(e)}, status=500)
    
    
        
def forgot_password(request):
    try:
        # Loading the template file
        return render(request, 'forgotpassword.html',status=200)
    except Exception as e:
        # Handle the exception or log the error
        logger = logging.getLogger(__name__)
        logger.exception(str(e))
        return render(request, 'error.html', {'message': 'An error occurred. Please try again later.'}, status=500)

        # return render(request, 'error.html', {'message': str(e)},status=500)
        
    
        


def mailid_auth(request):
    try:
        if request.method =='POST':
            # Get the email from the request
            email = request.POST['emailid']
            user = mycol.find_one({'email': email})
            if user is not None:
                user_emailid = user['email']
                if email==user_emailid:
                    return render(request,'setpassword.html',{'email': email}, status=200)
            else:
                #  if user is not None:
                     return render(request,'index.html',{'messages':'The email address provided does not exist in our records. Please register a new account.'}, status=400)               
    except Exception as e:
        # Handle the exception or log the error
        logger = logging.getLogger(__name__)
        logger.exception(str(e))
        return render(request, 'error.html', {'message': 'An error occurred. Please try again later.'}, status=500)

        # return render(request, 'error.html', {'message': str(e)}, status=500)
        
def reset_password(request):
    try:
        if request.method =='POST':
            # Get the email from the request
            email = request.POST['emailid']
            password = request.POST['password']
            user = mycol.find_one({'email': email})
            # Hash the password before storing it
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            # Store the token in the user document in MongoDB
            mycol.update_one({'email': email}, {'$set': {'password':hashed_password}})
            # Rendering the success page with a success message
            return render(request,'index.html')      
    except Exception as e:
        # Handle the exception or log the error
        logger = logging.getLogger(__name__)
        logger.exception(str(e))
        return render(request, 'error.html', {'message': 'An error occurred. Please try again later.'}, status=500)

        # return render(request, 'error.html', {'message': str(e)},status=500)
             
        
# def upload_view(request):
#     try:
#         if request.method =='POST':
#             # Get the email from the request
#             email = request.POST['emailid']
#             # Get the uploaded file from the request
#             file = request.FILES['json_file']
            # Save the uploaded file to a specific location
    #         file_path = default_storage.save('uploads/' + file.name, file)
    #         # Add the file path to the deque
    #         pdf_deque.append(file_path)
    #         for file_path in pdf_deque:
    #             # print(file_path)
    #             json_data=data(file_path)
    #             # json_data=create_json(file_path)
    #         last_element=pdf_deque.pop()
    #         print(json_data)
    #         document = json.loads(json_data)
    #         print(document)
    #         mylist={'email':email, 'resume':document,'path':file_path}
    #         # # # # # Insert the document into the 'userdemo' collection in MongoDB
    #         x = mydb.userdemo.insert_one(mylist)
    #         #  # Return a success response
    #         # return_dict = {"Request":request, "file_path":file_path}
    #         return render(request,'message.html')
    # except Exception as e:
        # Handle the exception or log the error
        # return render(request, 'error.html', {'message': str(e)})

    
def upload_view(request):
    try:
        if request.method =='POST':
            # Get the email from the request
            email = request.POST['emailid']
            # Get the uploaded file from the request
            file = request.FILES['json_file']
            #upload the file to HDFS
            url = f'http://ec2-43-205-15-58.ap-south-1.compute.amazonaws.com:9864/webhdfs/v1/cv/{file.name.replace(" ","_")}?op=CREATE&user.name=ubuntu&namenoderpcaddress=ec2-43-205-15-58.ap-south-1.compute.amazonaws.com:9000&createflag=&createparent=true&overwrite=false'
            # print(file.name.replace(" ","_"))
            headers = {'Content-Type': 'application/octet-stream'}
            response = requests.put(url, data=file, headers=headers)
            #checking the status
            if response.status_code == 201:
                mydb.flag.update_one({'email': email}, {'$set': {'uploadhdfs_success': "True"}})
                print(f'{file.name} added to HDFS')
            else:
                mydb.flag.update_one({'email': email}, {'$set': {'uploadhdfs_success': "False"}})
                print(f'HDFS Error: {response.text}')
            mylist={'email':email,'path':f'/cv/{file.name.replace(" ","_")}'}
            # # # # # Insert the document into the 'userdemo' collection in MongoDB
            x = mydb.userdemo.insert_one(mylist)
            #creating flag
            user = mydb.userdemo.find_one({'email': email})
            if user is not None:
                mydb.flag.update_one({'email': email}, {'$set': {'filepathsave_success': "True"}})
            else:
                mydb.flag.update_one({'email': email}, {'$set': {'filepathsave_success': "False"}})   
            #  # Return a success response
            # return_dict = {"Request":request, "file_path":file_path}
            return render(request,'message.html')
    except Exception as e:
        # Handle the exception or log the error
        logger = logging.getLogger(__name__)
        logger.exception(str(e))
        return render(request, 'error.html', {'message': 'An error occurred. Please try again later.'}, status=500)

        # return render(request, 'error.html', {'message': str(e)},status=500)
    

    
            
            
            # Save the uploaded file to a specific location
    #         file_path = default_storage.save('uploads/' + file.name, file)
    #         # Add the file path to the deque
    #         pdf_deque.append(file_path)
    #         for file_path in pdf_deque:
    #             # print(file_path)
    #             json_data=data(file_path)
    #             # json_data=create_json(file_path)
    #         last_element=pdf_deque.pop()
    #         print(json_data)
    #         document = json.loads(json_data)
    #         print(document)
    #         mylist={'email':email, 'resume':document,'path':file_path}
    #         # # # # # Insert the document into the 'userdemo' collection in MongoDB
    #         x = mydb.userdemo.insert_one(mylist)
    #         #  # Return a success response
    #         # return_dict = {"Request":request, "file_path":file_path}
    #         return render(request,'message.html')
    # except Exception as e:
        # Handle the exception or log the error
        # return render(request, 'error.html', {'message': str(e)})
    

    
        
    
        

      
            







        
        
      
            







        
    