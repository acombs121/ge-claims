#!/bin/bash

# Local testing script following A2A JSON-RPC stream specification
# Usage: ./test_local.sh "give me the top 5 MSAs for MASH"

QUERY=${1:-"give me the top 5 MSAs for MASH"}
PORT=${2:-8080}

echo "Submitting query: '$QUERY' to local endpoint on port $PORT..."

curl -N -X POST "http://127.0.0.1:$PORT/" \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "jsonrpc": "2.0",
  "id": "diagnostic-$(date +%s)",
  "method": "message/stream",
  "params": {
    "configuration": {
      "acceptedOutputModes": [],
      "blocking": true
    },
    "message": {
      "kind": "message",
      "messageId": "msg-$(date +%s)",
      "parts": [
        {
          "kind": "text",
          "text": "$QUERY"
        }
      ],
      "role": "user"
    },
    "metadata": {
      "a2uiClientCapabilities": {
        "supportedCatalogIds": [
          "https://a2ui.org/specification/v0_8/standard_catalog_definition.json"
        ]
      },
      "X-A2A-Extensions": "https://a2ui.org/a2a-extension/a2ui/v0.8"
    }
  }
}
EOF

echo -e "\n--- Stream Complete ---"
