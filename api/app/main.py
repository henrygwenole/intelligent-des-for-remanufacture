from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import httpx
import os
import json
from typing import Dict, Any, Optional

# Initialize FastAPI
app = FastAPI(title="ASMG Framework API with Gemini 2.5 Pro - Enhanced")

# Configure Gemini (using your proven approach)
genai.configure(api_key="AIzaSyBW6SMuYHBj_iXvdrxFrAbNIN8JuMj3ZBQ")
model = genai.GenerativeModel("gemini-2.5-pro")

class SimulationRequest(BaseModel):
    user_request: str

class SimulationResponse(BaseModel):
    status: str
    message: str
    intent: str
    json_config: Dict[str, Any]
    simtalk_code: str
    execution_result: Optional[Dict[str, Any]] = None
    explanation: str

@app.get("/")
async def root():
    return {
        "message": "ASMG Framework API with Gemini 2.5 Pro - Enhanced",
        "version": "3.1.0",
        "status": "running",
        "ai_model": "gemini-2.5-pro",
        "plant_simulation": "2504",
        "features": [
            "Advanced JSON model generation",
            "3D object positioning", 
            "Complex object relationships",
            "Proven Plant Simulation integration"
        ]
    }

@app.get("/health")
async def health():
    # Test Gemini
    try:
        test_response = model.generate_content("Respond with: HEALTHY")
        gemini_status = "healthy" if "HEALTHY" in test_response.text else "degraded"
    except:
        gemini_status = "unhealthy"
    
    # Test Plant Sim Bridge
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://host.docker.internal:8002/health", timeout=3.0)
            bridge_status = "healthy" if response.status_code == 200 else "degraded"
    except:
        bridge_status = "unhealthy"
    
    return {
        "status": "healthy",
        "services": {
            "gemini_2_5_pro": gemini_status,
            "plant_sim_bridge": bridge_status
        },
        "plant_simulation": "2504"
    }

@app.post("/simulate", response_model=SimulationResponse)
async def simulate(request: SimulationRequest):
    try:
        # Generate JSON configuration using your proven schema
        json_schema_definition = """
        {
          "sources": [
            {"name": "SourceName", "interval": 10, "amount": 1}
          ],
          "drains": [
            {"name": "DrainName"}
          ],
          "stations": [
            {"name": "StationName", "processing_time": 15}
          ],
          "buffers": [
            {"name": "BufferName", "capacity": 100}
          ],
          "conveyors": [
            {"name": "ConveyorName", "length": 5}
          ],
          "connections": [
            {"from": "ObjectName1", "to": "ObjectName2"}
          ]
        }
        """

        system_prompt_content = (
            "You are a simulation engineer who writes structured JSON configurations for "
            "Plant Simulation 2504 models. Generate a JSON describing the number and type of "
            "machines, buffers, sources, drains, conveyors, and flow logic (connections between objects). "
            "The JSON must strictly adhere to the following schema. Only output the JSON object, nothing else.\n\n"
            f"SCHEMA:\n```json\n{json_schema_definition.strip()}\n```\n\n"
        )

        full_prompt = f"{system_prompt_content}User request: {request.user_request}"

        generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            response_mime_type="application/json"
        )

        # Generate JSON configuration
        config_response = model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        json_output = config_response.text.strip()
        if json_output.startswith("```json") and json_output.endswith("```"):
            json_output = json_output[7:-3].strip()
        
        json_config = json.loads(json_output)
        
        # Generate human-readable SimTalk summary
        simtalk_prompt = f"""Based on this Plant Simulation JSON configuration:
{json.dumps(json_config, indent=2)}

Generate a summary of the SimTalk operations that will be performed. 
Include object creation, positioning, and connections."""
        
        simtalk_response = model.generate_content(simtalk_prompt)
        simtalk_summary = simtalk_response.text.strip()
        
        # Execute via bridge (using your proven JSON approach)
        execution_result = None
        try:
            async with httpx.AsyncClient() as client:
                bridge_response = await client.post(
                    "http://host.docker.internal:8002/execute_json",
                    json={
                        "json_config": json_config,
                        "operation": "build_model_from_json"
                    },
                    timeout=60.0
                )
                
                if bridge_response.status_code == 200:
                    execution_result = bridge_response.json()
                else:
                    execution_result = {"status": "error", "message": "Bridge communication failed"}
        except:
            execution_result = {"status": "error", "message": "Could not connect to Plant Simulation bridge"}
        
        # Generate explanation
        explain_prompt = f"""Explain this Plant Simulation model in business terms:

User Request: {request.user_request}
Generated Model: {json.dumps(json_config, indent=2)}
Execution Result: {execution_result}

Provide clear insights about what was created and its business value."""
        
        explanation_response = model.generate_content(explain_prompt)
        explanation = explanation_response.text.strip()
        
        return SimulationResponse(
            status="success",
            message="Advanced model generated with Gemini 2.5 Pro and Plant Simulation 2504",
            intent="advanced_model_generation",
            json_config=json_config,
            simtalk_code=simtalk_summary,
            execution_result=execution_result,
            explanation=explanation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)