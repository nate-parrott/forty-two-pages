from app import app
from flaskext.sass import sass
sass(app, input_dir='sass', output_dir='css')
app.run(debug=True)
