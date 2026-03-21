#!/bin/bash
# deploy.sh
# Deploys the Generic ADK Orchestrator Agent to Cloud Run

SERVICE_NAME="my-custom-agent"
REGION="us-central1"

echo "Deploying service '$SERVICE_NAME' to Cloud Run..."

# Deploy to Cloud Run from source code
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars="GEMINI_MODEL=gemini-3-flash-preview" \
    --quiet

echo "Deployment complete."

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format='value(status.url)')
echo "Service URL: $SERVICE_URL"

echo "Updating service with its public URL for A2A headers..."
# Required so that the agent can derive correct absolute paths for bridging
gcloud run services update "$SERVICE_NAME" --region "$REGION" --update-env-vars=AGENT_URL=$SERVICE_URL --quiet
