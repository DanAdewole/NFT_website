import uuid
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from werkzeug.utils import secure_filename
from .models import Users, NFTItem, Notifications, Collection, Activity
from VisualNft import app, db
from PIL import Image


# Function to get Ether to USD exchange rate
def get_eth_to_usd_price():
    response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd')
    data = response.json()
    return data.get('ethereum', {}).get('usd', 0)

# Function to calculate the equivalent in USD
def get_price_in_usd(eth_price):
    eth_to_usd = get_eth_to_usd_price()
    price_in_usd = eth_price * eth_to_usd
    return f"${price_in_usd:.2f}"

def get_user_notifications(user_id):
        user_notifications = Notifications.query.filter_by(user_id=user_id).all()
        return user_notifications

def upload_proof_of_funds(user_id):
    activity = Activity(user_id=user_id, activity_type='Upload Proof of Funds')
    db.session.add(activity)
    db.session.commit()


def send_notification(users, message):
    notification = Notifications(user_id=users.id, message=message)
    db.session.add(notification)
    db.session.commit()


@app.route('/')
@app.route('/home')
def index():

    return render_template('index.html')
  
    
@app.route('/explore')
def explore():
    return render_template('explore.html')

@app.route('/explore_music')
def explore_music():
    return render_template('explore_music.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Users.query.filter_by(email=email).first()

        if user and user.password == password:
            login_user(user)  # Use login_user to initiate the user session
            return redirect(url_for('user_dashboard'))  # Redirect to user's dashboard

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('FirstName')
        last_name = request.form.get('LastName')
        email = request.form.get('email')
        username = request.form.get('Username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if the passwords match
        if password != confirm_password:
            return "Passwords do not match"

        # Check if the provided email is already registered
        existing_user_email = Users.query.filter_by(email=email).first()
        existing_username = Users.query.filter_by(username=username).first()
        if existing_user_email:
            return "Email already registered"
        elif existing_username:
            return "Username already taken"

        # Create a new user and add to the database
        new_user = Users(firstname=first_name, lastname=last_name, email=email, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

       
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/like_item/<int:item_id>', methods=['POST'])
@login_required
def like_item(item_id):
    nft_item = NFTItem.query.get_or_404(item_id)
    
    if nft_item.author != current_user:  # Prevent the author from liking their own item
        nft_item.likes += 1
        db.session.commit()
    
    return "Liked", 200

@app.route('/view_item/<int:item_id>', methods=['POST'])
def view_item(item_id):
    nft_item = NFTItem.query.get_or_404(item_id)
    
    nft_item.views += 1
    db.session.commit()
    
    return "Viewed", 200


@login_required
@app.route('/profile_update', methods=['GET', 'POST'])
def profile_update():
    user_notifications = get_user_notifications(current_user.id)  # Replace with your logic to get user notifications
    notification_count = len(user_notifications)

    if request.method == 'POST':
        user = current_user
        user.username = request.form.get('username')
        user.bio = request.form.get('bio')
        user.email = request.form.get('email_address')
        user.your_site = request.form.get('your_site')
        user.twitter_username = request.form.get('twitter_username')
        user.instagram_username = request.form.get('instagram_username')

        if 'upload_profile_img' in request.files:
            profile_picture = request.files['upload_profile_img']
            if profile_picture.filename:
                pic_filename = secure_filename(profile_picture.filename)
                pic_name = str(uuid.uuid1()) + "_" + pic_filename
                pic_path = os.path.join(app.config['UPLOAD_FOLDER'], pic_name)
                os.makedirs(os.path.dirname(pic_path), exist_ok=True)
                # Delete the prior image if it exists
                if user.profile_picture:
                    prior_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture)
                    if os.path.exists(prior_pic_path):
                        os.remove(prior_pic_path)
                
                # Resize the image to a square
                img = Image.open(profile_picture)
                width, height = img.size
                min_dimension = min(width, height)
                img = img.resize((min_dimension, min_dimension))
                
                img.save(pic_path)
                user.profile_picture = pic_name
                    

        try:
            db.session.commit()
            flash("User Updated Successfully!", 'success')
            return redirect(url_for('user_dashboard'))
        except:
            db.session.rollback()
            flash("Error! There was a problem...try again!", 'danger')

    return render_template('profile_update.html', notification_count=notification_count)

        
                            
    
@app.route('/user_dashboard')
@login_required
def user_dashboard():
    return render_template('user_dashboard.html', nft_item=current_user.nfts, user=current_user)

@app.route('/item_details/<int:id>')
@login_required
def item_details(id):
    nft_item = NFTItem.query.get(id)
    if nft_item:
        user = Users.query.get(nft_item.author_id)
        return render_template('item_details.html', nft_item=nft_item, user=user, get_price_in_usd=get_price_in_usd)
    else:
        flash('NFT item not found.', 'danger')
        return redirect(url_for('some_other_route'))  # Redirect to a suitable route if item is not found


@app.route('/create-options')
@login_required
def create_options():
    return render_template('create_options.html')

@app.route('/create-single', methods=['GET', 'POST'])
@login_required
def create_single():
    if request.method == 'POST':
        uploaded_file = request.files['upload_file']
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            file_extension = os.path.splitext(filename)[1].lower()  # Get the file extension
            media_name = str(uuid.uuid1()) + "_" + filename
            media_path = os.path.join(app.config['UPLOAD_FOLDER'], media_name)
            os.makedirs(os.path.dirname(media_path), exist_ok=True)
            uploaded_file.save(media_path)

        item_price = request.form.get('item_price')
        item_collection = request.form.get('item_collection')
        item_title = request.form.get('item_title')
        item_desc = request.form.get('item_desc')

        # Check user's account balance
        user_balance = current_user.account_funds
    
        required_balance_eth = 0.12

        if user_balance < required_balance_eth:
            flash('Insufficient funds in your account.', 'error')
            return redirect(url_for('add_funds'))

        new_item = NFTItem(
            media=media_name,  # Store the media filename in the database
            media_extension=file_extension,  # Store the media file extension in the database
            name=item_title,
            price=item_price,
            description=item_desc,
            author_id=current_user.id,
            collection_id=item_collection
        )
        db.session.add(new_item)
        db.session.commit()

        flash('Item created successfully!', 'success')
        return redirect(url_for('create_single'))

    return render_template('create_single.html')


@app.route('/create-multiple', methods=['GET', 'POST'])
@login_required
def create_multiple():
    if request.method == 'POST':
        # Handle form submission and file uploads here
        uploaded_files = request.files.getlist('upload_files')
        uploaded_filenames = []

        for uploaded_file in uploaded_files:
            if uploaded_file:
                # Save the uploaded file
                filename = secure_filename(uploaded_file.filename)
                uploaded_file.save('path_to_upload_folder/' + filename)
                uploaded_filenames.append(filename)

        # Process other form data here
        item_price = request.form.get('item_price')
        item_unlock = request.form.get('item_unlock')
        item_collection = request.form.get('item_collection')
        item_title = request.form.get('item_title')
        item_desc = request.form.get('item_desc')

        # Create new items in the database
        for filename in uploaded_filenames:
            new_item = NFTItem(
                image='path_to_upload_folder/' + filename,
                name=item_title,
                item_price=item_price,
                description=item_desc,
                author_id=current_user.id,  # Assuming the current user is the author
                collection=item_collection  # Replace with the actual collection ID
            )
            db.session.add(new_item)

        db.session.commit()

        flash('Items created successfully!', 'success')
        return redirect(url_for('create_multiple'))

    return render_template('create_multiple.html')

@app.route('/manage_funds')
@login_required
def manage_funds():
    return render_template('manage_funds.html')

@app.route('/add_funds')
@login_required
def add_funds():
    return render_template('add_funds.html')

@app.route('/withdrawal')
@login_required
def withdrawal():
    return render_template('withdrawal.html')


@app.route('/contact')
def contact():
    return render_template('contact.html', user=current_user)

@app.route('/author')
def author():
    nft_item = NFTItem.query.get(id)
    if nft_item:
        user = Users.query.get(nft_item.author_id)
        return render_template('author.html', nft_item=nft_item, user=user)
    else:
        flash('NFT item not found.', 'danger')
        return redirect(url_for('some_other_route')) 
    

#admin routes
@app.route('/admin')
def admin_index():
    return render_template('admin/admin_index.html')

@app.route('/user_management')
def user_management():
    users = Users.query.all()
    return render_template('admin/user_management.html', users=users)

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = Users.query.get_or_404(id)

    if request.method == 'POST':
        # Update user information based on form submission
        user.username = request.form['username']
        user.firstname = request.form['firstname']
        user.lastname = request.form['lastname']
        user.email = request.form['email']
        user.bio = request.form['bio']
        user.password =request.form['password']
        # ... update other fields as needed
        db.session.commit()
        flash('User information updated successfully', 'success')
        return redirect(url_for('user_management'))  # Redirect to user management page

    return render_template('admin/edit_user.html', user=user)


@app.route('/delete_user/<int:id>', methods=['GET', 'POST'])
def delete_user(id):
    user = Users.query.get_or_404(id)

    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.firstname} {user.lastname} has been deleted', 'success')
        return redirect(url_for('user_management'))  # Redirect to user management page

    return render_template('admin/delete_user.html', user=user)

@app.route('/fund_user')
def fund_user():
    users = Users.query.all()
    return render_template('admin/fund_user.html', users=users)

@app.route('/fund_amount/<int:id>', methods=['GET', 'POST'])
def fund_amount(id):
    user = Users.query.get_or_404(id)
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        user.account_funds += amount
        db.session.commit()
        flash(f'Funded {amount} ETH to {user.username}', 'success')
        return redirect(url_for('fund_user'))
    return render_template('admin/fund_amount.html', user=user)

@app.route('/activity')
def activity():
    users = Users.query.all()
    return render_template('admin/activity.html', users=users)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))