from wsgi import application as app  # Import 'application' and alias it as 'app'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)