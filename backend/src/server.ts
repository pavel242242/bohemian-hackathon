import express, { Request, Response } from 'express';
import cors from 'cors';
import axios from 'axios';
import dotenv from 'dotenv';
import { ApiResponse, AdArchiveResponse, CampaignQueryParams } from './types';
import apiRoutes from './api';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;
const META_MOCK_SERVER = process.env.META_MOCK_SERVER || 'http://localhost:3001';

// Middleware
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Mount API routes
app.use('/api', apiRoutes);

// Main endpoint: Query Meta Ad Library mock server
app.get('/api/campaigns', async (req: Request, res: Response) => {
  try {
    const queryParams: CampaignQueryParams = {
      search: req.query.search as string,
      limit: req.query.limit ? parseInt(req.query.limit as string) : 10,
      offset: req.query.offset ? parseInt(req.query.offset as string) : 0,
      after: req.query.after as string,
    };

    // Remove undefined parameters
    Object.keys(queryParams).forEach(
      (key) =>
        queryParams[key as keyof CampaignQueryParams] === undefined &&
        delete queryParams[key as keyof CampaignQueryParams]
    );

    console.log(
      `[${new Date().toISOString()}] Querying Meta mock server with params:`,
      queryParams
    );

    // Query the Meta Ad Library mock server
    const response = await axios.get<AdArchiveResponse>(
      `${META_MOCK_SERVER}/ads_archive`,
      {
        params: queryParams,
        timeout: 5000,
      }
    );

    const apiResponse: ApiResponse<AdArchiveResponse> = {
      success: true,
      data: response.data,
      timestamp: new Date().toISOString(),
    };

    res.json(apiResponse);
  } catch (error) {
    console.error('Error querying Meta mock server:', error);

    if (axios.isAxiosError(error)) {
      const apiResponse: ApiResponse<null> = {
        success: false,
        error: error.message || 'Failed to query Meta Ad Library',
        timestamp: new Date().toISOString(),
      };
      res.status(error.response?.status || 500).json(apiResponse);
    } else {
      const apiResponse: ApiResponse<null> = {
        success: false,
        error: 'Internal server error',
        timestamp: new Date().toISOString(),
      };
      res.status(500).json(apiResponse);
    }
  }
});

// Proxy endpoint for direct ads_archive queries
app.get('/api/ads_archive', async (req: Request, res: Response) => {
  try {
    console.log(
      `[${new Date().toISOString()}] Direct ads_archive query with params:`,
      req.query
    );

    const response = await axios.get<AdArchiveResponse>(
      `${META_MOCK_SERVER}/ads_archive`,
      {
        params: req.query,
        timeout: 5000,
      }
    );

    const apiResponse: ApiResponse<AdArchiveResponse> = {
      success: true,
      data: response.data,
      timestamp: new Date().toISOString(),
    };

    res.json(apiResponse);
  } catch (error) {
    console.error('Error in direct ads_archive query:', error);

    if (axios.isAxiosError(error)) {
      const apiResponse: ApiResponse<null> = {
        success: false,
        error: error.message || 'Failed to query ads archive',
        timestamp: new Date().toISOString(),
      };
      res.status(error.response?.status || 500).json(apiResponse);
    } else {
      const apiResponse: ApiResponse<null> = {
        success: false,
        error: 'Internal server error',
        timestamp: new Date().toISOString(),
      };
      res.status(500).json(apiResponse);
    }
  }
});

// Error handling middleware
app.use((err: any, req: Request, res: Response, next: any) => {
  console.error('Unhandled error:', err);
  const apiResponse: ApiResponse<null> = {
    success: false,
    error: 'Internal server error',
    timestamp: new Date().toISOString(),
  };
  res.status(500).json(apiResponse);
});

// 404 handler
app.use((req: Request, res: Response) => {
  const apiResponse: ApiResponse<null> = {
    success: false,
    error: 'Not found',
    timestamp: new Date().toISOString(),
  };
  res.status(404).json(apiResponse);
});

// Start server
app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════╗
║  STAGEHAND Backend Server                  ║
║  Server running on http://localhost:${PORT}  ║
║  Meta Mock at: ${META_MOCK_SERVER}         ║
║  Ready to query /api/campaigns             ║
╚════════════════════════════════════════════╝
  `);
});

export default app;
