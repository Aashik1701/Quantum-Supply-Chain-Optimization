#!/bin/bash
# Quick setup script for IBM Quantum integration

echo "=========================================="
echo "IBM Quantum Platform Setup"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# IBM Quantum Platform Configuration
IBM_QUANTUM_TOKEN=

# Backend selection (optional)
QUANTUM_BACKEND=ibmq_qasm_simulator

# Flask configuration
FLASK_ENV=development
PORT=5000
EOF
    echo "✓ Created .env file"
    echo ""
fi

# Check if token is set
if grep -q "IBM_QUANTUM_TOKEN=$" .env; then
    echo "⚠️  IBM_QUANTUM_TOKEN is empty in .env"
    echo ""
    echo "📝 To set up IBM Quantum:"
    echo "   1. Go to: https://quantum-computing.ibm.com/"
    echo "   2. Sign up / Log in"
    echo "   3. Get your API token from Account Settings"
    echo "   4. Add to .env file: IBM_QUANTUM_TOKEN=your_token_here"
    echo ""
fi

# Install quantum dependencies
echo "Installing quantum computing dependencies..."
pip install -r requirements-quantum.txt

echo ""
echo "✓ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Add IBM_QUANTUM_TOKEN to .env file"
echo "  2. Run: python test_ibm_quantum.py"
echo "  3. Start using IBM Quantum backends!"
echo ""
