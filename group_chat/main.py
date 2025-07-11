import argparse

import uvicorn

from group_chat import app

parser = argparse.ArgumentParser(description="Group Chat")
parser.add_argument("--port", type=int, default=5000, help="Port to run the server on")


def main():
    args = parser.parse_args()
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
