<script lang="ts">
	import { queryNikeCampaigns, refreshData, getStatus, type StatusResponse } from '$lib/api';
	import { onMount } from 'svelte';

	let query = 'Show me the top 20 Nike campaigns';
	let loading = false;
	let refreshing = false;
	let resultOutput = '';
	let summary = { total: 0, sources: [] as string[], channels: [] as string[] };
	let logs: string[] = [];
	let status: StatusResponse | null = null;

	onMount(async () => {
		await loadStatus();
	});

	async function loadStatus() {
		try {
			status = await getStatus();
			if (!status.ready && status.dataAvailable === false) {
				addLog('⚠️ No data available. Click "Refresh Data" to run the pipeline.');
			} else if (!status.ready) {
				addLog('⚠️ Some mock servers are offline. Check status above.');
			}
		} catch (error) {
			const errorMessage = error instanceof Error ? error.message : String(error);
			addLog(`Status check error: ${errorMessage}`);
		}
	}

	async function handleSubmit() {
		loading = true;
		logs = [];
		resultOutput = '';

		try {
			addLog('🔍 Querying Nike campaigns...');
			const response = await queryNikeCampaigns(query);

			if (response.success && response.data) {
				addLog('✅ Query successful!');
				resultOutput = response.data.rawOutput;
				summary = response.data.summary;
				addLog(`📊 Found ${summary.total} campaigns`);
				addLog(`📍 Sources: ${summary.sources.join(', ')}`);
				addLog(`📺 Channels: ${summary.channels.join(', ')}`);
			} else {
				addLog(`❌ Error: ${response.error || 'Unknown error'}`);
			}
		} catch (error) {
			const errorMessage = error instanceof Error ? error.message : String(error);
			addLog(`❌ Error: ${errorMessage}`);
		} finally {
			loading = false;
		}
	}

	async function handleRefresh() {
		refreshing = true;
		logs = [];

		try {
			addLog('🔄 Running data pipeline...');
			addLog('This may take a few moments...');
			const response = await refreshData();

			if (response.success) {
				addLog('✅ ' + (response.message || 'Data refreshed successfully'));
				if (response.output) {
					const outputLines = response.output.split('\n').filter(line => line.trim());
					outputLines.forEach(line => addLog(line));
				}
				await loadStatus();
			} else {
				addLog(`❌ Error: ${response.error || 'Unknown error'}`);
			}
		} catch (error) {
			const errorMessage = error instanceof Error ? error.message : String(error);
			addLog(`❌ Error: ${errorMessage}`);
		} finally {
			refreshing = false;
		}
	}

	function addLog(message: string) {
		const timestamp = new Date().toLocaleTimeString();
		logs = [...logs, `[${timestamp}] ${message}`];
	}
</script>

<div class="space-y-6">
	<!-- Status Bar -->
	{#if status}
		<div class="bg-white rounded-lg shadow p-4">
			<div class="flex items-center justify-between">
				<div class="flex items-center space-x-4">
					<div class="flex items-center">
						<span class="text-sm font-medium text-gray-700 mr-2">System Status:</span>
						{#if status.ready}
							<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
								Ready
							</span>
						{:else}
							<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
								Not Ready
							</span>
						{/if}
					</div>
					<div class="flex items-center space-x-2">
						{#each status.mockServers as server}
							<span
								class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium {server.status === 'running'
									? 'bg-green-100 text-green-800'
									: 'bg-red-100 text-red-800'}"
								title="{server.name} - Port {server.port}"
							>
								{server.name}
							</span>
						{/each}
					</div>
				</div>
				<button
					on:click={handleRefresh}
					disabled={refreshing}
					class="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white text-sm font-semibold py-2 px-4 rounded-md transition-colors"
				>
					{refreshing ? 'Refreshing...' : 'Refresh Data'}
				</button>
			</div>
		</div>
	{/if}

	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Left side: Query input -->
		<div class="lg:col-span-1">
			<div class="bg-white rounded-lg shadow p-6">
				<h2 class="text-lg font-semibold text-gray-900 mb-4">Query</h2>
				<textarea
					bind:value={query}
					disabled={loading || refreshing}
					rows="6"
					class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
					placeholder="Ask about Nike campaigns..."
				/>
				<button
					on:click={handleSubmit}
					disabled={loading || refreshing}
					class="mt-4 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold py-2 px-4 rounded-md transition-colors"
				>
					{loading ? 'Querying...' : 'Submit Query'}
				</button>

				{#if summary.total > 0}
					<div class="mt-4 p-3 bg-gray-50 rounded-md">
						<div class="text-xs text-gray-600">
							<div class="font-semibold mb-1">Summary:</div>
							<div>Total: {summary.total} campaigns</div>
							<div>Sources: {summary.sources.join(', ')}</div>
							<div>Channels: {summary.channels.join(', ')}</div>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Right side: Results and Logs -->
		<div class="lg:col-span-2 space-y-6">
			<!-- Results Section -->
			<div class="bg-white rounded-lg shadow p-6">
				<h2 class="text-lg font-semibold text-gray-900 mb-4">Results</h2>
				{#if !resultOutput}
					<p class="text-gray-500 py-8 text-center">
						No results yet. Submit a query to see Nike campaigns.
					</p>
				{:else}
					<div class="bg-gray-900 rounded text-gray-100 p-4 font-mono text-xs overflow-x-auto">
						<pre class="whitespace-pre">{resultOutput}</pre>
					</div>
				{/if}
			</div>

			<!-- Logs Section -->
			<div class="bg-white rounded-lg shadow p-6">
				<h2 class="text-lg font-semibold text-gray-900 mb-4">Logs</h2>
				<div
					class="bg-gray-900 rounded text-gray-100 p-4 font-mono text-xs max-h-64 overflow-y-auto"
				>
					{#if logs.length === 0}
						<p class="text-gray-500">No logs yet...</p>
					{:else}
						{#each logs as log}
							<div>{log}</div>
						{/each}
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>
