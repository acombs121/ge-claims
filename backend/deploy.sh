#!/bin/bash
# deploy.sh
# Deploys the Generic ADK Orchestrator Agent to Cloud Run

SERVICE_NAME="aon-hr-agent"
REGION="us-central1"

echo "Deploying service '$SERVICE_NAME' to Cloud Run..."

# Extract Google Maps API Key from Bayer environment if available
if [ -z "$GOOGLE_MAPS_API_KEY" ]; then
    if [ -f "../../aon-hr-agent/backend/.env" ]; then
        export $(grep -v '^#' ../../aon-hr-agent/backend/.env | grep GOOGLE_MAPS_API_KEY | xargs)
    fi
fi

# Deploy to Cloud Run from source code
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars="GEMINI_MODEL=gemini-3.1-flash-lite-preview,GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY" \
    --quiet


echo "Deployment complete."

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format='value(status.url)')
echo "Service URL: $SERVICE_URL"

echo "Updating service with its public URL for A2A headers..."
# Required so that the agent can derive correct absolute paths for bridging
gcloud run services update "$SERVICE_NAME" --region "$REGION" --update-env-vars=AGENT_URL=$SERVICE_URL --quiet
