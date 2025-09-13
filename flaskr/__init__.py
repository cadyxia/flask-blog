# for making directory
import os

from flask import Flask

# application factory function to create + configure app
def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)
  # TODO: change SECRET_KEY to random value when deploying
  app.config.from_mapping(SECRET_KEY='dev', DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),)

  if test_config is None:
    # load instance config
    app.config.from_pyfile('config.py', silent=True)
  else:
    # load custom config (for testing)
    app.config.from_mapping(test_config)
  
  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass

  # simple page saying hello
  @app.route('/hello')
  def hello():
    return 'Hello, World!'
  
  from . import db
  db.init_app(app)

  from . import auth
  app.register_blueprint(auth.bp)

  from . import blog
  app.register_blueprint(blog.bp)
  app.add_url_rule('/', endpoint='index')
  
  return app