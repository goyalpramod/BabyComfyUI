import { useCallback, useState } from 'react';
import { Handle, Position } from '@xyflow/react';

export function TextInputNode({ data }) {
  const [text, setText] = useState(data?.text || '');

  const onChange = useCallback((evt) => {
    setText(evt.target.value);
    console.log('Text Input:', evt.target.value);
  }, []);

  return (
    <div className="custom-node text-input-node">
      <div className="node-header">Text Input</div>
      <div className="node-content">
        <textarea
          value={text}
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

export function ModelSelectorNode({ data }) {
  const [selectedModel, setSelectedModel] = useState(data?.model || 'gpt-4');

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
    setSelectedModel(evt.target.value);
    console.log('Selected Model:', evt.target.value);
  }, []);

  return (
    <div className="custom-node model-selector-node">
      <Handle type="target" position={Position.Left} id="model-input" />
      <div className="node-header">Model Selector</div>
      <div className="node-content">
        <select value={selectedModel} onChange={onChange} className="nodrag">
          {models.map((model) => (
            <option key={model} value={model}>
              {model}
            </option>
          ))}
        </select>
      </div>
      <Handle type="source" position={Position.Right} id="model-output" />
    </div>
  );
}

export function OutputNode({ data }) {
  const [imagePath, setImagePath] = useState(data?.imagePath || '');

  return (
    <div className="custom-node output-node">
      <Handle type="target" position={Position.Left} id="output-input" />
      <div className="node-header">Output</div>
      <div className="node-content">
        <div className="output-preview">
          {imagePath ? (
            <img src={imagePath} alt="Output" />
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