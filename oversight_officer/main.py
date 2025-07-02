import argparse

import uvicorn

from oversight_officer import app

parser = argparse.ArgumentParser(description="Oversight Officer")
parser.add_argument("--port", type=int, default=8083, help="Port to run the server on")

if __name__ == "__main__":
    args = parser.parse_args()
    uvicorn.run(app, host="0.0.0.0", port=args.port)
