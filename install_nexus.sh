#!/bin/bash
# CHIMERA NEXUS - Complete Installation Script
# Installs ALL real dependencies for production-grade AI system

echo "🚀 CHIMERA NEXUS v3.0 - Complete Installation"
echo "=============================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.12.0"

echo "✓ Python version: $python_version"

if [ ! -d "droxai-env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv droxai-env
fi

echo "🔧 Activating virtual environment..."
source droxai-env/bin/activate

echo "📥 Installing core dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "🤖 Installing ML/AI packages (this may take a while)..."
pip install tensorflow>=2.15.0 scikit-learn>=1.3.0

echo ""
echo "☁️  Installing cloud SDKs..."
pip install boto3>=1.34.0 azure-mgmt-compute>=30.0.0 google-cloud-compute>=1.15.0

echo ""
echo "🎤 Installing voice processing..."
pip install openai-whisper sounddevice pyttsx3

# Platform-specific audio setup
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Linux detected - installing PortAudio..."
    sudo apt-get update && sudo apt-get install -y portaudio19-dev python3-pyaudio ffmpeg
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS detected - installing PortAudio..."
    brew install portaudio ffmpeg
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📊 System Status:"
python3 << EOF
import sys
print(f"  Python: {sys.version.split()[0]}")

try:
    import tensorflow as tf
    print(f"  TensorFlow: {tf.__version__} ✅")
except:
    print("  TensorFlow: Not installed ❌")

try:
    import sklearn
    print(f"  scikit-learn: {sklearn.__version__} ✅")
except:
    print("  scikit-learn: Not installed ❌")

try:
    import whisper
    print(f"  Whisper: Installed ✅")
except:
    print("  Whisper: Not installed ❌")

try:
    import pyttsx3
    print(f"  pyttsx3: Installed ✅")
except:
    print("  pyttsx3: Not installed ❌")

try:
    import boto3
    print(f"  boto3: {boto3.__version__} ✅")
except:
    print("  boto3: Not installed ❌")

try:
    import azure.mgmt.compute
    print(f"  Azure SDK: Installed ✅")
except:
    print("  Azure SDK: Not installed ❌")

try:
    import google.cloud.compute_v1
    print(f"  GCP SDK: Installed ✅")
except:
    print("  GCP SDK: Not installed ❌")
EOF

echo ""
echo "🎯 Next Steps:"
echo "1. Configure cloud credentials (see INTEGRATION_GUIDE.md)"
echo "2. Test individual systems: python3 predictive_monitor.py"
echo "3. Start CHIMERA: python3 chimera_autarch.py"
echo "4. Access 3D dashboard: http://localhost:8000"
echo ""
echo "📖 Full guide: cat INTEGRATION_GUIDE.md"
echo ""
echo "🔥 Ready to change the world!"
