import sys
from .app.__init__ import create_app

# Print the Python system path for debugging purposes.
print(sys.path)
# Create a Flask web server from the app factory
app = create_app('development')

# Only run the application when this file is called directly
if __name__ == '__main__':
    # Run the flask app on host 0.0.0.0 and port 5000 with debug mode on
    app.run(debug=True, host='0.0.0.0', port=5000)
