"""
OpenAI Processing Service for GenAI Table Processing.
"""
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()


@dataclass
class ProcessingResult:
    """Result from processing a single item."""
    response: Dict[str, Any]
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str


@dataclass
class ProcessingStep:
    """Configuration for a single processing step."""
    prompt: str
    output_fields: List[str]
    model: str = "gpt-4o-mini"
    

class OpenAIProcessingService:
    """Service for processing data items using OpenAI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the processing service."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        self.client = OpenAI(api_key=self.api_key)
        
    def process_item(
        self, 
        prompt: str, 
        output_fields: List[str],
        model: str = "gpt-4o-mini"
    ) -> ProcessingResult:
        """
        Process a single item using OpenAI.
        
        Args:
            prompt: The formatted prompt with data already substituted
            output_fields: List of field names expected in the response
            model: OpenAI model to use
            
        Returns:
            ProcessingResult with response data and token usage
        """
        # Build system message for structured output
        system_message = """You are an AI assistant for data processing. 
You must respond with a valid JSON object containing the requested fields.
Do not include any text outside the JSON object."""

        # Build the output instruction
        fields_description = ", ".join([f'"{f}"' for f in output_fields])
        user_message = f"""{prompt}

Respond with a JSON object containing these fields: {fields_description}"""

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse the response
        content = response.choices[0].message.content
        try:
            parsed_response = json.loads(content)
        except json.JSONDecodeError:
            parsed_response = {"raw_response": content}
            
        return ProcessingResult(
            response=parsed_response,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            model=response.model
        )
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str = "gpt-4o-mini") -> float:
        """
        Estimate cost based on token usage.
        
        Pricing (as of Dec 2024, approximate):
        - gpt-4o-mini: $0.15/1M input, $0.60/1M output
        - gpt-4o: $2.50/1M input, $10.00/1M output
        """
        pricing = {
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4o": {"input": 0.0025, "output": 0.01},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        }
        
        # Default to gpt-4o-mini pricing if model not found
        model_pricing = pricing.get(model, pricing["gpt-4o-mini"])
        
        input_cost = (prompt_tokens / 1000) * model_pricing["input"]
        output_cost = (completion_tokens / 1000) * model_pricing["output"]
        
        return input_cost + output_cost
