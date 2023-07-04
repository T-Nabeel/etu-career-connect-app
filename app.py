# Importing Flask class and boto3
from flask import Flask, render_template, request, session
import boto3
import urllib.parse
from boto3.dynamodb.conditions import Key, Attr
import key_config as keys # Importing key_config file
import dynamodb_handler as db_handler


# Get the service resource - DynamoDB resrouce object
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id = keys.ACCESS_KEY_ID,
    aws_secret_access_key = keys.ACCESS_SECRET_KEY,
    region_name = keys.REGION_NAME
)

# s3 resource object
s3 = boto3.resource(
    's3',
    aws_access_key_id = keys.ACCESS_KEY_ID,
    aws_secret_access_key = keys.ACCESS_SECRET_KEY,
    region_name = keys.REGION_NAME
)

app = Flask(__name__) # Creating an instance of Flask class
app.secret_key = 'jS30y5w@2BX!' # Setting secret key for sesssion

# Route decorator to create the table
# @app.route("/")
# def index():
#     db_handler.create_table_student()
#     return 'Table created'

# Route decorator to load login page
@app.route("/")
def index():
    return render_template('login.html')

# Route decorator to load signup page
@app.route("/signup")
def signup():
    return render_template('signup.html')
    
# Route to handle login
@app.route("/login", methods=['post'])
def login():
    if request.method == "POST":
        
        # Defining variables for form data
        reg_no = request.form['regno']
        email = request.form['email']
        password = request.form['password']
        
        # Converting reg_no to an integer
        reg_no = int(request.form['regno'])
        
        # Getting the dynamodb table
        table_students = dynamodb.Table('students')
        
        # Quering through table
        response = table_students.query (
            KeyConditionExpression = Key('registration_number').eq(reg_no)
        )
        items = response['Items'] # items will be a python list
        
        # Iterate through all items to find a matching user
        for item in items:
            if password == item['password']:
                
                # Store registration number and email in session
                session['registration_number'] = item['registration_number']
                session['email'] = item['email']
                
                # Getting all the fields
                first_name = item['first_name']
                last_name = item['last_name']
                email = item['email']
                reg_no = item['registration_number']
                deg_programme = item['degree_programme']
                password = item['password']
                contact_no = item['contact_number']
                gpa = item['gpa']
                # gender = item['gender']
                gender = item.get('gender', '') # will return an empty string instead of raising a KeyError
                intro = item['introduction']
                skills = item['skills']
                # profile_image = item['profile_image_url']
                profile_image = item.get('profile_image_url', '')

                
                # Returning queried items
                return render_template(
                    'profile-edit.html',
                    first_name = first_name,
                    last_name = last_name,
                    email = email,
                    reg_no = reg_no,
                    deg_programme = deg_programme,
                    password = password,
                    contact_no = contact_no,
                    gpa = gpa,
                    gender = gender,
                    intro = intro,
                    skills = skills,
                    profile_image = profile_image
                )
        
    return render_template('login.html')
    
    
# Route to handle create account
@app.route("/createaccount", methods=['post'])
def create_account():
    if request.method == "POST":
        
        # Defining variables for form data
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        reg_no = request.form['regno']
        deg_programme= request.form['degprogramme']
        password = request.form['password']
        contact_no = request.form['contactno']
        gpa = request.form['gpa']
        gender = request.form['gender']
        intro = request.form['intro']
        skills = request.form['skills']
        
        # Converting reg_no to an integer
        reg_no = int(request.form['regno'])
        
        # Getting the dynamodb table
        table_students = dynamodb.Table('students')
        
        # Inserting data into the table
        table_students.put_item(
            Item = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'registration_number' : reg_no,
                'degree_programme' : deg_programme,
                'password' : password,
                'contact_number' : contact_no,
                'gpa' : gpa,
                'gender' : gender,
                'introduction' : intro,
                'skills' : skills
            }
        )
        
        signup_complete_msg = "Account created. Please Login to your account!"
        
        return render_template('login.html', signup_complete_msg = signup_complete_msg)
    return render_template('signup.html')


# Route to handle updating a user's profile
@app.route("/login/<int:regno>", methods=['PUT'])
def update_profile(regno):
    
    # Get the data sent in the PUT request as JSON
    data = request.get_json()
    
     # Extract fields from the data
    firstname = data['firstname']
    lastname = data['lastname']
    email = data['email']
    degprogramme = data['degprogramme']
    password = data['password']
    contactno = data['contactno']
    gpa = data['gpa']
    gender = data['gender']
    intro = data['intro']
    skills = data['skills']
    
    response = db_handler.update_student_account_details(regno, email, firstname, lastname, degprogramme, password, contactno, gpa, gender, intro, skills)
    
    if (response['ResponseMetadata']['HTTPStatusCode'] == 200):
        updated_msg = 'Account details updated!'
        return render_template('profile-edit.html', updated_msg = updated_msg)

    error_msg = 'Some error occurred'
    return render_template('profile-edit.html', error_msg = error_msg)
    
    # try:
    #     db_handler.update_student_account_details(regno, email, firstname, lastname, degprogramme, password, contactno, gpa, intro, skills)
    #     updated_msg = 'Account details updated!'
    #     return render_template('profile-edit.html', updated_msg=updated_msg)
        
    # except Exception as e:
    #     error_msg = 'Some error occurred'
    #     return render_template('profile-edit.html', error_msg=error_msg)

    

# Route to handle displaying a user's profile
@app.route("/profile/<int:regno>")
def profile(regno):
    # Query the DynamoDB table to get the student details for the given registration number
    table_students = dynamodb.Table('students')
    response = table_students.query(
        KeyConditionExpression=Key('registration_number').eq(regno)
    )
    
    # Check if any items were returned by the query
    if response['Items']:
        # Get the first item returned by the query
        student = response['Items'][0]
        
        # Extract the student details from the item
        name = f"{student['first_name']} {student['last_name']}"
        email = student['email']
        degree_programme = student['degree_programme']
        contactno = student['contact_number']
        gpa = student['gpa']
        gender = student.get('gender', '')
        intro = student['introduction']
        skills = student['skills']
        profile_image_url = student.get('profile_image_url', '')
        
        # Render the profile.html template with the student details
        return render_template(
            'profile-view.html',
            regno=regno,
            name=name,
            email=email,
            degree_programme=degree_programme,
            contactno=contactno,
            gpa=gpa,
            gender=gender,
            intro=intro,
            skills=skills,
            profile_image_url=profile_image_url
        )
    else:
        # No items were returned by the query, so display an error message
        error_msg = 'Student not found'
        return render_template('profile-view.html', error_msg=error_msg)
        
        
# Route handle image upload
@app.route("/imageupload", methods=['post'])
def imageUpload():
    file = request.files['profileimage']
    filename = file.filename
        
    # Check if a file was selected
    # if not filename:
    #     image_updated_msg = 'Image not uploaded'
    #     return render_template('profile-edit.html', image_updated_msg=image_updated_msg)
        
    bucket_name = 'eduxbucket'
    bucket = s3.Bucket(bucket_name)
    bucket.put_object(
        Key=filename,
        Body=file,
        ContentType='image/jpeg',
        ContentDisposition='inline'
    )
        
    encoded_object_key = urllib.parse.quote(filename)
    object_url = f"https://{bucket_name}.s3.amazonaws.com/{encoded_object_key}"
        
    # Get registration number and email from session
    registration_number = int(session.get('registration_number'))
    email = session.get('email')
        
    # Debug statements
    # print(f"registration_number: {registration_number}")
    # print(f"email: {email}")
    
    # Getting the dynamodb table
    table_students = dynamodb.Table('students')
    
    # Update DynamoDB table with object_url
    response = table_students.update_item(
        Key={
            'registration_number': registration_number,
            'email': email
        },
        UpdateExpression='SET profile_image_url = :val1',
        ExpressionAttributeValues={
            ':val1': object_url
        }
    )
        
    # Query DynamoDB table to get item for currently logged-in user
    response = table_students.query(
        KeyConditionExpression=Key('registration_number').eq(registration_number) & Key('email').eq(email)
    )
    item = response['Items'][0]
    
    # Extract attribute values from item
    first_name = item['first_name']
    last_name = item['last_name']
    email = item['email']
    reg_no = item['registration_number']
    deg_programme = item['degree_programme']
    password = item['password']
    contact_no = item['contact_number']
    gpa = item['gpa']
    gender = item['gender']
    intro = item['introduction']
    skills = item['skills']
    
    image_updated_msg = 'Image updated'
    return render_template(
        'profile-edit.html',
        image_updated_msg=image_updated_msg,
        profile_image=object_url,
        first_name=first_name,
        last_name=last_name,
        email=email,
        reg_no=reg_no,
        deg_programme=deg_programme,
        password=password,
        contact_no=contact_no,
        gpa=gpa,
        gender=gender,
        intro=intro,
        skills=skills
    )

    
# Start the Flask development server
if __name__ == '__main__':
    app.run(debug = True, port = 8080, host = '0.0.0.0')