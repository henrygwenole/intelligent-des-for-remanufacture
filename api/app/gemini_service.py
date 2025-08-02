import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from typing import Dict, Any, List, Optional, Union
import os
import json
import logging
import asyncio
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog
from dataclasses import dataclass

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

@dataclass
class GeminiConfig:
    """Configuration for Gemini 2.5 Pro"""
    api_key: str
    model_name: str = "gemini-2.5-pro"
    temperature: float = 0.2
    top_p: float = 0.9
    top_k: int = 40
    max_output_tokens: int = 8192
    candidate_count: int = 1

class GeminiLLMService:
    """Advanced Gemini 2.5 Pro Service for ASMG Framework"""
    
    def __init__(self):
        self.config = self._load_config()
        self._initialize_model()
        self.request_count = 0
        self.error_count = 0
        
        logger.info("gemini_service_initialized", 
                   model=self.config.model_name,
                   temperature=self.config.temperature)
    
    def _load_config(self) -> GeminiConfig:
        """Load configuration from environment"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        return GeminiConfig(
            api_key=api_key,
            model_name=os.getenv('GEMINI_MODEL', 'gemini-2.5-pro'),
            temperature=float(os.getenv('GEMINI_TEMPERATURE', '0.2')),
            top_p=float(os.getenv('GEMINI_TOP_P', '0.9')),
            top_k=int(os.getenv('GEMINI_TOP_K', '40')),
            max_output_tokens=int(os.getenv('MAX_OUTPUT_TOKENS', '8192'))
        )
    
    def _initialize_model(self):
        """Initialize Gemini 2.5 Pro with optimized settings"""
        # Configure Gemini API
        genai.configure(api_key=self.config.api_key)
        
        # Optimized generation configuration for Plant Simulation tasks
        self.generation_config = {
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "top_k": self.config.top_k,
            "max_output_tokens": self.config.max_output_tokens,
            "candidate_count": self.config.candidate_count,
            "response_mime_type": "text/plain"
        }
        
        # Enhanced safety settings for industrial applications
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.config.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
            system_instruction="""You are an expert AI assistant specialized in Siemens Plant Simulation and industrial manufacturing processes. You have deep knowledge of:

1. SimTalk programming language and syntax
2. Plant Simulation objects and their properties
3. Manufacturing systems design and optimization
4. Discrete event simulation principles
5. Industrial engineering best practices

Always provide accurate, executable code and practical insights for manufacturing applications."""
        )
        
        logger.info("gemini_model_initialized", 
                   model=self.config.model_name,
                   max_tokens=self.config.max_output_tokens)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_content_with_retry(self, prompt: str) -> str:
        """Generate content with retry logic for reliability"""
        try:
            self.request_count += 1
            
            # Use async generation for better performance
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            if not response.text:
                raise ValueError("Empty response from Gemini")
            
            logger.info("gemini_request_success", 
                       request_count=self.request_count,
                       response_length=len(response.text))
            
            return response.text.strip()
            
        except Exception as e:
            self.error_count += 1
            logger.error("gemini_request_failed", 
                        error=str(e),
                        error_count=self.error_count,
                        request_count=self.request_count)
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for Gemini service"""
        try:
            start_time = datetime.now()
            
            # Simple test query
            test_response = await self._generate_content_with_retry(
                "Respond with exactly: 'ASMG-Gemini-2.5-Ready'"
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            is_healthy = "ASMG-Gemini-2.5-Ready" in test_response
            
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "model": self.config.model_name,
                "response_time_seconds": round(response_time, 2),
                "request_count": self.request_count,
                "error_count": self.error_count,
                "error_rate": round(self.error_count / max(self.request_count, 1) * 100, 2),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model": self.config.model_name,
                "timestamp": datetime.now().isoformat()
            }
    
    async def extract_simulation_parameters(self, user_request: str, context: str = "") -> Dict[str, Any]:
        """Extract simulation parameters using Gemini 2.5 Pro's advanced reasoning"""
        
        prompt = f"""PLANT SIMULATION PARAMETER EXTRACTION

Context Information:
{context}

User Request: "{user_request}"

Analyze this request and extract simulation parameters. Use your expertise in manufacturing systems to infer appropriate values where not explicitly stated.

Respond with ONLY a valid JSON object:
{{
    "intent": "primary_action",
    "confidence": 0.95,
    "parameters": {{
        "stations": number_of_workstations,
        "processing_time": seconds_per_operation,
        "buffer_capacity": units_capacity,
        "simulation_duration": time_units,
        "arrival_rate": parts_per_minute,
        "setup_time": seconds_if_applicable,
        "failure_rate": probability_if_mentioned,
        "batch_size": units_if_applicable
    }},
    "components": ["SimulationObject1", "SimulationObject2"],
    "simtalk_approach": "detailed_implementation_strategy",
    "manufacturing_insights": "key_considerations_and_recommendations"
}}

Focus on manufacturing best practices and realistic parameter values."""
        
        try:
            response_text = await self._generate_content_with_retry(prompt)
            
            # Enhanced JSON parsing with fallback
            response_text = self._clean_json_response(response_text)
            result = json.loads(response_text)
            
            # Validate and enhance the response
            result = self._validate_and_enhance_parameters(result, user_request)
            
            logger.info("parameter_extraction_success", 
                       intent=result.get('intent'),
                       confidence=result.get('confidence', 0.0))
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error("json_parsing_failed", error=str(e), raw_response=response_text[:200])
            return self._create_fallback_parameters(user_request, str(e))
        except Exception as e:
            logger.error("parameter_extraction_failed", error=str(e))
            return self._create_fallback_parameters(user_request, str(e))
    
    async def generate_simtalk_code(self, intent: str, parameters: Dict[str, Any], examples: List[str]) -> str:
        """Generate optimized SimTalk code using Gemini 2.5 Pro"""
        
        examples_text = "\n\n".join([f"Reference Example {i+1}:\n{ex}" for i, ex in enumerate(examples[:3])])
        
        prompt = f"""SIMTALK CODE GENERATION FOR PLANT SIMULATION

Task: Generate production-ready SimTalk code

Intent: {intent}
Parameters: {json.dumps(parameters, indent=2)}

Reference Examples:
{examples_text}

Generate complete, executable SimTalk code following these requirements:

1. SYNTAX: Use proper SimTalk syntax and conventions
2. STRUCTURE: Create objects, set properties, establish connections
3. COMMENTS: Include clear comments explaining each section
4. ERROR HANDLING: Add basic error checking where appropriate
5. OPTIMIZATION: Use efficient coding patterns
6. REALISM: Apply realistic manufacturing parameters

Code Structure:
- Object creation and initialization
- Parameter configuration
- Connection establishment
- Optional: Basic statistics collection

Generate ONLY the SimTalk code with comments, no markdown or explanations."""
        
        try:
            response = await self._generate_content_with_retry(prompt)
            
            # Clean and validate the code
            code = self._clean_simtalk_code(response)
            
            logger.info("simtalk_generation_success", 
                       intent=intent,
                       code_length=len(code))
            
            return code
            
        except Exception as e:
            logger.error("simtalk_generation_failed", error=str(e))
            return self._generate_fallback_simtalk_code(intent, parameters)
    
    async def explain_simulation_results(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive analysis of simulation results"""
        
        prompt = f"""SIMULATION RESULTS ANALYSIS

Results Data:
{json.dumps(results, indent=2)}

Provide a comprehensive business-focused analysis covering:

1. PERFORMANCE SUMMARY: Key metrics and outcomes
2. BOTTLENECK ANALYSIS: Identify constraints and limitations
3. EFFICIENCY ASSESSMENT: Utilization rates and throughput
4. RECOMMENDATIONS: Specific improvement suggestions
5. BUSINESS IMPACT: Operational and financial implications

Structure your response for both technical and management audiences. Be specific and actionable."""
        
        try:
            response = await self._generate_content_with_retry(prompt)
            
            logger.info("results_explanation_success", 
                       response_length=len(response))
            
            return response
            
        except Exception as e:
            logger.error("results_explanation_failed", error=str(e))
            return f"Analysis unavailable due to error: {e}"
    
    async def optimize_manufacturing_system(self, system_description: str, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """Advanced manufacturing system optimization using Gemini 2.5 Pro"""
        
        constraints_text = json.dumps(constraints or {}, indent=2)
        
        prompt = f"""MANUFACTURING SYSTEM OPTIMIZATION

System Description:
{system_description}

Constraints:
{constraints_text}

Perform a comprehensive optimization analysis and provide:

1. Current system analysis
2. Bottleneck identification
3. Optimization opportunities
4. Implementation recommendations
5. Expected improvements

Respond with a JSON object containing your analysis and recommendations."""
        
        try:
            response = await self._generate_content_with_retry(prompt)
            response_text = self._clean_json_response(response)
            result = json.loads(response_text)
            
            logger.info("optimization_analysis_success")
            return result
            
        except Exception as e:
            logger.error("optimization_analysis_failed", error=str(e))
            return {"error": str(e), "status": "failed"}
    
    # Helper methods
    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response from potential markdown formatting"""
        response = response.strip()
        if response.startswith("```json"):
            response = response.replace("```json", "").replace("```", "").strip()
        elif response.startswith("```"):
            lines = response.split('\n')
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            response = '\n'.join(lines)
        return response
    
    def _clean_simtalk_code(self, code: str) -> str:
        """Clean and validate SimTalk code"""
        code = code.strip()
        if code.startswith("```"):
            lines = code.split('\n')
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            code = '\n'.join(lines)
        return code
    
    def _validate_and_enhance_parameters(self, result: Dict[str, Any], user_request: str) -> Dict[str, Any]:
        """Validate and enhance extracted parameters"""
        # Ensure required fields exist
        required_fields = ["intent", "parameters", "components", "simtalk_approach"]
        for field in required_fields:
            if field not in result:
                result[field] = self._get_default_value(field)
        
        # Add confidence if missing
        if "confidence" not in result:
            result["confidence"] = 0.8
        
        # Add timestamp
        result["extracted_at"] = datetime.now().isoformat()
        result["original_request"] = user_request
        
        return result
    
    def _get_default_value(self, field: str):
        """Get default values for missing fields"""
        defaults = {
            "intent": "unknown",
            "parameters": {},
            "components": [],
            "simtalk_approach": "Manual implementation required"
        }
        return defaults.get(field, "")
    
    def _create_fallback_parameters(self, user_request: str, error: str) -> Dict[str, Any]:
        """Create fallback parameters when extraction fails"""
        return {
            "intent": "manual_review_required",
            "confidence": 0.1,
            "error": error,
            "parameters": {
                "stations": 1,
                "processing_time": 10,
                "buffer_capacity": 50
            },
            "components": ["Source", "SingleProc", "Drain"],
            "simtalk_approach": "Manual intervention required due to parsing error",
            "original_request": user_request,
            "extracted_at": datetime.now().isoformat()
        }
    
    def _generate_fallback_simtalk_code(self, intent: str, parameters: Dict[str, Any]) -> str:
        """Generate basic fallback SimTalk code"""
        return f"""-- Fallback SimTalk Code
-- Intent: {intent}
-- Generated due to error in AI code generation

-- Basic production line template
.Source := new Source
.Processor := new SingleProc
.Drain := new Drain

-- Basic configuration
.Processor.procTime := {parameters.get('processing_time', 10)}
.Source.creationTimes := [5]

-- Basic connections
.Source.successor := .Processor
.Processor.successor := .Drain

-- Note: Manual review and enhancement required"""

# Backward compatibility
LLMService = GeminiLLMService