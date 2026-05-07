'use client';

import { useState } from 'react';
import { searchResearch, listResearchSearchResults, convertSearchResultToCandidate, rejectResearchSearchResult, SearchIntent } from '@/lib/api';

export default function ResearchSearchPage() {
  const [query, setQuery] = useState('');
  const [intent, setIntent] = useState<string>('GENERAL_RESEARCH');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string>('');
  const [storedCount, setStoredCount] = useState(0);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setStatus('');
    try {
      const response = await searchResearch({ query, intent: intent as SearchIntent, max_results: 10 });
      setResults(response.results || []);
      setStoredCount(response.stored_count || 0);
      const providerStatus = response.provider_statuses?.map((p: any) => `${p.provider}:${p.status}`).join(', ') || 'none';
      setStatus(`Provider statuses: ${providerStatus} | Stored: ${response.stored_count}/${response.result_count}`);
    } catch (err: any) {
      setStatus(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleConvert = async (resultId: string, candidateType: string) => {
    try {
      await convertSearchResultToCandidate({ search_result_id: resultId, candidate_type: candidateType as any });
      setResults(prev => prev.map(r => r.id === resultId ? { ...r, conversion_status: 'CONVERTED_TO_CANDIDATE' } : r));
      setStatus('Converted to candidate - pending manual review.');
    } catch (err: any) {
      setStatus(`Error: ${err.message}`);
    }
  };

  const handleReject = async (resultId: string, reason: string) => {
    try {
      await rejectResearchSearchResult(resultId, reason);
      setResults(prev => prev.map(r => r.id === resultId ? { ...r, conversion_status: 'REJECTED' } : r));
      setStatus('Result rejected.');
    } catch (err: any) {
      setStatus(`Error: ${err.message}`);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px' }}>
      <div style={{ background: '#fef3cd', border: '1px solid #ffc107', borderRadius: '8px', padding: '12px 16px', marginBottom: '20px', fontSize: '14px' }}>
        <strong>Discovery Only — Not Verified Evidence</strong><br />
        Search results are discovery artifacts. They are <em>not</em> verified evidence and cannot make a product READY_FOR_SAMPLE.
        Convert results to candidates and verify before any readiness decision.
      </div>

      <h1 style={{ fontSize: '24px', marginBottom: '20px' }}>Research Search Broker</h1>

      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search query (e.g. door hinge pin removal tool sold)"
          style={{ flex: 1, minWidth: '300px', padding: '10px', fontSize: '16px', border: '1px solid #ccc', borderRadius: '6px' }}
          onKeyDown={e => e.key === 'Enter' && handleSearch()}
        />
        <select value={intent} onChange={e => setIntent(e.target.value)} style={{ padding: '10px', fontSize: '16px' }}>
          <option value="GENERAL_RESEARCH">General Research</option>
          <option value="SOLD_EVIDENCE">Sold Evidence</option>
          <option value="ACTIVE_LISTING">Active Listing</option>
          <option value="SUPPLIER">Supplier</option>
          <option value="COMPETITOR">Competitor</option>
          <option value="COMPLAINT_RESEARCH">Complaint Research</option>
          <option value="KEYWORD_DEMAND">Keyword Demand</option>
        </select>
        <button onClick={handleSearch} disabled={loading} style={{ padding: '10px 24px', fontSize: '16px', cursor: 'pointer' }}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {status && (
        <div style={{ padding: '10px', background: '#f8f9fa', border: '1px solid #dee2e6', borderRadius: '6px', marginBottom: '16px', fontSize: '14px', fontFamily: 'monospace' }}>
          {status}
        </div>
      )}

      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
        <thead>
          <tr style={{ background: '#f8f9fa', textAlign: 'left' }}>
            <th style={{ padding: '10px', borderBottom: '2px solid #dee2e6' }}>Title</th>
            <th style={{ padding: '10px', borderBottom: '2px solid #dee2e6' }}>Domain</th>
            <th style={{ padding: '10px', borderBottom: '2px solid #dee2e6' }}>Provider</th>
            <th style={{ padding: '10px', borderBottom: '2px solid #dee2e6' }}>Intent</th>
            <th style={{ padding: '10px', borderBottom: '2px solid #dee2e6' }}>Status</th>
            <th style={{ padding: '10px', borderBottom: '2px solid #dee2e6' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r: any) => (
            <tr key={r.id} style={{ borderBottom: '1px solid #dee2e6' }}>
              <td style={{ padding: '10px', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                <a href={r.url} target="_blank" rel="noopener noreferrer" title={r.title}>{r.title || r.url}</a>
              </td>
              <td style={{ padding: '10px', color: '#666' }}>{r.source_domain}</td>
              <td style={{ padding: '10px' }}>{r.provider}</td>
              <td style={{ padding: '10px' }}>{r.intent}</td>
              <td style={{ padding: '10px' }}>
                <span style={{
                  padding: '2px 8px', borderRadius: '4px', fontSize: '12px',
                  background: r.conversion_status === 'CONVERTED_TO_CANDIDATE' ? '#d4edda' :
                    r.conversion_status === 'REJECTED' ? '#f8d7da' : '#fff3cd',
                  color: r.conversion_status === 'CONVERTED_TO_CANDIDATE' ? '#155724' :
                    r.conversion_status === 'REJECTED' ? '#721c24' : '#856404',
                }}>
                  {r.conversion_status || 'NOT_CONVERTED'}
                </span>
              </td>
              <td style={{ padding: '10px', display: 'flex', gap: '6px' }}>
                {r.conversion_status === 'NOT_CONVERTED' && (
                  <>
                    <button onClick={() => handleConvert(r.id, 'SOLD_LISTING')} title="Convert to sold evidence candidate" style={{ padding: '4px 8px', fontSize: '12px', cursor: 'pointer' }}>Sold</button>
                    <button onClick={() => handleConvert(r.id, 'ACTIVE_LISTING')} title="Convert to active listing candidate" style={{ padding: '4px 8px', fontSize: '12px', cursor: 'pointer' }}>Active</button>
                    <button onClick={() => handleConvert(r.id, 'COMPETITOR_LISTING')} title="Convert to competitor candidate" style={{ padding: '4px 8px', fontSize: '12px', cursor: 'pointer' }}>Competitor</button>
                    <button onClick={() => handleReject(r.id, 'Not relevant')} title="Reject result" style={{ padding: '4px 8px', fontSize: '12px', cursor: 'pointer', background: '#fff3cd' }}>Reject</button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {!loading && results.length === 0 && (
        <p style={{ color: '#666', marginTop: '20px' }}>
          No results yet. Enter a query above to search via local SearXNG/OpenSERP providers.
          Results are stored in ResellOS for later conversion to evidence candidates.
        </p>
      )}
    </div>
  );
}