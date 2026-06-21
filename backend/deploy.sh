#!/bin/bash
# deploy.sh
# Deploys the Rebranded A2UI Seed Agent to Cloud Run with IAM Service Account Identity

SERVICE_NAME="a2ui-seed-agent"
REGION="us-central1"

echo "Deploying service '$SERVICE_NAME' to Cloud Run..."

# Extract Google Maps API Key from local environment if available
if [ -z "$GOOGLE_MAPS_API_KEY" ]; then
    if [ -f "./.env" ]; then
        export $(grep -v '^#' ./.env | grep GOOGLE_MAPS_API_KEY | xargs)
    fi
fi

# Resolve active GCP Project ID dynamically for service account mapping
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ] || [ "$PROJECT_ID" = "YOUR_GCP_PROJECT_ID" ]; then
    echo "❌ ERROR: No active Google Cloud Project is configured in your gcloud CLI."
    echo "   Please set your active project before deploying using:"
    echo "   gcloud config set project YOUR_GCP_PROJECT_ID"
    exit 1
fi

# Resolve URL first if service already exists
EXISTING_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)' 2>/dev/null)

if [ -n "$EXISTING_URL" ]; then
    echo "Existing Service URL found: $EXISTING_URL"
    AGENT_URL_VAL="$EXISTING_URL"
else
    # Temporary placeholder for first deploy
    AGENT_URL_VAL="pending"
fi

# Deploy to Cloud Run from source code attaching a dedicated least-privilege identity
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --service-account="a2ui-seed-run-identity@$PROJECT_ID.iam.gserviceaccount.com" \
    --set-env-vars="GEMINI_MODEL=gemini-3.1-flash-lite-preview,GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY,AGENT_URL=$AGENT_URL_VAL" \
    --quiet

echo "Deployment complete."

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format='value(status.url)')
echo "Service URL: $SERVICE_URL"

if [ "$AGENT_URL_VAL" = "pending" ]; then
    echo "Updating service with its public URL for A2A headers..."
    gcloud run services update "$SERVICE_NAME" --region "$REGION" --update-env-vars=AGENT_URL=$SERVICE_URL --quiet
fi
