#!/usr/bin/env python3
"""
scripts/rollback_model.py
Connects to MLflow and updates the 'Production' alias to point to the previous version.
"""
import os
import argparse
from mlflow.tracking import MlflowClient

def main():
    parser = argparse.ArgumentParser(description="Rollback MLflow model alias")
    parser.add_argument("--model-name", type=str, default="ticket-triage-classifier")
    parser.add_argument("--version", type=int, required=True, help="The model version to rollback to")
    parser.add_argument("--alias", type=str, default="Production")
    args = parser.parse_args()

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    client = MlflowClient(tracking_uri=tracking_uri)

    print(f"Setting alias '{args.alias}' for model '{args.model_name}' to version {args.version} on MLflow at {tracking_uri}")
    try:
        client.set_registered_model_alias(args.model_name, args.alias, str(args.version))
        print("Model rollback successful.")
    except Exception as e:
        print(f"Failed to rollback model: {e}")
        exit(1)

if __name__ == "__main__":
    main()
