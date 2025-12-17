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
                "model": ("STRING", {"default": "stable-diffusion-v1-5"})
            }
        }

    RETURN_TYPES = ("IMAGE",)

    def execute(self, prompt, model):
        # Use diffusers (simpler than ComfyUI's custom loading)
        from diffusers import StableDiffusionPipeline
        import torch

        # Load model
        pipe = StableDiffusionPipeline.from_pretrained(
            model,
            torch_dtype=torch.float16
        )
        pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

        # Generate
        image = pipe(prompt, num_inference_steps=20).images[0]
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

    RETURN_TYPES = ()  # No outputs

    def execute(self, image):
        # Just pass through - server will serialize
        return (image,)

# Export - keys must match React Flow node types
NODE_CLASS_MAPPINGS = {
    "textInput": TextNode,
    "modelSelector": SimpleImageGen,
    "output": OutputNode,
}