if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=6969, reload=True, host="192.168.29.53")
    # uvicorn.run("main:app", port=80)
