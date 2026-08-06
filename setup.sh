#!/usr/bin/env bash
# setup.sh
# Convenience script to set up the Conda environment and install
# dependencies, as described in the project PPT.
#
# Usage:
#   bash setup.sh

set -e

ENV_NAME="myntra-review-scrapper"
PYTHON_VERSION="3.10"

echo "Creating Conda environment '$ENV_NAME' with Python $PYTHON_VERSION..."
conda create -y -n "$ENV_NAME" python="$PYTHON_VERSION"

echo "Activating environment..."
# shellcheck disable=SC1091
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "Setup complete. Activate the environment with:"
echo "    conda activate $ENV_NAME"
echo ""
echo "Then run the app with either:"
echo "    python app.py                 # Flask, http://localhost:5000"
echo "    streamlit run streamlit_app.py  # Streamlit, http://localhost:8501"
