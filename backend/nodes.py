# Reference: nodes.py:54-100 - Node patterns
from abc import abstractmethod

class BaseNode:
    """Simplified base - ComfyUI uses ComfyNodeABC"""
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ()
    FUNCTION = "execute"
    CATEGORY = "basic"

    @abstractmethod
    def execute(self, **kwargs):
        pass

class TextNode(BaseNode):
    """Maps to your textInput React Flow node"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": ""})
            }
        }

    RETURN_TYPES = ("STRING",)

    def execute(self, text):
        return (text,)  # Always return tuple

class SimpleImageGen(BaseNode):
    """Maps to your modelSelector React Flow node"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING",),
                "model": ("STRING", {"default": "segmind/tiny-sd"})
            }
        }

    RETURN_TYPES = ("IMAGE",)

    def execute(self, prompt, model):
        # Use diffusers (simpler than ComfyUI's custom loading)
        from diffusers import StableDiffusionPipeline
        import torch

        print(f"Loading model: {model}")

        # Load model - use float32 for CPU compatibility
        pipe = StableDiffusionPipeline.from_pretrained(
            model,
            torch_dtype=torch.float32  # Use float32 for CPU
        )
        pipe = pipe.to("cpu")  # Force CPU for now

        print(f"Generating image with prompt: {prompt}")
        # Generate with fewer steps for faster CPU inference
        image = pipe(prompt, num_inference_steps=10).images[0]
        print("Image generated successfully")
        return (image,)

class OutputNode(BaseNode):
    """Maps to your output React Flow node"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",)
            }
        }

    RETURN_TYPES = ("STRING",)  # Return image path

    def execute(self, image):
        import os
        import uuid
        from pathlib import Path

        # Create output directory if it doesn't exist
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        # Generate unique filename
        filename = f"{uuid.uuid4()}.png"
        filepath = output_dir / filename

        # Save the PIL image
        image.save(filepath)
        print(f"Saved image to: {filepath}")

        # Return relative path that frontend can use
        return (str(filepath),)

# Export - keys must match React Flow node types
NODE_CLASS_MAPPINGS = {
    "textInput": TextNode,
    "modelSelector": SimpleImageGen,
    "output": OutputNode,
}