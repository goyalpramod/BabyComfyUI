# Reference: server.py:183-770

from aiohttp import web
from aiohttp_cors import setup as cors_setup
import aiohttp_cors
from execution import MinimalExecutor

class MinimalComfyServer:
    def __init__(self):
        self.app = web.Application()
        self.executor = MinimalExecutor() 
        self.setup_routes()
        cors = cors_setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*"
            )
        })
        for route in list(self.app.router.routes()):
            cors.add(route)

    def setup_routes(self):
        """
        Reference: server.py:232-772
        ComfyUI uses @routes decorator pattern
        """
        routes = web.RouteTableDef()

        @routes.post('/prompt')
        async def post_prompt(request):
            """
            Reference: server.py:719-770 - POST /prompt handler

            Flow:
            1. Parse JSON
            2. Validate workflow (you can skip for minimal)
            3. Execute workflow
            4. Return results
            """
            json_data = await request.json()

            if "prompt" not in json_data:
                return web.json_response(
                    {"error": "No prompt provided"},
                    status=400
                )

            prompt = json_data["prompt"]
            prompt_id = "test-id"  # ComfyUI generates UUID

            # Execute (implement in Part 5)
            results = await self.executor.execute(prompt, prompt_id)

            return web.json_response({
                "prompt_id": prompt_id,
                "outputs": self.serialize_outputs(results)
            })

        @routes.get('/object_info')
        async def get_object_info(request):
            """
            Reference: server.py:671-682 - GET /object_info
            Returns node definitions for frontend
            """
            from nodes import NODE_CLASS_MAPPINGS

            node_info = {}
            for name, node_class in NODE_CLASS_MAPPINGS.items():
                node_info[name] = {
                    "input": node_class.INPUT_TYPES(),
                    "output": node_class.RETURN_TYPES,
                }

            return web.json_response(node_info)

        self.app.router.add_routes(routes)

    def serialize_outputs(self, results):
        """Convert outputs to JSON-serializable format"""
        serialized = {}
        for node_id, output in results.items():
            # Handle PIL Images - convert to base64
            if hasattr(output, 'save'):  # PIL Image
                import base64
                from io import BytesIO
                buffer = BytesIO()
                output.save(buffer, format='PNG')
                img_str = base64.b64encode(buffer.getvalue()).decode()
                serialized[node_id] = f"data:image/png;base64,{img_str}"
            else:
                serialized[node_id] = output

        return serialized

    def run(self):
        """Reference: main.py calls server startup"""
        web.run_app(self.app, host='127.0.0.1', port=8188)

if __name__ == '__main__':
    server = MinimalComfyServer()
    server.run()




