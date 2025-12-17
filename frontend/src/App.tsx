import { useCallback, useRef, useState } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  useReactFlow,
  ReactFlowProvider,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { TextInputNode, ModelSelectorNode, OutputNode } from './components/Nodes';

const nodeTypes = {
  textInput: TextInputNode,
  modelSelector: ModelSelectorNode,
  output: OutputNode,
};

const initialNodes = [
  {
    id: 'text-1',
    type: 'textInput',
    data: { text: '' },
    position: { x: 50, y: 150 },
  },
];

let id = 2;
const getId = () => `node-${id++}`;

function Flow() {
  const reactFlowWrapper = useRef(null);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const { screenToFlowPosition } = useReactFlow();
  const [menu, setMenu] = useState(null);
  const [pendingConnection, setPendingConnection] = useState(null);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [],
  );

  const onConnectEnd = useCallback(
    (event, connectionState) => {
      if (!connectionState.isValid) {
        const { clientX, clientY } =
          'changedTouches' in event ? event.changedTouches[0] : event;

        setMenu({
          x: clientX,
          y: clientY,
        });
        setPendingConnection(connectionState);
      }
    },
    [screenToFlowPosition],
  );

  const createNode = useCallback(
    (type) => {
      if (!menu || !pendingConnection) return;

      const newNodeId = getId();
      const position = screenToFlowPosition({
        x: menu.x,
        y: menu.y,
      });

      const newNode = {
        id: newNodeId,
        type,
        position,
        data: type === 'textInput'
          ? { text: '' }
          : type === 'modelSelector'
          ? { model: 'gpt-4' }
          : { imagePath: '' },
      };

      setNodes((nds) => nds.concat(newNode));
      setEdges((eds) =>
        eds.concat({
          id: `${pendingConnection.fromNode.id}-${newNodeId}`,
          source: pendingConnection.fromNode.id,
          target: newNodeId,
        }),
      );

      setMenu(null);
      setPendingConnection(null);
    },
    [menu, pendingConnection, screenToFlowPosition],
  );

  const closeMenu = useCallback(() => {
    setMenu(null);
    setPendingConnection(null);
  }, []);

  // 1. Serialize workflow to JSON
  const serializeWorkflow = () => ({
    prompt: Object.fromEntries(
      nodes.map(node => [
        node.id,
        {
          class_type: node.type,  // Must match backend NODE_CLASS_MAPPINGS
          inputs: extractInputs(node, edges)
        }
      ])
    )
  });

  // 2. Extract inputs helper
  const extractInputs = (node, edges) => {
    const inputs = {...node.data};  // Start with node's own data

    // Add connected inputs from edges
    edges.forEach(edge => {
      if (edge.target === node.id) {
        // Only add if targetHandle is defined (not undefined)
        if (edge.targetHandle) {
          // Format: [source_node_id, source_output_index]
          inputs[edge.targetHandle] = [edge.source, 0];
        }
      }
    });

    return inputs;
  };

  // 3. Update output nodes with results
  const updateOutputNodes = (result) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.type === 'output' && result[node.id]) {
          return {
            ...node,
            data: { ...node.data, imagePath: result[node.id] },
          };
        }
        return node;
      })
    );
  };

  // 4. Execute function
  const executeWorkflow = async () => {
    const workflow = serializeWorkflow();

    const response = await fetch('http://localhost:8188/prompt', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(workflow)
    });

    const result = await response.json();

    // Handle result (update output nodes)
    updateOutputNodes(result);
  };

  return (
    <div style={{ height: '100%', position: 'relative' }} ref={reactFlowWrapper}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onConnectEnd={onConnectEnd}
        fitView
        fitViewOptions={{ padding: 2 }}
      >
        <Background />
        <Controls />
      </ReactFlow>

      {menu && (
        <>
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: 999,
            }}
            onClick={closeMenu}
          />
          <div
            className="node-menu"
            style={{
              left: menu.x,
              top: menu.y,
            }}
          >
            <button onClick={() => createNode('textInput')}>Text Input</button>
            <button onClick={() => createNode('modelSelector')}>Model Selector</button>
            <button onClick={() => createNode('output')}>Output</button>
          </div>
        </>
      )}
      <div className="execute-button-container" style={{ position: 'absolute', top: 10, right: 10 }}>
        <button className="execute-button" onClick={executeWorkflow}>
          Execute Workflow
        </button>
      </div>
    </div>
  );
}

export default () => (
  <ReactFlowProvider>
    <Flow />
  </ReactFlowProvider>
);


// References
// https://reactflow.dev/examples/nodes/add-node-on-edge-drop
// https://reactflow.dev/examples/nodes/node-toolbar
// https://reactflow.dev/examples/nodes/node-resizer
// https://reactflow.dev/examples/nodes/proximity-connect
// https://reactflow.dev/examples/edges/custom-connectionline
// https://reactflow.dev/examples/edges/markers
// https://reactflow.dev/examples/interaction/computing-flows
// https://reactflow.dev/examples/interaction/context-menu
// https://reactflow.dev/examples/interaction/save-and-restore
// https://reactflow.dev/examples/grouping/sub-flows
// https://reactflow.dev/examples/layout/elkjs
// https://reactflow.dev/examples/styling/dark-mode
// https://reactflow.dev/examples/styling/tailwind