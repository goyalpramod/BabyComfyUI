import { useCallback } from 'react';
import { Handle, Position } from '@xyflow/react';

export function TextInputNode({ data, id }) {
  const onChange = useCallback((evt) => {
    // Update the data directly - ReactFlow will handle the state
    data.text = evt.target.value;
    console.log('Text Input:', evt.target.value);
  }, [data]);

  return (
    <div className="custom-node text-input-node">
      <div className="node-header">Text Input</div>
      <div className="node-content">
        <textarea
          value={data.text || ''}
          onChange={onChange}
          placeholder="Enter your text here..."
          className="nodrag"
          rows={4}
        />
      </div>
      <Handle type="source" position={Position.Right} id="text-output" />
    </div>
  );
}

export function ModelSelectorNode({ data, id }) {
  const models = [
    'gpt-4',
    'gpt-3.5-turbo',
    'claude-3-opus',
    'claude-3-sonnet',
    'dall-e-3',
    'stable-diffusion-xl',
    'midjourney-v6',
  ];

  const onChange = useCallback((evt) => {
    // Update the data directly - ReactFlow will handle the state
    data.model = evt.target.value;
    console.log('Selected Model:', evt.target.value);
  }, [data]);

  return (
    <div className="custom-node model-selector-node">
      <Handle type="target" position={Position.Left} id="prompt" />
      <div className="node-header">Model Selector</div>
      <div className="node-content">
        <select value={data.model || 'gpt-4'} onChange={onChange} className="nodrag">
          {models.map((model) => (
            <option key={model} value={model}>
              {model}
            </option>
          ))}
        </select>
      </div>
      <Handle type="source" position={Position.Right} id="image" />
    </div>
  );
}

export function OutputNode({ data, id }) {
  return (
    <div className="custom-node output-node">
      <Handle type="target" position={Position.Left} id="image" />
      <div className="node-header">Output</div>
      <div className="node-content">
        <div className="output-preview">
          {data.imagePath ? (
            <img src={data.imagePath} alt="Output" />
          ) : (
            <div className="output-placeholder">
              <span>No output yet</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}