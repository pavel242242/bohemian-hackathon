const API_BASE_URL = 'http://localhost:4000';

export interface QueryResponse {
	success: boolean;
	data?: {
		query: string;
		summary: {
			total: number;
			sources: string[];
			channels: string[];
		};
		rawOutput: string;
	};
	error?: string;
	timestamp: string;
}

export interface RefreshResponse {
	success: boolean;
	message?: string;
	output?: string;
	error?: string;
	timestamp: string;
}

export interface StatusResponse {
	success: boolean;
	dataAvailable: boolean;
	mockServers: {
		name: string;
		port: number;
		status: 'running' | 'offline' | 'error';
	}[];
	ready: boolean;
	error?: string;
	timestamp: string;
}

/**
 * Query Nike campaigns data
 */
export async function queryNikeCampaigns(query: string): Promise<QueryResponse> {
	const response = await fetch(`${API_BASE_URL}/api/query`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ query })
	});

	if (!response.ok) {
		throw new Error(`API error: ${response.status} ${response.statusText}`);
	}

	return response.json();
}

/**
 * Refresh data by re-running the pipeline
 */
export async function refreshData(): Promise<RefreshResponse> {
	const response = await fetch(`${API_BASE_URL}/api/refresh`, {
		method: 'POST'
	});

	if (!response.ok) {
		throw new Error(`API error: ${response.status} ${response.statusText}`);
	}

	return response.json();
}

/**
 * Get system status
 */
export async function getStatus(): Promise<StatusResponse> {
	const response = await fetch(`${API_BASE_URL}/api/status`);

	if (!response.ok) {
		throw new Error(`API error: ${response.status} ${response.statusText}`);
	}

	return response.json();
}
