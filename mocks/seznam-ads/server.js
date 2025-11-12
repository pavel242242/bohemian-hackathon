/**
 * Seznam Ads Mock Server
 *
 * Simulates a complex, unfriendly API with:
 * - Nested pagination with cursor tokens
 * - Rate limiting
 * - Non-standard response format
 * - Multiple endpoints needed for complete data
 */

const express = require('express');
const app = express();
const PORT = process.env.PORT || 3004;

// Rate limiting state
let requestCount = 0;
let resetTime = Date.now() + 60000; // Reset every minute

// Mock data
const CAMPAIGNS = [
  {
    campaignId: 'szn_c_001',
    name: 'Nike Běžecké Boty Zima 2025',
    status: 'ACTIVE',
    dailyBudgetCZK: 45000,
    created: '2025-09-01T08:00:00Z',
    updated: '2025-11-10T14:30:00Z'
  },
  {
    campaignId: 'szn_c_002',
    name: 'Nike Air Max Kampaň',
    status: 'ACTIVE',
    dailyBudgetCZK: 32000,
    created: '2025-09-15T10:00:00Z',
    updated: '2025-11-11T09:15:00Z'
  },
  {
    campaignId: 'szn_c_003',
    name: 'Nike Sportovní Oblečení',
    status: 'ACTIVE',
    dailyBudgetCZK: 28000,
    created: '2025-10-01T12:00:00Z',
    updated: '2025-11-09T16:45:00Z'
  },
  {
    campaignId: 'szn_c_004',
    name: 'Nike Zimní Kolekce Premium',
    status: 'PAUSED',
    dailyBudgetCZK: 55000,
    created: '2025-08-20T07:30:00Z',
    updated: '2025-11-08T11:00:00Z'
  },
  {
    campaignId: 'szn_c_005',
    name: 'Nike Running Club CZ',
    status: 'ACTIVE',
    dailyBudgetCZK: 38000,
    created: '2025-09-10T09:00:00Z',
    updated: '2025-11-11T10:30:00Z'
  }
];

const ADS = {
  'szn_c_001': [
    { adId: 'ad_001_1', title: 'Běžecké boty Nike', clicks: 12500, impressions: 450000, ctr: 2.78 },
    { adId: 'ad_001_2', title: 'Zimní běh s Nike', clicks: 8900, impressions: 320000, ctr: 2.78 }
  ],
  'szn_c_002': [
    { adId: 'ad_002_1', title: 'Nike Air Max', clicks: 9800, impressions: 380000, ctr: 2.58 }
  ],
  'szn_c_003': [
    { adId: 'ad_003_1', title: 'Sportovní móda Nike', clicks: 7200, impressions: 290000, ctr: 2.48 }
  ],
  'szn_c_004': [
    { adId: 'ad_004_1', title: 'Premium zimní kolekce', clicks: 15000, impressions: 520000, ctr: 2.88 }
  ],
  'szn_c_005': [
    { adId: 'ad_005_1', title: 'Running Club Nike', clicks: 10500, impressions: 360000, ctr: 2.92 }
  ]
};

const STATS = {
  'szn_c_001': { totalSpend: 1350000, avgCPC: 108, conversions: 450, conversionRate: 3.6 },
  'szn_c_002': { totalSpend: 960000, avgCPC: 98, conversions: 320, conversionRate: 3.27 },
  'szn_c_003': { totalSpend: 840000, avgCPC: 117, conversions: 280, conversionRate: 3.89 },
  'szn_c_004': { totalSpend: 1650000, avgCPC: 110, conversions: 550, conversionRate: 3.67 },
  'szn_c_005': { totalSpend: 1140000, avgCPC: 109, conversions: 390, conversionRate: 3.71 }
};

// Middleware: Check API key
app.use((req, res, next) => {
  const apiKey = req.headers['x-seznam-api-key'];

  if (!apiKey) {
    return res.status(401).json({
      responseMetadata: {
        status: 'ERROR',
        errorCode: 'AUTH_REQUIRED',
        message: 'API key missing'
      }
    });
  }

  next();
});

// Middleware: Rate limiting
app.use((req, res, next) => {
  if (Date.now() > resetTime) {
    requestCount = 0;
    resetTime = Date.now() + 60000;
  }

  requestCount++;

  // Seznam Ads style rate limit headers
  res.setHeader('X-RateLimit-Limit', '100');
  res.setHeader('X-RateLimit-Remaining', Math.max(0, 100 - requestCount));
  res.setHeader('X-RateLimit-Reset', Math.floor(resetTime / 1000));

  if (requestCount > 100) {
    return res.status(429).json({
      responseMetadata: {
        status: 'ERROR',
        errorCode: 'RATE_LIMIT_EXCEEDED',
        message: 'Příliš mnoho požadavků. Zkuste to prosím později.',
        retryAfter: Math.ceil((resetTime - Date.now()) / 1000)
      }
    });
  }

  next();
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'seznam-ads-api' });
});

/**
 * GET /api/v2/campaigns
 * Non-standard pagination with nested cursor structure
 */
app.get('/api/v2/campaigns', (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const pageSize = parseInt(req.query.pageSize) || 3;
  const cursor = req.query.cursor;

  // Complex cursor-based pagination
  let startIdx = 0;
  if (cursor) {
    const decoded = Buffer.from(cursor, 'base64').toString('utf-8');
    startIdx = parseInt(decoded.split(':')[1]) || 0;
  } else {
    startIdx = (page - 1) * pageSize;
  }

  const campaigns = CAMPAIGNS.slice(startIdx, startIdx + pageSize);
  const hasMore = startIdx + pageSize < CAMPAIGNS.length;
  const nextCursor = hasMore ? Buffer.from(`page:${startIdx + pageSize}`).toString('base64') : null;

  // Non-standard response format
  res.json({
    responseMetadata: {
      status: 'SUCCESS',
      requestId: `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      processingTime: Math.random() * 200 + 50
    },
    pagination: {
      currentPage: {
        size: campaigns.length,
        index: page
      },
      navigation: {
        hasNext: hasMore,
        nextCursor: nextCursor,
        hasPrevious: startIdx > 0,
        totalElements: CAMPAIGNS.length,
        totalPages: Math.ceil(CAMPAIGNS.length / pageSize)
      }
    },
    data: {
      campaigns: campaigns.map(c => ({
        ...c,
        _links: {
          self: `/api/v2/campaigns/${c.campaignId}`,
          ads: `/api/v2/campaigns/${c.campaignId}/ads`,
          stats: `/api/v2/campaigns/${c.campaignId}/stats`
        }
      }))
    }
  });
});

/**
 * GET /api/v2/campaigns/:id/ads
 * Must be called separately to get ad details
 */
app.get('/api/v2/campaigns/:campaignId/ads', (req, res) => {
  const { campaignId } = req.params;
  const ads = ADS[campaignId] || [];

  res.json({
    responseMetadata: {
      status: 'SUCCESS',
      requestId: `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString()
    },
    data: {
      ads: ads,
      campaignId: campaignId
    }
  });
});

/**
 * GET /api/v2/campaigns/:id/stats
 * Must be called separately to get statistics
 */
app.get('/api/v2/campaigns/:campaignId/stats', (req, res) => {
  const { campaignId } = req.params;
  const stats = STATS[campaignId] || null;

  res.json({
    responseMetadata: {
      status: 'SUCCESS',
      requestId: `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString()
    },
    data: {
      statistics: stats,
      campaignId: campaignId,
      currency: 'CZK',
      period: {
        start: '2025-10-01',
        end: '2025-11-11'
      }
    }
  });
});

app.listen(PORT, () => {
  console.log(`Seznam Ads Mock API running on port ${PORT}`);
  console.log(`Features:`);
  console.log(`  - Nested cursor pagination`);
  console.log(`  - Rate limiting (100 req/min)`);
  console.log(`  - Non-standard response format`);
  console.log(`  - Multiple endpoints for complete data`);
});
