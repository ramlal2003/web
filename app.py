from flask import Flask, render_template, request, jsonify, session, send_file
import os
from image_to_svg import image_to_svg
import time
from PIL import Image
import io
import tempfile
import logging
from logging.handlers import RotatingFileHandler
import shutil
from werkzeug.utils import secure_filename
import cairosvg

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Application startup')

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """Clean up files older than 1 hour"""
    current_time = time.time()
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.getmtime(filepath) < current_time - 3600:  # 1 hour
            try:
                os.remove(filepath)
            except Exception as e:
                app.logger.error(f'Error cleaning up file {filepath}: {str(e)}')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'})
            
            if file and allowed_file(file.filename):
                try:
                    # Clean up old files
                    cleanup_old_files()
                    
                    # Generate a unique filename
                    timestamp = int(time.time())
                    filename = secure_filename(f"{timestamp}_{file.filename}")
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    session['current_file'] = file_path
                    
                    # Process the image
                    output_path = os.path.join('static', 'output.svg')
                    image_to_svg(
                        file_path,
                        output_path,
                        min_contour_len=10,
                        stroke_width=1.0,
                        stroke_color="#FFFFFF",
                        background_color="#000000",
                        threshold_block_size=11,
                        threshold_c=2
                    )
                    return jsonify({'success': True, 'svg_path': '/static/output.svg'})
                except Exception as e:
                    app.logger.error(f'Error processing file: {str(e)}')
                    return jsonify({'error': 'Error processing file'}), 500
            else:
                return jsonify({'error': 'Invalid file type'}), 400
        
        # Handle parameter updates
        if request.form.get('update'):
            if 'current_file' not in session:
                return jsonify({'error': 'No image uploaded yet'})
            
            try:
                min_contour_len = int(request.form.get('minContourLen', 10))
                stroke_width = float(request.form.get('strokeWidth', 1.0))
                threshold_block_size = int(request.form.get('thresholdBlockSize', 11))
                threshold_c = int(request.form.get('thresholdC', 2))
                stroke_color = request.form.get('strokeColor', "#FFFFFF")
                background_color = request.form.get('backgroundColor', "#000000")
                
                input_path = session['current_file']
                output_path = os.path.join('static', 'output.svg')
                
                image_to_svg(
                    input_path,
                    output_path,
                    min_contour_len=min_contour_len,
                    stroke_width=stroke_width,
                    stroke_color=stroke_color,
                    background_color=background_color,
                    threshold_block_size=threshold_block_size,
                    threshold_c=threshold_c
                )
                return jsonify({'success': True, 'svg_path': '/static/output.svg'})
            except Exception as e:
                app.logger.error(f'Error updating parameters: {str(e)}')
                return jsonify({'error': 'Error updating parameters'}), 500
            
    return render_template('index.html')

@app.route('/download_png')
def download_png():
    svg_path = 'static/output.svg'
    if not os.path.exists(svg_path):
        return 'SVG file not found', 404
    
    try:
        # Convert SVG to PNG using cairosvg
        png_data = cairosvg.svg2png(url=svg_path, dpi=300)
        
        # Create BytesIO object and send it
        png_io = io.BytesIO(png_data)
        png_io.seek(0)
        
        return send_file(
            png_io,
            mimetype='image/png',
            as_attachment=True,
            download_name='output.png'
        )
    except Exception as e:
        app.logger.error(f'Error in download_png: {str(e)}')
        return 'Internal server error', 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # In production, use a WSGI server instead of app.run()
    if os.environ.get('FLASK_ENV') == 'production':
        # This will be handled by the WSGI server
        pass
    else:
        app.run(debug=False)  # Disable debug mode in production 