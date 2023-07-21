from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import glob

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure secret key
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROFILE_PICS_FOLDER'] = 'profile_pics'
app.config['SLIDES_FOLDER'] = 'static/slides'

# User data (replace this with data from a proper database)
users = {
    '1': {'password': '1'},
    '2': {'password': '2'}
}

# Add a list of slide URLs

class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.password = password

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User(user_id, users.get(user_id, {}).get('password'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Process the registration form data
        username = request.form['username']
        password = request.form['password']
        profile_picture = request.files['profile_picture']

        # Save the profile picture to the server if provided
        if profile_picture.filename:
            filename = f"{username}_profile.jpg"
            profile_picture.save(os.path.join(app.config['PROFILE_PICS_FOLDER'], filename))

        # Save the user information to the database (if using a database)
        # ...

        # Redirect the user to the profile settings page after registration
        return redirect(url_for('profile_settings'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user['password'] == password:
            user_obj = User(username, password)
            login_user(user_obj)
            return redirect(url_for('index'))
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/')
def home():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    slides = glob.glob(os.path.join(app.config['SLIDES_FOLDER'], '*.png'))  # Get all image files in the slides directory

    return render_template('home.html', files=files, slides=slides)

@app.route('/index.html')
@login_required
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files, username=current_user.id)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash("No file part", 'error')
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        flash("No selected file", 'error')
        return redirect(url_for('index'))
    # Save the uploaded file to the server
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    flash("File uploaded successfully!", 'success')
    return redirect(url_for('index'))

@app.route('/profile_settings')
@login_required
def profile_settings():
    # Get the user's profile picture filename from the database (if using a database)
    # For this example, let's assume the filename is stored in a variable called 'profile_picture_filename'
    profile_picture_filename = f"{current_user.id}_profile.jpg"  # Replace this with the actual filename

    return render_template('profile_settings.html', profile_picture=profile_picture_filename)

@app.route('/remove/<filename>', methods=['DELETE'])
@login_required  # Ensure only authenticated users can remove files
def remove_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return jsonify({'success': True, 'message': 'File removed successfully.'})
        except Exception as e:
            return jsonify({'success': False, 'message': 'Failed to remove the file.'})
    else:
        return jsonify({'success': False, 'message': 'File not found.'}), 404

@app.route('/download/<filename>')
@login_required
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['PROFILE_PICS_FOLDER']):
        os.makedirs(app.config['PROFILE_PICS_FOLDER'])
    app.run(host='0.0.0.0', port=5000, debug=True)