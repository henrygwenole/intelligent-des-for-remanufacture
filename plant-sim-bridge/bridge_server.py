from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from plant_simulation_controller import PlantSimulationController
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Plant Simulation Bridge for ASMG Framework", 
    version="2.1.0",
    description="Enhanced Windows COM Bridge for Plant Simulation 2504"
)

# Initialize Plant Simulation controller
plant_sim = PlantSimulationController()

class ExecutionRequest(BaseModel):
    simtalk_code: str
    parameters: Dict[str, Any]
    timestamp: Optional[str] = None

class JSONModelRequest(BaseModel):
    json_config: Dict[str, Any]
    operation: str = "build_model_from_json"

@app.on_event("startup")
async def startup_event():
    """Connect to Plant Simulation on startup"""
    logger.info("🚀 Starting Enhanced Plant Simulation Bridge for 2504...")
    
    if plant_sim.connect():
        logger.info("✅ Plant Simulation 2504 Bridge connected successfully")
    else:
        logger.warning("⚠️ Plant Simulation not available - bridge running in limited mode")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    plant_sim.disconnect()
    logger.info("👋 Plant Simulation Bridge shutdown complete")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Enhanced Plant Simulation Bridge for ASMG Framework",
        "version": "2.1.0",
        "plant_simulation_version": "2504",
        "plant_simulation_connected": plant_sim.connected,
        "capabilities": [
            "Advanced JSON model building",
            "3D object positioning",
            "Complex object relationships",
            "SimTalk code execution",
            "Simulation control",
            "Statistics collection"
        ],
        "endpoints": {
            "health": "/health",
            "execute": "/execute", 
            "execute_json": "/execute_json",
            "simulation/run": "/simulation/run",
            "simulation/reset": "/simulation/reset"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check for the bridge"""
    
    connection_details = {}
    performance_metrics = {}
    
    if plant_sim.connected:
        try:
            # Test Plant Simulation responsiveness
            test_start = datetime.now()
            plant_sim_responding = plant_sim.health_check()
            test_end = datetime.now()
            
            response_time = (test_end - test_start).total_seconds()
            
            connection_details = {
                "version": plant_sim.get_version_info(),
                "last_test_time": test_end.isoformat(),
                "response_time_seconds": round(response_time, 3)
            }
            
            performance_metrics = {
                "total_requests": plant_sim.request_count,
                "successful_requests": plant_sim.success_count,
                "failed_requests": plant_sim.error_count,
                "average_response_time": plant_sim.get_average_response_time()
            }
            
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            connection_details["error"] = str(e)
    
    return {
        "status": "healthy" if plant_sim.connected and plant_sim.health_check() else "degraded",
        "timestamp": datetime.now().isoformat(),
        "plant_simulation_connected": plant_sim.connected,
        "plant_simulation_responding": plant_sim.health_check() if plant_sim.connected else False,
        "connection_details": connection_details,
        "performance_metrics": performance_metrics
    }

@app.post("/execute")
async def execute_simulation(request: ExecutionRequest):
    """Execute SimTalk code in Plant Simulation with enhanced error handling"""
    
    if not plant_sim.connected:
        # Attempt to reconnect
        logger.info("Attempting to reconnect to Plant Simulation...")
        if not plant_sim.connect():
            raise HTTPException(
                status_code=503,
                detail="Plant Simulation not connected and reconnection failed"
            )
    
    try:
        logger.info(f"Executing SimTalk request with intent: {request.parameters.get('intent', 'unknown')}")
        
        # Handle different types of requests based on intent
        intent = request.parameters.get('intent', 'unknown')
        
        if intent == 'create_production_line':
            result = plant_sim.create_production_line(request.parameters.get('parameters', {}))
        elif intent == 'run_simulation':
            duration = request.parameters.get('parameters', {}).get('simulation_duration', 1000)
            result = plant_sim.run_simulation(duration)
        elif intent == 'analyze_system':
            result = plant_sim.analyze_current_system(request.parameters.get('parameters', {}))
        else:
            # Execute raw SimTalk code
            simtalk_result = plant_sim.execute_simtalk(request.simtalk_code)
            
            result = {
                "status": "success",
                "simtalk_result": simtalk_result,
                "message": "SimTalk code executed successfully",
                "execution_details": {
                    "code_executed": request.simtalk_code[:200] + "..." if len(request.simtalk_code) > 200 else request.simtalk_code,
                    "execution_time": datetime.now().isoformat(),
                    "intent": intent
                }
            }
        
        logger.info(f"Execution completed successfully: {result.get('status')}")
        return result
        
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

@app.post("/execute_json")
async def execute_json_model(request: JSONModelRequest):
    """Execute JSON model building using proven advanced approach"""
    
    if not plant_sim.connected:
        logger.info("Attempting to connect to Plant Simulation for JSON model building...")
        if not plant_sim.connect():
            raise HTTPException(
                status_code=503, 
                detail="Plant Simulation not connected and reconnection failed"
            )
    
    try:
        logger.info(f"Building model from JSON configuration with operation: {request.operation}")
        logger.info(f"JSON config contains: {len(request.json_config.get('sources', []))} sources, "
                   f"{len(request.json_config.get('stations', []))} stations, "
                   f"{len(request.json_config.get('buffers', []))} buffers, "
                   f"{len(request.json_config.get('connections', []))} connections")
        
        if request.operation == "build_model_from_json":
            result = plant_sim.build_model_from_json(request.json_config)
        else:
            result = {
                "status": "error", 
                "message": f"Unknown operation: {request.operation}",
                "supported_operations": ["build_model_from_json"]
            }
        
        logger.info(f"JSON model building completed: {result.get('status')}")
        return result
        
    except Exception as e:
        logger.error(f"JSON model building failed: {e}")
        raise HTTPException(status_code=500, detail=f"JSON execution failed: {str(e)}")

@app.post("/simulation/run")
async def run_simulation(duration: int = 1000):
    """Run simulation for specified duration"""
    
    if not plant_sim.connected:
        raise HTTPException(status_code=503, detail="Plant Simulation not connected")
    
    try:
        logger.info(f"Running simulation for {duration} time units...")
        result = plant_sim.run_simulation(duration)
        logger.info(f"Simulation run completed: {result.get('status')}")
        return result
        
    except Exception as e:
        logger.error(f"Simulation run failed: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation run failed: {str(e)}")

@app.post("/simulation/reset")
async def reset_simulation():
    """Reset simulation state and statistics"""
    
    if not plant_sim.connected:
        raise HTTPException(status_code=503, detail="Plant Simulation not connected")
    
    try:
        result = plant_sim.reset_simulation()
        logger.info("Simulation reset completed")
        
        return {
            "status": "success",
            "message": "Simulation reset completed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Simulation reset failed: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation reset failed: {str(e)}")

@app.get("/models")
async def list_available_models():
    """List available Plant Simulation models"""
    
    if not plant_sim.connected:
        raise HTTPException(status_code=503, detail="Plant Simulation not connected")
    
    try:
        models = plant_sim.list_models()
        return {
            "models": models,
            "count": len(models),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Model listing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")

@app.get("/statistics")
async def get_bridge_statistics():
    """Get bridge performance statistics"""
    
    return {
        "bridge_statistics": {
            "total_requests": plant_sim.request_count,
            "successful_requests": plant_sim.success_count,
            "failed_requests": plant_sim.error_count,
            "success_rate": round((plant_sim.success_count / max(plant_sim.request_count, 1)) * 100, 2),
            "average_response_time": plant_sim.get_average_response_time()
        },
        "connection_status": {
            "connected": plant_sim.connected,
            "plant_simulation_version": plant_sim.get_version_info()
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8002,
        log_level="info",
        access_log=True
    )