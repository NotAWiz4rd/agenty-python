import argparse

import uvicorn

from group_work_log import app

parser = argparse.ArgumentParser(description="Group Work Log")
parser.add_argument("--port", type=int, default=8082, help="Port to run the server on")

if __name__ == "__main__":
    args = parser.parse_args()
    uvicorn.run(app, host="0.0.0.0", port=args.port)
