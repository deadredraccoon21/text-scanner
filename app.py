from flask import Flask, render_template, request, redirect, url_for
import easyocr
import os
import gc
from werkzeug.utils import secure_filename

# Initialize the Flask app and the OCR reader
app = Flask(__name__)

# Use smaller model if available (EasyOCR has options for different model sizes)
reader = easyocr.Reader(['en'], gpu=False)  # Disable GPU if not needed to save memory

# Configure upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = 'static/uploaded_images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file upload to 16 MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Route for file upload and OCR processing
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Perform OCR on the uploaded file
        try:
            result = reader.readtext(file_path)

            # Extract text from OCR result
            extracted_text = "\n".join([item[1] for item in result])

            # Correct path for serving static files (use forward slashes)
            image_path = os.path.join('uploaded_images', filename).replace('\\', '/')

        except Exception as e:
            return f"Error during OCR processing: {str(e)}"

        # Clear memory after processing
        gc.collect()

        return render_template('index.html', extracted_text=extracted_text, image_path=image_path)
    
    return redirect(request.url)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
