#!/usr/bin/env python3
"""
DroxAI Autarch Tool Validation Client (test_tools.py)

Tests the WebSocket API endpoints to ensure the Chimera Autarch backend 
(chimera_autarch_v4_tuned.py) is operational and its complex tools are functional.
"""

import asyncio
import websockets
import json
import time
import os
import logging
from typing import Dict, Any

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DroxAI.Client")

# --- Configuration (Reads from environment set by DroxAI_Launcher) ---
WS_HOST = os.environ.get("WS_HOST", "127.0.0.1")
WS_PORT = os.environ.get("WS_PORT", "3000")
WS_URL = f"ws://{WS_HOST}:{WS_PORT}"

async def send_message(websocket, message: dict) -> Dict[str, Any]:
    """Send JSON message, wait for response, and log details."""
    raw_message = json.dumps(message)
    logger.info(f"--> [REQ] Type: {message.get('type')}")
    
    start_time = time.time()
    await websocket.send(raw_message)
    
    response = await websocket.recv()
    elapsed = time.time() - start_time
    
    data = json.loads(response)
    
    if data.get('success', False) or data.get('type') == 'system_status':
        logger.info(f"<-- [RESP] Type: {data.get('type')} | Success: {data.get('success', True)} | Time: {elapsed:.3f}s")
    else:
        logger.error(f"<-- [FAIL] Type: {data.get('type')} | Error: {data.get('error', data.get('result'))} | Time: {elapsed:.3f}s")
        
    return data

async def run_client_tests():
    """Main client connection and tool test loop."""
    try:
        async with websockets.connect(WS_URL) as websocket:
            logger.info(f"==================================================")
            logger.info(f"Connected to DroxAI Autarch at {WS_URL}")
            
            # -----------------------------------------------------------------
            # TEST 1: System Status Check (Reads DB Metrics)
            # -----------------------------------------------------------------
            status_request = {"type": "status_request"}
            status_response = await send_message(websocket, status_request)
            
            system_status = status_response.get("system_health", {})
            logger.info(f"STATUS: System Health: {system_status.get('status')} | CPU: {system_status.get('cpu_percent', 0.0):.1f}%")
            logger.info(f"STATUS: Tools Registered: {len(status_response.get('tool_health', {}))}")
            
            # -----------------------------------------------------------------
            # TEST 2: Echo Tool Execution (Security/Connectivity Check)
            # -----------------------------------------------------------------
            echo_request = {"type": "echo", "message": "Verify core security validation is active."}
            await send_message(websocket, echo_request)
            
            # -----------------------------------------------------------------
            # TEST 3: Anomaly Check (metric_data -> anomaly_check tool)
            # -----------------------------------------------------------------
            anomaly_request = {
                "type": "metric_data",
                "metric_name": "database_latency",
                "value": time.time() % 0.5 + 0.1 # Simulated realistic metric value
            }
            anomaly_response = await send_message(websocket, anomaly_request)
            
            if anomaly_response.get("success"):
                result = anomaly_response["result"]
                logger.info(f"ANOMALY: Check complete. Is Anomaly: {result['is_anomaly']} | Confidence: {result['confidence']:.2f}")
            
            # -----------------------------------------------------------------
            # TEST 4: Bulk Optimization (optimize -> bulk_optimize tool)
            # This simulates invoking the asynchronous thread-pool execution
            # -----------------------------------------------------------------
            optimize_request = {
                "type": "optimize", 
                "target_path": "plugins/code_src", 
                "output_path": "temp/optimized_code"
            }
            logger.warning("OPTIMIZE: This test simulates a long-running, synchronous operation.")
            optimize_response = await send_message(websocket, optimize_request)
            
            if optimize_response.get("success"):
                 result = optimize_response["result"]
                 logger.info(f"OPTIMIZE: Successful. Files Improved: {result['files_improved']} | Gain: {result['performance_gain']}")
            
            logger.info(f"==================================================")
            logger.info("âœ… All core API and tool integration tests complete.")
            logger.info(f"==================================================")


    except ConnectionRefusedError:
        logger.error(f"FATAL: Connection refused. Ensure the DroxAI backend is running at {WS_URL} and the firewall is open.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during testing: {e}")

if __name__ == "__main__":
    asyncio.run(run_client_tests())
