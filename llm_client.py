from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from typing import List, Dict, Any, Optional
import logging
from config import settings

logger = logging.getLogger(__name__)


class GPTOSSClient:
    def __init__(self):
        self.model_name = settings.model_name
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._load_model()
    
    def _load_model(self):
        """Load the GPT-OSS-20B model and tokenizer"""
        try:
            if settings.model_path:
                # Load from local path
                self.tokenizer = AutoTokenizer.from_pretrained(settings.model_path)
                self.model = AutoModelForCausalLM.from_pretrained(
                    settings.model_path,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None
                )
            else:
                # Load from Hugging Face Hub or API
                logger.warning("Model path not specified. Using placeholder for GPT-OSS-20B")
                # This would be the actual model identifier when available
                model_id = "microsoft/DialoGPT-medium"  # Placeholder
                self.tokenizer = AutoTokenizer.from_pretrained(model_id)
                self.model = AutoModelForCausalLM.from_pretrained(model_id)
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            logger.info(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def generate_code(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Generate Java code based on prompt and context"""
        try:
            # Prepare the full prompt with context
            full_prompt = self._prepare_prompt(prompt, context)
            
            # Tokenize input
            inputs = self.tokenizer.encode(
                full_prompt,
                return_tensors="pt",
                max_length=settings.max_context_length,
                truncation=True
            ).to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + settings.max_tokens,
                    temperature=settings.temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    num_return_sequences=1
                )
            
            # Decode response
            generated_text = self.tokenizer.decode(
                outputs[0][inputs.shape[1]:],
                skip_special_tokens=True
            )
            
            return self._extract_code(generated_text)
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return ""
    
    def _prepare_prompt(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Prepare the prompt with context information"""
        context_info = ""
        if context:
            if "related_classes" in context:
                context_info += "Related classes:\n"
                for cls in context["related_classes"]:
                    context_info += f"- {cls['name']} in {cls['package']}\n"
            
            if "methods" in context:
                context_info += "\nExisting methods:\n"
                for method in context["methods"]:
                    context_info += f"- {method['method_name']}({method.get('parameters', '')})\n"
        
        full_prompt = f"""You are a Java development assistant. Generate high-quality Java code based on the following requirements.

Context Information:
{context_info}

Task: {prompt}

Generated Java Code:
```java
"""
        return full_prompt
    
    def _extract_code(self, generated_text: str) -> str:
        """Extract clean Java code from generated response"""
        # Remove any markdown formatting
        code = generated_text.strip()
        
        # Remove ```java and ``` markers if present
        if code.startswith("```java"):
            code = code[7:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        
        return code.strip()
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze Java code and provide insights"""
        prompt = f"""Analyze the following Java code and provide insights about:
1. Code quality and potential improvements
2. Design patterns used
3. Potential bugs or issues
4. Suggestions for refactoring

Java Code:
```java
{code}
```

Analysis:"""
        
        try:
            inputs = self.tokenizer.encode(
                prompt,
                return_tensors="pt",
                max_length=settings.max_context_length,
                truncation=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 512,
                    temperature=0.3,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            analysis = self.tokenizer.decode(
                outputs[0][inputs.shape[1]:],
                skip_special_tokens=True
            )
            
            return {"analysis": analysis.strip()}
            
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return {"analysis": "Error occurred during code analysis"}
    
    def suggest_improvements(self, code: str, context: Dict = None) -> List[str]:
        """Suggest improvements for the given code"""
        analysis_result = self.analyze_code(code)
        
        # Extract suggestions from analysis
        suggestions = []
        analysis_text = analysis_result.get("analysis", "")
        
        # Simple extraction logic - in practice, you'd want more sophisticated parsing
        lines = analysis_text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['suggest', 'improve', 'should', 'consider', 'recommend']):
                suggestions.append(line.strip())
        
        return suggestions[:5]  # Return top 5 suggestions


# Global LLM client instance
llm_client = GPTOSSClient()