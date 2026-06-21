'use client'

import { useState } from 'react'
import { apiV2 } from '@/lib/api-client'
import { Search, ExternalLink } from 'lucide-react'

interface GraphNode {
  id: string
  label: string
  type: string
  risk_score: number | null
}

interface GraphEdge {
  source: string
  target: string
  relationship: string
  weight: number
}

export default function GraphPage() {
  const [entityId, setEntityId] = useState('')
  const [nodes, setNodes] = useState<GraphNode[]>([])
  const [edges, setEdges] = useState<GraphEdge[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [expanded, setExpanded] = useState<string | null>(null)

  const loadGraph = async (eid: string) => {
    setLoading(true)
    setError('')
    try {
      const res = await apiV2.get<{ data: { nodes: GraphNode[]; edges: GraphEdge[] } }>(`/graph/entity/${eid}`)
      setNodes(res.data.nodes)
      setEdges(res.data.edges)
    } catch {
      setError('Failed to load graph')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    if (!entityId.trim()) return
    loadGraph(entityId.trim())
  }

  const getRiskColor = (score: number | null) => {
    if (score === null) return 'bg-gray-400'
    if (score > 80) return 'bg-risk-red'
    if (score > 60) return 'bg-orange-400'
    if (score > 40) return 'bg-yellow-400'
    return 'bg-green-400'
  }

  const edgesBySource = edges.reduce<Record<string, GraphEdge[]>>((acc, e) => {
    if (!acc[e.source]) acc[e.source] = []
    acc[e.source].push(e)
    return acc
  }, {})

  const edgesByTarget = edges.reduce<Record<string, GraphEdge[]>>((acc, e) => {
    if (!acc[e.target]) acc[e.target] = []
    acc[e.target].push(e)
    return acc
  }, {})

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <ExternalLink className="w-6 h-6 text-sentinel-600" />
          Risk Graph
        </h1>
        <p className="text-gray-500 mt-1">Visualize entity relationships and risk propagation</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex gap-2">
          <input type="text" value={entityId} onChange={e => setEntityId(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="Enter entity ID to explore..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sentinel-500 text-sm"
          />
          <button onClick={handleSearch} disabled={loading || !entityId.trim()}
            className="px-4 py-2 bg-sentinel-600 text-white rounded-lg hover:bg-sentinel-700 disabled:opacity-50 flex items-center gap-2">
            <Search className="w-4 h-4" /> Explore
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">{error}</div>
      )}

      {loading && (
        <div className="text-center py-12 text-gray-500">Loading graph...</div>
      )}

      {!loading && nodes.length > 0 && (
        <div className="grid grid-cols-1 gap-4">
          {nodes.map(node => {
            const outEdges = edgesBySource[node.id] || []
            const inEdges = edgesByTarget[node.id] || []
            const isExpanded = expanded === node.id

            return (
              <div key={node.id} className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="flex items-center gap-3 cursor-pointer" onClick={() => setExpanded(isExpanded ? null : node.id)}>
                  <span className={`w-3 h-3 rounded-full ${getRiskColor(node.risk_score)}`} />
                  <div className="flex-1">
                  <span className="font-medium text-gray-900">{node.label}</span>
                  <span className="text-xs text-gray-400 ml-2">{node.type}</span>
                  </div>
                  <span className={`text-sm font-medium ${node.risk_score && node.risk_score > 60 ? 'text-risk-red' : 'text-gray-500'}`}>
                    {node.risk_score ?? 'N/A'}
                  </span>
                </div>

                {isExpanded && (
                  <div className="mt-3 pl-6 space-y-2 border-t border-gray-100 pt-3">
                    {inEdges.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-gray-500 mb-1">Incoming</p>
                        {inEdges.map((e, i) => {
                          const src = nodes.find(n => n.id === e.source)
                          return (
                            <div key={i} className="text-xs text-gray-600">
                              ← {src?.label || e.source} <span className="text-gray-400">({e.relationship}, w={e.weight})</span>
                            </div>
                          )
                        })}
                      </div>
                    )}
                    {outEdges.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-gray-500 mb-1">Outgoing</p>
                        {outEdges.map((e, i) => {
                          const tgt = nodes.find(n => n.id === e.target)
                          return (
                            <div key={i} className="text-xs text-gray-600">
                              → {tgt?.label || e.target} <span className="text-gray-400">({e.relationship}, w={e.weight})</span>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}

          <div className="bg-gray-50 rounded-xl p-4 text-center text-sm text-gray-500">
            {nodes.length} nodes · {edges.length} edges
          </div>
        </div>
      )}

      {!loading && nodes.length === 0 && !error && (
        <div className="text-center py-12 text-gray-400">
          Enter an entity ID and click Explore to visualize the risk graph
        </div>
      )}
    </div>
  )
}
