from website import create_app

app = create_app()


# only run if the file is run directly else do not run
if __name__ == '__main__': 
    app.run(debug=True)