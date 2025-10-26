import threading
import uvicorn


def run_dev():
    def run_main():
        uvicorn.run("pwncore:app", host="127.0.0.1", port=8080, reload=True)

    def run_admin():
        uvicorn.run("pwncore.admin_app:admin_app", host="127.0.0.1", port=8081, reload=False)

    t1 = threading.Thread(target=run_main, daemon=True)
    t2 = threading.Thread(target=run_admin, daemon=True)

    t1.start()
    t2.start()

    t1.join()
    t2.join()


if __name__ == "__main__":
    run_dev()
