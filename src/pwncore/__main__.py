import uvicorn


def run_dev():
    uvicorn.run("pwncore:app", host="127.0.0.1", port=8080, reload=True)


if __name__ == "__main__":
    run_dev()
