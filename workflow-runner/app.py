import uvicorn

from wfrun import WorkflowApi

if __name__ == "__main__":
    api = WorkflowApi()
    config = uvicorn.Config(app=api.app, host="0.0.0.0", port=8000, loop="uvloop")
    server = uvicorn.Server(config)
    try:
        server.run()
    except KeyboardInterrupt:
        print("Shutting down gracefully...")
        server.shutdown()
