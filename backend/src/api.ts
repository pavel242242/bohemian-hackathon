/**
 * API endpoints for Nike campaigns query system
 */

import { Router } from 'express';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);
const router = Router();

interface QueryRequest {
  query: string;
  limit?: number;
}

interface CampaignResult {
  campaign_name: string;
  source: string;
  channel: string;
  budget: string;
  impressions: number;
  start_date: string | null;
  end_date: string | null;
}

/**
 * POST /api/query
 * Execute a query against Nike campaigns data
 */
router.post('/query', async (req, res) => {
  try {
    const { query, limit = 20 } = req.body as QueryRequest;

    if (!query) {
      return res.status(400).json({
        success: false,
        error: 'Query is required',
      });
    }

    console.log(`[API] Received query: ${query}`);

    // Execute Python agent script
    const pipelinesDir = path.join(__dirname, '../../pipelines');
    const command = `cd ${pipelinesDir} && source venv/bin/activate && python agent.py "${query.replace(/"/g, '\\"')}"`;

    const { stdout, stderr } = await execAsync(command, {
      maxBuffer: 10 * 1024 * 1024, // 10MB
    });

    // Parse output for results
    const output = stdout + stderr;
    const lines = output.split('\n');

    // Extract results section
    const resultsStart = lines.findIndex(line => line.includes('RESULTS:'));
    const summaryStart = lines.findIndex(line => line.includes('SUMMARY:'));

    let campaigns: CampaignResult[] = [];
    let summary = {
      total: 0,
      sources: [] as string[],
      channels: [] as string[],
    };

    // Parse summary
    if (summaryStart > 0) {
      for (let i = summaryStart; i < lines.length; i++) {
        const line = lines[i];
        if (line.includes('Total:')) {
          const match = line.match(/(\d+) campaigns/);
          if (match) summary.total = parseInt(match[1]);
        }
        if (line.includes('Sources:')) {
          const sourcesText = line.split('Sources:')[1]?.trim();
          if (sourcesText) {
            summary.sources = sourcesText.split(',').map(s => s.trim());
          }
        }
        if (line.includes('Channels:')) {
          const channelsText = line.split('Channels:')[1]?.trim();
          if (channelsText) {
            summary.channels = channelsText.split(',').map(s => s.trim());
          }
        }
      }
    }

    return res.json({
      success: true,
      data: {
        query,
        summary,
        rawOutput: output,
      },
      timestamp: new Date().toISOString(),
    });

  } catch (error: any) {
    console.error('[API] Query error:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Failed to execute query',
      timestamp: new Date().toISOString(),
    });
  }
});

/**
 * POST /api/refresh
 * Re-run the data extraction pipeline
 */
router.post('/refresh', async (req, res) => {
  try {
    console.log('[API] Running data refresh...');

    const pipelinesDir = path.join(__dirname, '../../pipelines');
    const command = `cd ${pipelinesDir} && source venv/bin/activate && python nike_campaigns_pipeline.py`;

    const { stdout, stderr } = await execAsync(command, {
      maxBuffer: 10 * 1024 * 1024,
      timeout: 60000, // 60 seconds
    });

    const output = stdout + stderr;
    const success = output.includes('PIPELINE COMPLETE');

    return res.json({
      success,
      message: success ? 'Data refreshed successfully' : 'Pipeline completed with warnings',
      output,
      timestamp: new Date().toISOString(),
    });

  } catch (error: any) {
    console.error('[API] Refresh error:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Failed to refresh data',
      timestamp: new Date().toISOString(),
    });
  }
});

/**
 * GET /api/status
 * Check if data is available and servers are running
 */
router.get('/status', async (req, res) => {
  try {
    const fs = require('fs');
    const pipelinesDir = path.join(__dirname, '../../pipelines');
    const dbPath = path.join(pipelinesDir, 'nike_campaigns.duckdb');

    const dataAvailable = fs.existsSync(dbPath);

    // Check mock servers
    const mockServers = [
      { name: 'Meta', port: 3001 },
      { name: 'Google', port: 8000 },
      { name: 'TikTok', port: 3003 },
      { name: 'SOAP', port: 5001 },
    ];

    const serverStatus = await Promise.all(
      mockServers.map(async (server) => {
        try {
          const response = await fetch(`http://localhost:${server.port}/health`);
          return {
            name: server.name,
            port: server.port,
            status: response.ok ? 'running' : 'error',
          };
        } catch {
          return {
            name: server.name,
            port: server.port,
            status: 'offline',
          };
        }
      })
    );

    const allServersRunning = serverStatus.every(s => s.status === 'running');

    return res.json({
      success: true,
      dataAvailable,
      mockServers: serverStatus,
      ready: dataAvailable && allServersRunning,
      timestamp: new Date().toISOString(),
    });

  } catch (error: any) {
    console.error('[API] Status check error:', error);
    return res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString(),
    });
  }
});

export default router;
