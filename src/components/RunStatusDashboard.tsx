import React, { useState, useEffect, useCallback } from 'react';

interface RunStatus {
  run: {
    id: string;
    type: string;
    input: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    created_at: string;
    updated_at: string;
    completed_at?: string;
    current_layer: number;
    total_api_calls: number;
    stats?: any;
  };
  profiles: Array<{
    username: string;
    full_name: string;
    follower_count: number;
    layer: number;
    discovery_method: string;
    found_from: string;
  }>;
}

interface Props {
  runId: string;
  onClose: () => void;
}

export default function RunStatusDashboard({ runId, onClose }: Props) {
  const [status, setStatus] = useState<RunStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch(`/api/run-status?id=${encodeURIComponent(runId)}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch status: ${response.status}`);
      }
      const data = await response.json();
      setStatus(data);
      setError(null);
      
      // Stop auto-refresh if run is completed or failed
      if (data.run.status === 'completed' || data.run.status === 'failed') {
        setAutoRefresh(false);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [runId]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      fetchStatus();
    }, 2000); // Refresh every 2 seconds

    return () => clearInterval(interval);
  }, [autoRefresh, fetchStatus]);

  const formatTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleTimeString();
  };

  const formatDuration = (start: string, end?: string) => {
    const startTime = new Date(start);
    const endTime = end ? new Date(end) : new Date();
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
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
            <p>Loading run status...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <h3 className="text-lg font-semibold text-red-600 mb-2">Error Loading Status</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="flex gap-2">
            <button 
              onClick={fetchStatus}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Retry
            </button>
            <button 
              onClick={onClose}
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!status) return null;

  const { run, profiles } = status;
  const profilesByLayer = profiles.reduce((acc, profile) => {
    acc[profile.layer] = (acc[profile.layer] || 0) + 1;
    return acc;
  }, {} as Record<number, number>);

  const topProfiles = profiles
    .sort((a, b) => b.follower_count - a.follower_count)
    .slice(0, 10);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold">Run Status: {run.input}</h2>
            <div className="flex items-center gap-2 mt-1">
              <span className={`px-2 py-1 rounded text-sm ${getStatusColor(run.status)}`}>
                {getStatusIcon(run.status)} {run.status.toUpperCase()}
              </span>
              <span className="text-sm text-gray-500">
                ID: {run.id.slice(0, 8)}...
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <label className="flex items-center gap-2 text-sm">
              <input 
                type="checkbox" 
                checked={autoRefresh} 
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
              Auto-refresh
            </label>
            <button 
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-xl font-bold"
            >
              ×
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Overview Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded">
              <div className="text-2xl font-bold text-blue-600">{profiles.length}</div>
              <div className="text-sm text-blue-800">Total Profiles</div>
            </div>
            <div className="bg-green-50 p-4 rounded">
              <div className="text-2xl font-bold text-green-600">{run.total_api_calls}</div>
              <div className="text-sm text-green-800">API Calls</div>
            </div>
            <div className="bg-purple-50 p-4 rounded">
              <div className="text-2xl font-bold text-purple-600">{run.current_layer}</div>
              <div className="text-sm text-purple-800">Current Layer</div>
            </div>
            <div className="bg-orange-50 p-4 rounded">
              <div className="text-2xl font-bold text-orange-600">
                {formatDuration(run.created_at, run.completed_at)}
              </div>
              <div className="text-sm text-orange-800">Duration</div>
            </div>
          </div>

          {/* Run Details */}
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-3">Run Information</h3>
              <div className="space-y-2 text-sm">
                <div><span className="font-medium">Type:</span> {run.type}</div>
                <div><span className="font-medium">Input:</span> {run.input}</div>
                <div><span className="font-medium">Started:</span> {formatTime(run.created_at)}</div>
                <div><span className="font-medium">Updated:</span> {formatTime(run.updated_at)}</div>
                {run.completed_at && (
                  <div><span className="font-medium">Completed:</span> {formatTime(run.completed_at)}</div>
                )}
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-3">Discovery Breakdown</h3>
              <div className="space-y-2 text-sm">
                {Object.entries(profilesByLayer).map(([layer, count]) => (
                  <div key={layer} className="flex justify-between">
                    <span>Layer {layer}:</span>
                    <span className="font-medium">{count} profiles</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Top Profiles */}
          {topProfiles.length > 0 && (
            <div>
              <h3 className="font-semibold mb-3">Top Discovered Profiles</h3>
              <div className="bg-gray-50 rounded-lg overflow-hidden">
                <div className="max-h-64 overflow-y-auto">
                  {topProfiles.map((profile, index) => (
                    <div key={profile.username} className="flex items-center justify-between p-3 border-b border-gray-200 last:border-0">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-medium text-gray-500">#{index + 1}</span>
                        <div>
                          <div className="font-medium">@{profile.username}</div>
                          {profile.full_name && (
                            <div className="text-sm text-gray-600">{profile.full_name}</div>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">
                          {profile.follower_count.toLocaleString()} followers
                        </div>
                        <div className="text-sm text-gray-500">
                          Layer {profile.layer} • {profile.discovery_method}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 pt-4 border-t">
            <button 
              onClick={fetchStatus}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Refresh Now
            </button>
            <a 
              href={`/api/run-status?id=${encodeURIComponent(runId)}`}
              target="_blank"
              rel="noreferrer"
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              View Raw JSON
            </a>
            <button 
              onClick={onClose}
              className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
