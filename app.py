from backend.routes import app, publish, make_account, submit_appeal, login, get_stories



if __name__ == "__main__":
    app.run(port=3000, debug=True)