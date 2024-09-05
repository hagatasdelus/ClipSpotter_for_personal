import uvicorn
from myapp.app import create_app

app = create_app()

if __name__ == "__main__":
    try:
        uvicorn.run("setup:app")
    except KeyboardInterrupt:
        print("Bot shutdown requested...exiting")
