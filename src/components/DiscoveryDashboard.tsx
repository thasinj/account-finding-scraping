import React, { useCallback, useMemo, useState, useEffect } from 'react';
import RunStatusDashboard from './RunStatusDashboard';

type Mode = 'combined' | 'similar';

type RunMeta = {
  id: string;
};

export default function DiscoveryDashboard() {
  const [mode, setMode] = useState<Mode>('combined');
  const [input, setInput] = useState<string>('edm');
  const [pages, setPages] = useState<number>(2);
  const [similarCount, setSimilarCount] = useState<number>(10);
  const [minFollowers, setMinFollowers] = useState<number>(10000);
  const [run, setRun] = useState<RunMeta | null>(null);
  const [running, setRunning] = useState<boolean>(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [statusUrl, setStatusUrl] = useState<string | null>(null);
  const [showStatusDashboard, setShowStatusDashboard] = useState<boolean>(false);

  const appendLog = useCallback((line: string) => {
    setLogs(prev => [...prev, line]);
  }, []);

  // Warn user before leaving during active run
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (running) {
        e.preventDefault();
        e.returnValue = 'Discovery run in progress. Leaving will stop the process but preserve found data.';
        return e.returnValue;
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [running]);

  const canStart = useMemo(() => {
    if (!input.trim()) return false;
    if (mode === 'combined' && pages <= 0) return false;
    if (similarCount <= 0) return false;
    return !running;
  }, [input, mode, pages, similarCount, running]);

  const chunk = <T,>(arr: T[], size: number): T[][] => {
    const out: T[][] = [];
    for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
    return out;
  };

  async function startRun() {
    try {
      setRunning(true);
      setLogs([]);
      appendLog('Starting run...');

      // 1) Create run
      const startRes = await fetch('/api/run-start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: mode,
          input,
          params: { pages, similarCount, minFollowers }
        })
      });
      if (!startRes.ok) throw new Error(`run-start failed: ${startRes.status}`);
      const { id } = await startRes.json();
      setRun({ id });
      const statusHref = `/api/run-status?id=${encodeURIComponent(id)}`;
      setStatusUrl(statusHref);
      appendLog(`Run created: ${id}`);

      // 2) Collect seeds and similars
      let seedUsernames: string[] = [];
      if (mode === 'combined') {
        appendLog(`Fetching hashtag seeds for #${input} (pages: ${pages})...`);
        // Fetch one page at a time via our hashtag proxy to emulate pagination
        // Our endpoint supports pagination_token, but for simplicity, call once
        const page1 = await fetch(`/api/hashtag?tag=${encodeURIComponent(input)}`);
        if (!page1.ok) throw new Error(`hashtag failed: ${page1.status}`);
        const data = await page1.json();

        // Extract usernames from posts/top_posts like the Python flow does
        const usernamesSet = new Set<string>();
        const collectFromEdges = (edges: any[]) => {
          for (const edge of edges || []) {
            const node = edge?.node;
            const caption: string | undefined = node?.accessibility_caption;
            if (typeof caption === 'string') {
              const m = caption.match(/shared by (@?[a-zA-Z0-9_.]+)|by (@?[a-zA-Z0-9_.]+)/i);
              const raw = m?.[1] || m?.[2];
              if (raw) {
                const u = raw.replace('@', '');
                if (/^[a-zA-Z0-9_.]{1,30}$/.test(u)) usernamesSet.add(u);
              }
            }
          }
        };

        if (data?.posts?.edges) collectFromEdges(data.posts.edges);
        if (data?.top_posts?.edges) collectFromEdges(data.top_posts.edges);

        seedUsernames = Array.from(usernamesSet).slice(0, 5);
        appendLog(`Seeds: ${seedUsernames.join(', ') || '(none)'}`);
      } else {
        // similar mode: use the single input as seed
        seedUsernames = [input.replace('@', '')];
      }

      // 3) Similar accounts for seeds
      const discovered = new Set<string>();
      for (const seed of seedUsernames) {
        appendLog(`Fetching similar accounts for @${seed}...`);
        const resp = await fetch(`/api/similar?username=${encodeURIComponent(seed)}`);
        if (!resp.ok) {
          appendLog(`  similar failed for @${seed} (${resp.status})`);
          continue;
        }
        const list = await resp.json();
        if (Array.isArray(list)) {
          for (const user of list.slice(0, similarCount)) {
            const u = user?.username;
            if (typeof u === 'string' && u) discovered.add(u);
          }
        }
      }

      const discoveredUsernames = Array.from(discovered);
      appendLog(`Discovered ${discoveredUsernames.length} usernames from similar.`);

      // 4) Enrich with profile details to get follower counts
      const enriched: any[] = [];
      const filtered: any[] = [];
      let processed = 0;
      for (const u of discoveredUsernames) {
        const res = await fetch(`/api/profile?username=${encodeURIComponent(u)}`);
        if (res.ok) {
          const profileJson = await res.json();
          enriched.push(profileJson);
          
          // Apply follower filter
          const followers = profileJson?.user_data?.follower_count || 0;
          if (followers >= minFollowers) {
            filtered.push(profileJson);
          }
        }
        processed += 1;
        if (processed % 10 === 0) appendLog(`Enriched ${processed}/${discoveredUsernames.length}...`);
      }
      appendLog(`Enriched ${processed} profiles. ${filtered.length} meet ${minFollowers.toLocaleString()}+ follower threshold.`);

      // 5) Ingest into DB in chunks (only profiles that meet follower threshold)
      const batches = chunk(filtered, 50);
      let totalInserted = 0;
      for (const batch of batches) {
        const ing = await fetch('/api/run-ingest', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            run_id: run?.id || id,
            layer: mode === 'combined' ? 1 : 0,
            discovered_from: mode === 'combined' ? `#${input}` : `similar:${input}`,
            discovery_method: 'similar_accounts',
            category: input, // Use input as category (e.g., 'edm', 'luxury', 'gaming')
            profiles: batch
          })
        });
        if (ing.ok) {
          const json = await ing.json();
          totalInserted += Number(json?.inserted_count || 0);
          appendLog(`Ingested batch (${json?.inserted_count || 0}). Total: ${totalInserted}`);
        }
      }

      // 6) Complete run
      await fetch('/api/run-complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, stats: { mode, input, pages, similarCount, minFollowers, totalInserted } })
      });
      appendLog('Run completed.');
    } catch (e: any) {
      appendLog(`Error: ${String(e?.message || e)}`);
      
      // Mark run as failed but preserve data collected so far
      if (run?.id) {
        try {
          await fetch('/api/run-fail', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              id: run.id, 
              error_message: String(e?.message || e),
              stats: { mode, input, pages, similarCount, minFollowers }
            })
          });
          appendLog('⚠️ Run marked as failed - data preserved up to failure point');
        } catch (failErr: any) {
          appendLog(`Failed to mark run as failed: ${failErr.message}`);
        }
      }
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="p-4 space-y-3">
      <h2 className="text-xl font-semibold">Discovery Dashboard</h2>
      <div className="flex flex-wrap gap-2 items-end">
        <label className="flex flex-col">
          <span className="text-sm">Mode</span>
          <select value={mode} onChange={e => setMode(e.target.value as Mode)} className="border rounded px-2 py-1">
            <option value="combined">Combined (Hashtag + Similar)</option>
            <option value="similar">Similar Only</option>
          </select>
        </label>
        <label className="flex flex-col">
          <span className="text-sm">Input ({mode === 'combined' ? '#hashtag' : 'username'})</span>
          <input value={input} onChange={e => setInput(e.target.value)} className="border rounded px-2 py-1" placeholder={mode === 'combined' ? 'edm' : 'edm'} />
        </label>
        {mode === 'combined' && (
          <label className="flex flex-col">
            <span className="text-sm">Hashtag pages</span>
            <input type="number" min={1} value={pages} onChange={e => setPages(Number(e.target.value))} className="border rounded px-2 py-1 w-24" />
          </label>
        )}
        <label className="flex flex-col">
          <span className="text-sm">Similar per seed</span>
          <input type="number" min={1} value={similarCount} onChange={e => setSimilarCount(Number(e.target.value))} className="border rounded px-2 py-1 w-24" />
        </label>
        <label className="flex flex-col">
          <span className="text-sm">Min followers</span>
          <input type="number" min={1000} step={1000} value={minFollowers} onChange={e => setMinFollowers(Number(e.target.value))} className="border rounded px-2 py-1 w-28" placeholder="10000" />
        </label>
        <button onClick={startRun} disabled={!canStart} className="bg-black text-white rounded px-3 py-2 disabled:opacity-50">
          {running ? 'Running…' : 'Start Run'}
        </button>
        {run && (
          <>
            <button 
              onClick={() => setShowStatusDashboard(true)} 
              className="bg-blue-600 text-white rounded px-3 py-2 hover:bg-blue-700"
            >
              View Status Dashboard
            </button>
            <a href={statusUrl || '#'} target="_blank" rel="noreferrer" className="text-blue-600 underline text-sm">
              Raw JSON
            </a>
          </>
        )}
      </div>

      <div className="bg-gray-50 border rounded p-2 max-h-64 overflow-auto text-sm whitespace-pre-wrap">
        {logs.map((l, i) => (
          <div key={i}>{l}</div>
        ))}
      </div>

      {showStatusDashboard && run && (
        <RunStatusDashboard 
          runId={run.id} 
          onClose={() => setShowStatusDashboard(false)} 
        />
      )}
    </div>
  );
}




