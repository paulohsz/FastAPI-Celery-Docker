#!/usr/bin/env python3
"""
Debug helper script for FastAPI application.
Run this inside the container to start FastAPI with debugger attached.
"""

import debugpy
import uvicorn
import os
import multiprocessing

# Only setup debugpy in the main process (not reloader children)
if multiprocessing.current_process().name == 'MainProcess':
    # Configure debugpy
    debugpy.configure(python="/usr/local/bin/python")

    # Start the debug server
    print("🐛 Starting debug server on port 5678...")
    try:
        debugpy.listen(("0.0.0.0", 5678))
        
        # Check if we should wait for debugger (default: yes)
        wait_for_debugger = os.getenv("WAIT_FOR_DEBUGGER", "true").lower() == "true"

        if wait_for_debugger:
            print("⏳ Waiting for debugger to attach...")
            print("   In VS Code:")
            print("   1. Set breakpoints in your code")
            print("   2. Go to Run & Debug (Ctrl+Shift+D)")
            print("   3. Select 'FastAPI Debug (Remote Attach)'")
            print("   4. Press F5 or click the green play button")
            debugpy.wait_for_client()
            print("✅ Debugger attached! Starting FastAPI...")
        else:
            print("🚀 Starting FastAPI without waiting for debugger...")
            print("   Debug server is available on port 5678 if you want to attach later")
    except RuntimeError as e:
        if "Address already in use" in str(e):
            print("⚠️  Debug port 5678 already in use, continuing without debugger...")
        else:
            raise

# Start FastAPI with uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8060,
        reload=True,
        log_level="debug"
    )