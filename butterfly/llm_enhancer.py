import os
from typing import Optional

from llama_cpp import Llama


class LlmEnhancer:
    """Optional LLM fallback for ambiguous formatting or metadata extraction."""

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        if model_path and os.path.exists(model_path):
            try:
                # Offload all layers to GPU (n_gpu_layers=-1) for 16GB VRAM
                # n_ctx=4096 keeps memory usage well under the 16GB limit
                self.model = Llama(
                    model_path=model_path,
                    n_gpu_layers=-1,
                    n_ctx=4096,
                    verbose=False
                )
            except Exception as e:
                print(f"Warning: Failed to load LLM model: {e}")

    def is_available(self) -> bool:
        return self.model is not None

    def enhance_prose(self, text: str) -> str:
        """Uses LLM to clean up highly ambiguous prose (fallback)."""
        if not self.model:
            return text

        prompt = f"""You are an expert text formatter. Format the following text into clean Markdown. 
        Merge hard-wrapped lines into proper paragraphs. Preserve scene breaks as '---'. 
        Do not change the wording or meaning. Output ONLY the cleaned text.

        Text:
        {text[:3000]}"""  # Limit context to prevent OOM

        try:
            response = self.model(
                prompt,
                max_tokens=1000,
                temperature=0.1,  # Low temperature for deterministic formatting
                stop=["\n\n---\n\n"]  # Prevent it from generating beyond the text
            )
            return response['choices'][0]['text'].strip()
        except Exception:
            return text  # Graceful fallback
