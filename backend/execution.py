# Reference: execution.py:614-737, comfy_execution/graph.py:22-240

# Core Concepts
# DynamicPrompt (graph.py:22-63) - Stores workflow nodes
# ExecutionList (graph.py:189-240) - Topological sort implementation
# PromptExecutor (execution.py:614-737) - Execution coordinator

from nodes import NODE_CLASS_MAPPINGS

class MinimalExecutor:
    """
    Simplified from execution.py:614-737 - PromptExecutor
    Removes: caching, validation, WebSocket updates
    """

    def __init__(self):
        self.outputs = {}
        self.nodes = NODE_CLASS_MAPPINGS

    async def execute(self, prompt, prompt_id):
        """
        Reference: execution.py:666-737 - execute_async()

        ComfyUI flow:
        1. Creates DynamicPrompt
        2. Creates ExecutionList (topological sort)
        3. Loops through staged nodes
        4. Calls execute() for each (line 404)
        5. Caches results

        Our simplified flow:
        1. Build dependency graph
        2. Topological sort
        3. Execute nodes in order
        4. Return outputs
        """
        self.outputs = {}

        # Build execution order
        execution_order = self.topological_sort(prompt)

        # Execute each node
        for node_id in execution_order:
            node_info = prompt[node_id]
            result = await self.execute_node(node_id, node_info, prompt)
            self.outputs[node_id] = result

        return self.outputs

    def topological_sort(self, prompt):
        """
        Reference: comfy_execution/graph.py:189-240 - ExecutionList

        ComfyUI uses complex ExecutionList with caching
        We use simple Kahn's algorithm
        """
        # Build graph and in-degrees
        graph = {node_id: [] for node_id in prompt.keys()}
        in_degree = {node_id: 0 for node_id in prompt.keys()}

        for node_id, node_info in prompt.items():
            inputs = node_info.get('inputs', {})
            for input_name, input_value in inputs.items():
                # Check if input is a link: [source_node_id, output_index]
                if isinstance(input_value, list) and len(input_value) == 2:
                    source_node = input_value[0]
                    if source_node in graph:
                        graph[source_node].append(node_id)
                        in_degree[node_id] += 1

        # Kahn's algorithm
        queue = [n for n in in_degree if in_degree[n] == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(prompt):
            raise Exception("Circular dependency detected")

        return result

    async def execute_node(self, node_id, node_info, prompt):
        """
        Reference: execution.py:404-550 - execute() function

        ComfyUI checks cache (line 412-421), handles async nodes,
        resolves inputs, calls node function
        """
        class_type = node_info['class_type']
        node_class = self.nodes[class_type]

        # Resolve inputs
        inputs = self.resolve_inputs(node_info, prompt)

        # Debug logging
        print(f"Executing node {node_id} ({class_type})")
        print(f"  Inputs received: {inputs}")

        # Execute
        instance = node_class()
        result = instance.execute(**inputs)

        # Result is tuple - store first element
        return result[0] if result else None

    def resolve_inputs(self, node_info, prompt):
        """
        Reference: execution.py:450-500 (input resolution logic)

        Combine:
        1. Direct values from node inputs
        2. Linked values from other nodes' outputs
        """
        inputs = {}
        node_inputs = node_info.get('inputs', {})

        print(f"  Raw node inputs: {node_inputs}")

        for input_name, input_value in node_inputs.items():
            # Check if it's a link: [source_node_id, output_index]
            if isinstance(input_value, list) and len(input_value) == 2:
                source_node_id = input_value[0]
                output_index = input_value[1]

                # Get output from executed node
                if source_node_id in self.outputs:
                    inputs[input_name] = self.outputs[source_node_id]
                    print(f"    Resolved link {input_name}: {source_node_id} -> {inputs[input_name]}")
                else:
                    print(f"    WARNING: Source node {source_node_id} not found in outputs for input {input_name}")
            else:
                # Direct value
                inputs[input_name] = input_value
                print(f"    Direct value {input_name}: {input_value}")

        return inputs