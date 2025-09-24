import React, { useState, useEffect } from 'react';
import RunStatusDashboard from './RunStatusDashboard';

interface RunSummary {
  id: string;
  type: string;
  input: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
  completed_at?: string;
  total_api_calls: number;
  profile_count: number;
  stats?: {
    totalInserted?: number;
    minFollowers?: number;
  };
}

export default function RunsHistory() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

  useEffect(() => {
    fetchRuns();
  }, []);

  const fetchRuns = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/runs-list');
      if (!response.ok) {
        throw new Error(`Failed to fetch runs: ${response.status}`);
      }
      const data = await response.json();
      setRuns(data.runs || []);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleString();
  };

  const formatDuration = (start: string, end?: string) => {
    if (!end) return 'Running...';
    const startTime = new Date(start);
    const endTime = new Date(end);
    const diff = Math.floor((endTime.getTime() - startTime.getTime()) / 1000);
    
    if (diff < 60) return `${diff}s`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ${diff % 60}s`;
    return `${Math.floor(diff / 3600)}h ${Math.floor((diff % 3600) / 60)}m`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-50';
      case 'running': return 'text-blue-600 bg-blue-50';
      case 'failed': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'running': return '🔄';
      case 'failed': return '❌';
      default: return '⏳';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Loading runs history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-red-600 mb-2">Error Loading Runs</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={fetchRuns}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Discovery Runs History</h2>
        <button 
          onClick={fetchRuns}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Refresh
        </button>
      </div>

      {runs.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg mb-2">No discovery runs yet</p>
          <p>Start your first discovery run to see it here!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {runs.map((run) => (
            <div key={run.id} className="border rounded-lg p-4 hover:bg-gray-50">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`px-2 py-1 rounded text-sm ${getStatusColor(run.status)}`}>
                      {getStatusIcon(run.status)} {run.status.toUpperCase()}
                    </span>
                    <span className="font-medium text-lg">{run.input}</span>
                    <span className="text-sm bg-gray-100 px-2 py-1 rounded">{run.type}</span>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                    <div>
                      <span className="font-medium">Profiles:</span> {run.profile_count.toLocaleString()}
                    </div>
                    <div>
                      <span className="font-medium">API Calls:</span> {run.total_api_calls.toLocaleString()}
                    </div>
                    <div>
                      <span className="font-medium">Duration:</span> {formatDuration(run.created_at, run.completed_at)}
                    </div>
                    <div>
                      <span className="font-medium">Started:</span> {formatTime(run.created_at)}
                    </div>
                  </div>

                  {run.stats && (
                    <div className="mt-2 text-sm text-gray-500">
                      {run.stats.minFollowers && (
                        <span>Min followers: {run.stats.minFollowers.toLocaleString()}</span>
                      )}
                      {run.stats.totalInserted && (
                        <span className="ml-4">Saved: {run.stats.totalInserted}</span>
                      )}
                    </div>
                  )}
                </div>

                <div className="flex gap-2 ml-4">
                  <button 
                    onClick={() => setSelectedRunId(run.id)}
                    className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                  >
                    View Details
                  </button>
                  <a 
                    href={`/api/run-status?id=${encodeURIComponent(run.id)}`}
                    target="_blank"
                    rel="noreferrer"
                    className="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600"
                  >
                    JSON
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedRunId && (
        <RunStatusDashboard 
          runId={selectedRunId} 
          onClose={() => setSelectedRunId(null)} 
        />
      )}
    </div>
  );
}
