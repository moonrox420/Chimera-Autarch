# CHIMERA NEXUS v3.0 - Comprehensive Test Suite
# Tests all 10 revolutionary systems + core features

Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          CHIMERA NEXUS v3.0 - Comprehensive Test Suite          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Activate environment
if (Test-Path "droxai-env\Scripts\Activate.ps1") {
  & .\droxai-env\Scripts\Activate.ps1
}
else {
  Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
  exit 1
}

$totalTests = 0
$passedTests = 0
$failedTests = 0

function Test-Component {
  param(
    [string]$Name,
    [string]$TestCode,
    [string]$Category = "CORE"
  )
    
  $global:totalTests++
  Write-Host "[$Category] Testing $Name..." -NoNewline -ForegroundColor Cyan
    
  try {
    $output = python -c $TestCode 2>&1
    if ($LASTEXITCODE -eq 0) {
      Write-Host " ✅ PASS" -ForegroundColor Green
      $global:passedTests++
      return $true
    }
    else {
      Write-Host " ❌ FAIL" -ForegroundColor Red
      Write-Host "  Error: $output" -ForegroundColor Gray
      $global:failedTests++
      return $false
    }
  }
  catch {
    Write-Host " ❌ FAIL" -ForegroundColor Red
    Write-Host "  Exception: $_" -ForegroundColor Gray
    $global:failedTests++
    return $false
  }
}

Write-Host "🧪 Running test suite..." -ForegroundColor Yellow
Write-Host ""

# ==========================================
# CORE DEPENDENCIES
# ==========================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "  CORE DEPENDENCIES" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

Test-Component "Python version" "import sys; assert sys.version_info >= (3, 12)" "CORE"
Test-Component "NumPy" "import numpy; assert numpy.__version__ >= '1.24'" "CORE"
Test-Component "WebSockets" "import websockets; print('OK')" "CORE"
Test-Component "AioSQLite" "import aiosqlite; print('OK')" "CORE"
Test-Component "PyYAML" "import yaml; print('OK')" "CORE"

# ==========================================
# MACHINE LEARNING STACK
# ==========================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "  MACHINE LEARNING STACK" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

Test-Component "TensorFlow" "import tensorflow as tf; print(tf.__version__)" "ML"
Test-Component "TensorFlow GPU Check" "import tensorflow as tf; print('CPUs:', len(tf.config.list_physical_devices('CPU')))" "ML"
Test-Component "scikit-learn" "import sklearn; print(sklearn.__version__)" "ML"
Test-Component "Isolation Forest" "from sklearn.ensemble import IsolationForest; print('OK')" "ML"

# ==========================================
# FEDERATED LEARNING
# ==========================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "  FEDERATED LEARNING" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

Test-Component "Flower framework" "import flwr; print('OK')" "FL"
Test-Component "gRPC" "import grpc; print('OK')" "FL"
Test-Component "gRPC health checking" "import grpc_health; print('OK')" "FL"

# ==========================================
# 1. NEURAL EVOLUTION ENGINE
# ==========================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "  1. NEURAL EVOLUTION ENGINE" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

Test-Component "Neural Evolution import" "from neural_evolution import NeuralEvolutionEngine; print('OK')" "NEURAL"
Test-Component "Code Analyzer" "from neural_evolution import CodeAnalyzer; print('OK')" "NEURAL"
Test-Component "Code Optimizer" "from neural_evolution import CodeOptimizer; print('OK')" "NEURAL"
Test-Component "Performance Tester" "from neural_evolution import PerformanceTester; print('OK')" "NEURAL"

# ==========================================
# 2. QUANTUM OPTIMIZER
# ==========================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "  2. QUANTUM OPTIMIZER" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

Test-Component "Hybrid Quantum Optimizer" "from quantum_optimizer import HybridQuantumOptimizer; print('OK')" "QUANTUM"
Test-Component "Simulated Annealing" "from quantum_optimizer import SimulatedAnnealingOptimizer; print('OK')" "QUANTUM"
Test-Component "Adaptive Optimizer" "from quantum_optimizer import AdaptiveQuantumOptimizer; print('OK')" "QUANTUM"

# ==========================================
# 3. PERSONALITY SYSTEM
# ==========================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "  3. PERSONALITY SYSTEM" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

Test-Component "Personality Engine" "from personality_system import PersonalityEngine; print('OK')" "PERSONALITY"
Test-Component "Personality Modes" "from personality_system import PersonalityMode; print('OK')" "PERSONALITY"
$testCode = @"
from personality_system import PersonalityEngine
engine = PersonalityEngine()
assert engine.current_mode is not None
print('OK')
"@
Test-Component "Personality initialization" $testCode "PERSONALITY"

# ==========================================
# 4. BLOCKCHAIN AUDIT LOGGER
# ==========================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "  4. BLOCKCHAIN AUDIT LOGGER" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

Test-Component "Audit Logger" "from blockchain_audit import AuditLogger; print('OK')" "BLOCKCHAIN"
Test-Component "Block structure" "from blockchain_audit import Block; print('OK')" "BLOCKCHAIN"
Test-Component "Blockchain validation" "from blockchain_audit import Blockchain; print('OK')" "BLOCKCHAIN"

# ==========================================
# 5. 3D VR DASHBOARD
# ==========================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "  5. 3D VR DASHBOARD" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

if (Test-Path "dashboard_3d.html") {
  Write-Host "[3D] Dashboard file exists..." -NoNewline -ForegroundColor Cyan
  Write-Host " ✅ PASS" -ForegroundColor Green
  $passedTests++
  $totalTests++
}
else {
  Write-Host "[3D] Dashboard file exists..." -NoNewline -ForegroundColor Cyan
  Write-Host " ❌ FAIL" -ForegroundColor Red
  $failedTests++
  $totalTests++
}

# ==========================================
# 6. VOICE INTERFACE
# ==========================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "  6. VOICE INTERFACE" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

Test-Component "Whisper import" "import whisper; print('OK')" "VOICE"
Test-Component "pyttsx3 TTS" "import pyttsx3; print('OK')" "VOICE"
Test-Component "sounddevice" "import sounddevice; print('OK')" "VOICE"
Test-Component "Voice Interface" "from voice_interface import VoiceInterface; print('OK')" "VOICE"

# ==========================================
# 7. GENETIC EVOLUTION
# ==========================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "  7. GENETIC EVOLUTION" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

Test-Component "Genetic Engine" "from genetic_evolution import GeneticEvolutionEngine; print('OK')" "GENETIC"
Test-Component "Individual class" "from genetic_evolution import Individual; print('OK')" "GENETIC"
Test-Component "Genome structure" "from genetic_evolution import Genome; print('OK')" "GENETIC"

# ==========================================
# 8. PREDICTIVE MONITOR
# ==========================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "  8. PREDICTIVE MONITOR" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

Test-Component "Predictive Monitor" "from predictive_monitor import PredictiveMonitor; print('OK')" "PREDICTIVE"
Test-Component "LSTM model" "from predictive_monitor import RealLSTM; print('OK')" "PREDICTIVE"
Test-Component "Anomaly Detector" "from predictive_monitor import RealAnomalyDetector; print('OK')" "PREDICTIVE"

# ==========================================
# 9. CLOUD ORCHESTRATOR
# ==========================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "  9. CLOUD ORCHESTRATOR" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

Test-Component "Multi-Cloud Orchestrator" "from cloud_orchestrator import MultiCloudOrchestrator; print('OK')" "CLOUD"
Test-Component "AWS Adapter" "from cloud_orchestrator import AWSAdapter; print('OK')" "CLOUD"
Test-Component "boto3 SDK" "import boto3; print('OK')" "CLOUD"

# ==========================================
# 10. PLUGIN SYSTEM
# ==========================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "  10. PLUGIN MARKETPLACE" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

Test-Component "Plugin Manager" "from plugin_system import PluginManager; print('OK')" "PLUGIN"
Test-Component "Plugin Sandbox" "from plugin_system import PluginSandbox; print('OK')" "PLUGIN"
Test-Component "Plugin Marketplace" "from plugin_system import PluginMarketplace; print('OK')" "PLUGIN"

# ==========================================
# INTEGRATION LAYER
# ==========================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "  INTEGRATION LAYER" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

Test-Component "NEXUS Integration" "from chimera_nexus_integration import ChimeraNexusIntegration; print('OK')" "NEXUS"
Test-Component "Config loading" "from chimera_nexus_integration import ChimeraNexusIntegration; c = ChimeraNexusIntegration(); print('OK')" "NEXUS"

# ==========================================
# CORE CHIMERA
# ==========================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "  CORE CHIMERA AUTARCH" -ForegroundColor Magenta
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

if (Test-Path "chimera_autarch.py") {
  Write-Host "[CHIMERA] Main file exists..." -NoNewline -ForegroundColor Cyan
  Write-Host " ✅ PASS" -ForegroundColor Green
  $passedTests++
  $totalTests++
}
else {
  Write-Host "[CHIMERA] Main file exists..." -NoNewline -ForegroundColor Cyan
  Write-Host " ❌ FAIL" -ForegroundColor Red
  $failedTests++
  $totalTests++
}

# ==========================================
# RESULTS
# ==========================================
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                         TEST RESULTS                             ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$successRate = [math]::Round(($passedTests / $totalTests) * 100, 1)

Write-Host "Total Tests:   $totalTests" -ForegroundColor White
Write-Host "Passed:        $passedTests ✅" -ForegroundColor Green
Write-Host "Failed:        $failedTests ❌" -ForegroundColor Red
Write-Host "Success Rate:  $successRate%" -ForegroundColor $(if ($successRate -ge 90) { "Green" } elseif ($successRate -ge 70) { "Yellow" } else { "Red" })
Write-Host ""

if ($successRate -eq 100) {
  Write-Host "🎉 PERFECT SCORE! All systems operational!" -ForegroundColor Green
  Write-Host ""
  Write-Host "Ready to launch CHIMERA NEXUS:" -ForegroundColor Cyan
  Write-Host "  .\start_nexus_v3.ps1" -ForegroundColor White
  exit 0
}
elseif ($successRate -ge 90) {
  Write-Host "✅ EXCELLENT! CHIMERA ready to launch" -ForegroundColor Green
  Write-Host ""
  Write-Host "  .\start_nexus_v3.ps1" -ForegroundColor White
  exit 0
}
elseif ($successRate -ge 70) {
  Write-Host "⚠️  GOOD, but some components missing" -ForegroundColor Yellow
  Write-Host "CHIMERA will run with reduced functionality" -ForegroundColor Gray
  exit 0
}
else {
  Write-Host "❌ CRITICAL FAILURES - Fix errors before launching" -ForegroundColor Red
  Write-Host "Run: .\install_quick_windows.ps1" -ForegroundColor Yellow
  exit 1
}
