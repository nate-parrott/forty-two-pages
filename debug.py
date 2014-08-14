from app import app
from flaskext.sass import sass
sass(app, input_dir='sass', output_dir='css')
app.run(debug=True)
#app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
