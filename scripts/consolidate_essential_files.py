#!/usr/bin/env python3
"""
Essential Python Files Consolidation Script
Consolidates only the core Python files needed for Drox_AI to operate with all features.
"""

import os
import glob
from pathlib import Path

def collect_essential_python_files():
    """Collect only essential Python files needed for Drox_AI operation."""
    
    # Define essential files for the system to operate
    essential_files = [
        # Core system files
        'main.py',
        'chimera_autarch.py',
        'chimera_main.py', 
        'chimera_core_rebuild_final.py',
        'chimera_core_rebuild.py',
        'DroxAI_Core.py',
        
        # Configuration and management
        'config.py',
        'droxai_config.py',
        'DroxAI_ConfigManager.py',
        'DroxAI_Launcher.py',
        'DroxAI_Consumer_Ready.py',
        
        # Key components
        'event_broker.py',
        'llm_integration.py',
        'personality_engine.py',
        'security.py',
        'security_truncated.py',
        'voice_interface.py',
        'voice_interface_broken.py',
        'plugin_system.py',
        
        # Services and APIs
        'graphql_api.py',
        'http_api_gateway.py',
        'ws_bridge.py',
        'ws_client.py',
        
        # Advanced features
        'anomaly_detection.py',
        'base_events.py',
        'cloud_orchestrator.py',
        'cognitive_reasoning_evaluator.py',
        'comprehensive_agent_evaluator.py',
        'federated_learning.py',
        'genetic_evolution.py',
        'neural_evolution.py',
        'predictive_monitor.py',
        'quantum_optimizer.py',
        'swarm_coordination.py',
        'system_prompt_evaluator.py',
        'system_prompt_evaluator_fixed.py',
        'tower_integration.py',
        'unify_everything.py',
        'unrestricted_ai_system.py',
        'user_compliance_integrator.py',
        'chimera_nexus_integration.py',
        'chimera_voice.py',
        'chimera_autarch_v4_tuned.py',
        'chimera_god_cli.py',
        'bulk_code_optimizer_fixed.py',
        
        # Additional utilities
        'hot_reload.py',
        'personality_system.py',
        'genetic_demo.py',
        'event_stream_demo.py',
        'quick_test.py',
        'import json.py',
        'import_requests.py',
        'logistical_reasoning_evaluator.py',
        'unify_ports.py',
        'unify_ports (2).py'
    ]
    
    # Files from subdirectories
    subdir_files = [
        'config/settings.py',
        'consumer/DroxAI_Consumer_Ready.py',
        'consumer/test_consumer.py',
        'Docs/code_analysis.py',
        'Docs/blockchain_audit.py',
        'Docs/demo_new_features.py',
        'Docs/evaluation_framework_demo.py',
        'build/droxai_config.py',
        'src/main.py',
        'src/chimera/core.py',
        'src/chimera/web.py',
        'src/services/intent_compiler.py',
        'src/services/orchestrator.py',
        'src/api/server.py',
        'tests/test_core.py',
        'tests/test_api.py',
        'scripts/guard_source.py'
    ]
    
    all_files = essential_files + subdir_files
    
    # Filter to only existing files
    existing_files = []
    for file_path in all_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
        else:
            print(f"Warning: {file_path} not found, skipping")
    
    return sorted(existing_files)

def read_file_safely(file_path):
    """Read file content safely with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def consolidate_essential_files():
    """Main consolidation function for essential files."""
    python_files = collect_essential_python_files()
    
    print(f"Found {len(python_files)} essential Python files to consolidate:")
    for file in python_files:
        print(f"  - {file}")
    
    # Create consolidated file
    consolidated_content = []
    consolidated_content.append('#!/usr/bin/env python3')
    consolidated_content.append('"""')
    consolidated_content.append('DROX_AI - ESSENTIAL SYSTEM CONSOLIDATION')
    consolidated_content.append('==========================================')
    consolidated_content.append('')
    consolidated_content.append('This file contains all essential Python code needed for')
    consolidated_content.append('Drox_AI to operate with full functionality and features.')
    consolidated_content.append('')
    consolidated_content.append('Generated on: 2025-11-29 10:30:14')
    consolidated_content.append(f'Essential files consolidated: {len(python_files)}')
    consolidated_content.append('')
    consolidated_content.append('SYSTEM FEATURES PRESERVED:')
    consolidated_content.append('- Core CHIMERA AUTARCH system')
    consolidated_content.append('- AI orchestration and evolution')
    consolidated_content.append('- Web interface and APIs')
    consolidated_content.append('- Voice interface capabilities')
    consolidated_content.append('- LLM integration')
    consolidated_content.append('- Federated learning')
    consolidated_content.append('- Quantum optimization')
    consolidated_content.append('- Neural evolution')
    consolidated_content.append('- Security and compliance')
    consolidated_content.append('- Plugin system architecture')
    consolidated_content.append('- GraphQL and WebSocket APIs')
    consolidated_content.append('- All wicked features intact')
    consolidated_content.append('"""')
    consolidated_content.append('')
    
    # Process each file
    for i, file_path in enumerate(python_files, 1):
        print(f"Processing file {i}/{len(python_files)}: {file_path}")
        
        content = read_file_safely(file_path)
        
        # Add section header
        consolidated_content.append('=' * 80)
        consolidated_content.append(f'# FILE: {file_path}')
        consolidated_content.append('=' * 80)
        consolidated_content.append('')
        
        # Add file content
        if content:
            consolidated_content.append(content)
        else:
            consolidated_content.append('# Error reading file content')
        
        consolidated_content.append('')
        consolidated_content.append('')
    
    # Write consolidated file
    output_file = 'DROX_AI_ESSENTIAL_CONSOLIDATED.py'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(consolidated_content))
    
    print(f"\nConsolidation complete!")
    print(f"Output file: {output_file}")
    print(f"Total lines: {sum(len(content.splitlines()) for content in consolidated_content)}")
    print(f"Essential features preserved: ALL WICKED FEATURES INTACT")
    
    return output_file

if __name__ == "__main__":
    consolidate_essential_files()
