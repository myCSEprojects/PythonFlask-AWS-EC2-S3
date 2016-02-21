from flask import Flask, request, render_template, send_file
import os

from boto3.session import Session

app = Flask(__name__)

session = Session(aws_access_key_id='',
                  aws_secret_access_key='',
                  region_name='us-west-2')


s3 = session.resource('s3')
#s3 = boto3.resource('s3')
bucketname = 'jeet-aws-cloud-cse-6331'
bucketObject = s3.Bucket(bucketname)

@app.route('/')
def hello_world():
    return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename=file.filename
        if filename != "":
            file_contents = file.stream.read()
            # Upload a new file
            s3.Bucket(bucketname).put_object(Key=filename, Body=file_contents)
            return render_template('result.html',result="Image '"+filename+"' successfully uploaded to S3 storage.")
        else:
            return render_template('result.html',result="Please select the file.")

@app.route('/list', methods=['GET', 'POST'])
def list():
    files = []
    for bucket in s3.buckets.all():
        for key in bucket.objects.all():
            print key
            fileinfo = {}
            fileinfo['filename'] = key.key
            files.append(fileinfo)

    return render_template('list.html',files=files)

@app.route('/download', methods=['GET', 'POST'])
def download():
    #filename=request.args.get('filename')
    filename, file_extension = os.path.splitext(request.args.get('filename'))
    s3.Bucket(bucketname).download_file(filename+file_extension, '/home/jeet/download')
    with open('/home/jeet/download', 'r') as example_file:
        filecontents = example_file.read()
    result= "File '" + filename+file_extension + "' downloaded successfully."

    file_download = open('/home/jeet/'+filename+file_extension, 'wb')

    file_download.write(filecontents);
    file_download.close()
    file_download = open('/home/jeet/'+filename+file_extension, 'rb')

    return send_file(file_download.name, as_attachment=True)


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    filename_delete=request.args.get('filename')
    for key in bucketObject.objects.all():
        if key.key == filename_delete:
            key.delete()

    return render_template('result.html',result="File '"+filename_delete+"' deleted successfully from S3 storage.")



@app.route('/signin', methods=['GET', 'POST'])
def signin():
    username=request.args.get('inputUsername')
    s3.Bucket(bucketname).download_file('users.txt', '/home/jeet/users.txt')
    with open('/home/jeet/users.txt', 'r') as example_file:
        users = example_file.read().splitlines()

    for user in users:
        if user == username:
            return render_template('index.html')

    return "User name is not valid"


port = os.getenv('VCAP_APP_PORT', '4000')

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
