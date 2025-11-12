const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3003;

// Middleware
app.use(express.json());

// Load fixtures
const fixturesPath = path.join(__dirname, 'fixtures.json');
const fixtures = JSON.parse(fs.readFileSync(fixturesPath, 'utf8'));

/**
 * GET /open_api/v1.3/campaign/get/
 * Returns campaigns with optional filtering by advertiser_id and date range
 */
app.get('/open_api/v1.3/campaign/get/', (req, res) => {
  const { advertiser_id, start_date, end_date } = req.query;

  // Start with all campaigns
  let campaigns = fixtures.data.campaigns;

  // Filter by advertiser_id if provided
  if (advertiser_id) {
    campaigns = campaigns.filter(
      campaign => campaign.advertiser_id === advertiser_id
    );
  }

  // Filter by date range if provided
  // Dates should be in format YYYY-MM-DD
  if (start_date && end_date) {
    const startTimestamp = Math.floor(new Date(start_date).getTime() / 1000);
    const endTimestamp = Math.floor(new Date(end_date).getTime() / 1000);

    campaigns = campaigns.filter(campaign => {
      const campaignStartTime = campaign.start_time;
      const campaignEndTime = campaign.end_time;

      // Check if campaign overlaps with requested date range
      return (
        campaignStartTime <= endTimestamp &&
        campaignEndTime >= startTimestamp
      );
    });
  }

  // Build response matching TikTok API structure
  const response = {
    data: {
      campaigns: campaigns
    },
    code: 0,
    message: 'OK',
    request_id: generateRequestId()
  };

  res.status(200).json(response);
});

/**
 * GET /open_api/v1.3/campaign/get/:campaign_id
 * Returns a single campaign by ID
 */
app.get('/open_api/v1.3/campaign/get/:campaign_id', (req, res) => {
  const { campaign_id } = req.params;
  const { advertiser_id } = req.query;

  let campaign = fixtures.data.campaigns.find(
    c => c.campaign_id === campaign_id
  );

  // Check advertiser_id if provided
  if (campaign && advertiser_id && campaign.advertiser_id !== advertiser_id) {
    campaign = null;
  }

  if (!campaign) {
    return res.status(404).json({
      data: null,
      code: 40001,
      message: 'Campaign not found',
      request_id: generateRequestId()
    });
  }

  const response = {
    data: {
      campaign: campaign
    },
    code: 0,
    message: 'OK',
    request_id: generateRequestId()
  };

  res.status(200).json(response);
});

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'OK',
    timestamp: new Date().toISOString()
  });
});

/**
 * Generate a request ID similar to TikTok API format
 */
function generateRequestId() {
  const timestamp = Date.now().toString();
  const random = Math.floor(Math.random() * 1000000000).toString().padStart(10, '0');
  return timestamp + random;
}

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({
    data: null,
    code: 50000,
    message: 'Internal Server Error',
    request_id: generateRequestId()
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    data: null,
    code: 40004,
    message: 'Endpoint not found',
    request_id: generateRequestId()
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`TikTok Ads API Mock Server running on http://localhost:${PORT}`);
  console.log(`Available endpoints:`);
  console.log(`  GET /open_api/v1.3/campaign/get/ - Get all campaigns`);
  console.log(`  GET /open_api/v1.3/campaign/get/:campaign_id - Get specific campaign`);
  console.log(`  GET /health - Health check`);
});

module.exports = app;
