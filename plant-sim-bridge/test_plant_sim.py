import win32com.client
import os
import sys

# Clear any existing cache
import tempfile
import shutil
cache_dir = os.path.join(tempfile.gettempdir(), f"gen_py-{sys.version_info.major}.{sys.version_info.minor}")
if os.path.exists(cache_dir):
    print(f"Clearing cache at: {cache_dir}")
    shutil.rmtree(cache_dir, ignore_errors=True)

print("Testing Plant Simulation connection...")

try:
    # Use Dispatch instead of gencache.EnsureDispatch
    app = win32com.client.Dispatch("Tecnomatix.PlantSimulation.RemoteControl.25.4")
    print("✅ Connected successfully!")
    
    app.SetVisible(True)
    print("✅ Plant Simulation is visible")
    
    app.NewModel()
    print("✅ New model created")
    
    print("\n🎉 Everything works! Now fix your main files by changing gencache.EnsureDispatch to Dispatch")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPossible issues:")
    print("1. Plant Simulation 2504 not installed")
    print("2. License server not accessible")
    print("3. COM registration issues")
    
input("\nPress Enter to close...")