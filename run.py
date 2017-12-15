from threading import Thread

from controller import app
from update import update


def thread_web():
    app.run()

def thread_updater():
    update()

def run():
    th_web = Thread(target=thread_web)
    th_update = Thread(target=thread_updater)

    th_web.start()
    th_update.start()

    th_web.join()
    th_update.join()

if __name__ == '__main__':
    run()
