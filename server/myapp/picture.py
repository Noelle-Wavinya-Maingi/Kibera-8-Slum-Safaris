from flask import  request, jsonify
from myapp import  cloudinary, app

# Upload route
@app.route('/upload', methods=['POST', 'GET'])
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
