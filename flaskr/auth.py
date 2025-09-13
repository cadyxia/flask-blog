import functools

from flask import ( Blueprint, flash, g, redirect, render_template, request, session, url_for )
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# checks if user is currently logged in
# to run before view function no matter which url is requested
@bp.before_app_request
def load_logged_in_user():
  user_id = session.get('user_id')
  if user_id is None:
    g.user = None
  else:
    g.user = get_db().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()

# registers a new username and password
@bp.route('/register', methods=('GET', 'POST'))
def register():
  if request.method == 'POST':
    # user submitted something
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None

    if not username:
      error = 'Username is required.'
    elif not password:
      error = 'Password is required.'
    
    if error is None:
      try:
        db.execute("INSERT INTO user (username, password) VALUES (?, ?)",
                   (username, generate_password_hash(password)),)
        db.commit()
      except db.IntegrityError:
        error = f"User {username} is already registered."
      else:
        # will redirect if successfully registered
        return redirect(url_for('auth.login'))
    flash(error)
  # user is getting the form
  return render_template('auth/register.html')

# logs into an existing user profile
@bp.route('/login', methods=('GET', 'POST'))
def login():
  if request.method == 'POST':
    # user submitted something
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None
    user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

    if user is None or (not check_password_hash(user['password'], password)):
      error = 'Incorrect username or password'
    
    if error is None:
      # set user id and redirect if correct credentials
      session.clear()
      session['user_id'] = user['id']
      return redirect(url_for('index'))
    
    flash(error)
  return render_template('auth/login.html')

# logs out a user from their account
@bp.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('index'))

# decorator to make sure only logged in users can access some features
# redirects to login page if user is not logged in
def login_required(view):
  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if g.user is None:
      return redirect(url_for('auth.login'))
    return view(**kwargs)
  return wrapped_view