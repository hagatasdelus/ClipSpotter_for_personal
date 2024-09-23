import uvicorn

from clipspotter.app import create_app
from clipspotter.config import get_logger

logger = get_logger(__name__)
app = create_app()

if __name__ == "__main__":
    try:
        uvicorn.run("setup:app")
    except KeyboardInterrupt:
        print("Bot shutdown requested...exiting")
