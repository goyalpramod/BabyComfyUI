from server import MinimalComfyServer
from execution import MinimalExecutor

if __name__ == '__main__':
    server = MinimalComfyServer()
    server.executor = MinimalExecutor()

    print("Starting ComfyUI minimal server on http://localhost:8188")
    server.run()