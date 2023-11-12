from flask import Flask, render_template, request, jsonify
from myapp import os , cloudinary

app = Flask(__name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('ddi2x0uf9'),
    api_key=os.getenv('677945454898332'),
    api_secret=os.getenv('GmNEkzXoXwSrY-1MkfSBZ255FD4')
)
# Home route
@app.route('/')
def hello():
    return "Hello World!"

# Upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if request.method == 'POST':
            file_to_upload = request.files['file']
            
            if file_to_upload:
                # Upload file to Cloudinary
                upload_result = cloudinary.uploader.upload(file_to_upload)
                
                # Extract the image URL from the Cloudinary upload result
                image_url = upload_result.get('secure_url')
                
                # Return the image URL as a JSON response
                return jsonify({"image_url": image_url})
                
    except Exception as e:
        return jsonify({"error": str(e)}), 500
