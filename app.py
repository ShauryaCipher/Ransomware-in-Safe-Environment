import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import tempfile
import shutil
import uuid
from crypto import encrypt_directory, decrypt_directory, generate_key

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "development_secret_key")

# Temporary storage for simulation data
TEMP_DIR = tempfile.gettempdir()
UPLOAD_FOLDER = os.path.join(TEMP_DIR, 'ransomware_simulation')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions for simulation
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/simulation', methods=['GET', 'POST'])
def simulation():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'files[]' not in request.files:
            flash('No files selected', 'danger')
            return redirect(request.url)
        
        files = request.files.getlist('files[]')
        
        # If user does not select files, browser submits empty part without filename
        if not files or files[0].filename == '':
            flash('No files selected', 'danger')
            return redirect(request.url)
            
        # Create unique session ID to track this simulation
        simulation_id = str(uuid.uuid4())
        simulation_dir = os.path.join(app.config['UPLOAD_FOLDER'], simulation_id)
        os.makedirs(simulation_dir)
        
        # Save all uploaded files
        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(simulation_dir, filename)
                file.save(filepath)
                saved_files.append(filename)
        
        if not saved_files:
            flash('No valid files were uploaded', 'warning')
            # Clean up empty directory
            shutil.rmtree(simulation_dir)
            return redirect(request.url)
        
        # Generate encryption key
        key = generate_key()
        
        # Encrypt the directory
        try:
            encrypted_files = encrypt_directory(simulation_dir, key)
            
            # Store simulation info in session
            session['simulation_id'] = simulation_id
            session['encryption_key'] = key.decode('utf-8')
            session['encrypted_files'] = encrypted_files
            session['original_filenames'] = saved_files
            
            logger.info(f"Simulation {simulation_id} created with {len(encrypted_files)} encrypted files")
            
            flash(f'Successfully encrypted {len(encrypted_files)} files for simulation', 'success')
            return redirect(url_for('ransom_note'))
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            flash(f'Encryption failed: {str(e)}', 'danger')
            # Clean up files on error
            shutil.rmtree(simulation_dir)
            return redirect(request.url)
    
    return render_template('simulation.html')

@app.route('/ransom_note')
def ransom_note():
    # Ensure simulation exists
    if 'simulation_id' not in session:
        flash('No active simulation found', 'danger')
        return redirect(url_for('simulation'))
    
    simulation_id = session['simulation_id']
    encrypted_files = session.get('encrypted_files', [])
    original_filenames = session.get('original_filenames', [])
    
    return render_template('recovery.html', 
                          simulation_id=simulation_id, 
                          encrypted_files=encrypted_files,
                          original_filenames=original_filenames)

@app.route('/decrypt', methods=['POST'])
def decrypt():
    # Ensure simulation exists
    if 'simulation_id' not in session:
        flash('No active simulation found', 'danger')
        return redirect(url_for('simulation'))
    
    simulation_id = session['simulation_id']
    key = session.get('encryption_key', '').encode('utf-8')
    
    simulation_dir = os.path.join(app.config['UPLOAD_FOLDER'], simulation_id)
    
    if not os.path.exists(simulation_dir):
        flash('Simulation directory not found', 'danger')
        return redirect(url_for('simulation'))
    
    try:
        decrypted_files = decrypt_directory(simulation_dir, key)
        
        # Clear simulation data after successful decryption
        session.pop('simulation_id', None)
        session.pop('encryption_key', None)
        session.pop('encrypted_files', None)
        session.pop('original_filenames', None)
        
        logger.info(f"Successfully decrypted {len(decrypted_files)} files for simulation {simulation_id}")
        
        flash(f'Successfully decrypted {len(decrypted_files)} files', 'success')
        # Clean up files after decryption
        shutil.rmtree(simulation_dir)
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Decryption failed: {str(e)}")
        flash(f'Decryption failed: {str(e)}', 'danger')
        return redirect(url_for('ransom_note'))

@app.route('/clear_simulation')
def clear_simulation():
    # Clean up the simulation if user cancels
    if 'simulation_id' in session:
        simulation_id = session['simulation_id']
        simulation_dir = os.path.join(app.config['UPLOAD_FOLDER'], simulation_id)
        
        if os.path.exists(simulation_dir):
            shutil.rmtree(simulation_dir)
            logger.info(f"Cleaned up simulation {simulation_id}")
        
        # Clear session data
        session.pop('simulation_id', None)
        session.pop('encryption_key', None)
        session.pop('encrypted_files', None)
        session.pop('original_filenames', None)
    
    flash('Simulation cleared', 'info')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
