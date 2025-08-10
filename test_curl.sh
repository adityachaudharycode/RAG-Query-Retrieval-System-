#!/bin/bash

# Test script using curl to test the API
# Make sure the server is running first: python run-fast.py

echo "🧪 Testing API with curl..."
echo "================================"

# Configuration
API_URL="http://localhost:8000"
BEARER_TOKEN="87e1f87355284c19bac1880413d4a1e7cb868891939fc1c6d8227ee2c1b89cb0"
DOCUMENT_URL="https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"

# Test 1: Health check
echo "🔍 Testing health endpoint..."
curl -X GET "$API_URL/health" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n\n"

# Test 2: Main endpoint
echo "🚀 Testing main endpoint..."
curl -X POST "$API_URL/hackrx/run" \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "'$DOCUMENT_URL'",
    "questions": [
      "What is the grace period for premium payment?",
      "What is the waiting period for cataract surgery?",
      "What is the waiting period for pre-existing diseases?"
    ]
  }' \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n" \
  --max-time 120

echo "================================"
echo "✅ Test completed"
