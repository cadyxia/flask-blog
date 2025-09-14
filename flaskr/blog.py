from flask import ( Blueprint, flash, g, redirect, render_template, request, url_for )
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
  db = get_db()
  posts = db.execute('SELECT p.id, title, body, created, author_id, username'
                     ' FROM post p JOIN user u ON p.author_id = u.id'
                     ' ORDER BY created DESC').fetchall()
  return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
  if request.method == 'POST':
    title = request.form['title']
    body = request.form['body']
    error = None

    if not title:
      error = 'Title is required'
    
    if error is None:
      db = get_db()
      db.execute('INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)',
                 (title, body, g.user['id']))
      db.commit()
      return redirect(url_for('blog.index'))
    else:
      flash(error)
  return render_template('blog/create.html')

def get_post(id, check_author=True):
  post = get_db().execute('SELECT p.id, title, body, created, author_id, username'
                          ' FROM post p JOIN user u ON p.author_id = u.id'
                          ' WHERE p.id = ?', (id,)).fetchone()
  if post is None:
    abort(404, f"Post id {id} doesn't exist.")
  if check_author and post['author_id'] != g.user['id']:
    abort(403)
  return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
  post = get_post(id)
  if request.method == 'POST':
    title = request.form['title']
    body = request.form['body']
    error = None

    if not title:
      error = 'Title is required.'
    if error is None:
      db = get_db()
      db.execute('UPDATE post SET title = ?, body = ? WHERE id = ?',
                 (title, body, id))
      db.commit()
      return redirect(url_for('blog.index'))
    else:
      flash(error)
  return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
  # get_post(id)
  db = get_db()
  db.execute('DELETE FROM post WHERE id = ?', (id,))
  db.commit()
  return redirect(url_for('blog.index'))

@bp.route('/search', methods=('POST',))
def search():
  query = request.form['query']
  db = get_db()
  posts = db.execute("SELECT p.id, title, body, created, author_id, username "
                     "FROM post p JOIN user u ON p.author_id = u.id "
                     "WHERE body LIKE '%'||?||'%'  ORDER BY created DESC",
                     (query,)).fetchall()
  g.query = query
  return render_template('blog/index.html', posts=posts)

def get_comments(id):
  comments = get_db().execute('SELECT body, created, username'
                     ' FROM comments c JOIN user u ON c.author_id = u.id'
                     ' WHERE post_id = ? ORDER BY created DESC',
                     (id,)).fetchall()
  # comments = get_db().execute('SELECT author_id, body, created'
  #                         ' FROM comments WHERE post_id = ?', (id,)).fetchall()
  return comments

@bp.route('/<int:id>/detailed-post', methods=('GET',))
def detailed_post(id):
  post = get_post(id, False)
  comments = get_comments(id)
  return render_template('blog/detailed-post.html', post=post, comments=comments)

@bp.route('/comment', methods=('POST',))
@login_required
def comment():
  post_id = request.form['post_id']
  author_id = request.form['author_id']
  body = request.form['body']
  
  db = get_db()
  db.execute('INSERT INTO comments (post_id, author_id, body) VALUES (?, ?, ?)',
             (post_id, author_id, body))
  db.commit()
  comments=get_comments(post_id)
  flash("Comment posted!")
  return redirect(url_for('blog.detailed_post', id=post_id, comments=comments))