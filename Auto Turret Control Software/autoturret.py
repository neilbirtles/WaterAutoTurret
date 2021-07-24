from autoturretwebapp import init_autoturret

app = init_autoturret()

if __name__ == '__main__':
        app.run(debug=True, use_reloader=False, host='0.0.0.0')