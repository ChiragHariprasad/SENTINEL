'use client'

import { useState, useEffect } from 'react'
import { apiV2 } from '@/lib/api-client'
import { FlaskConical, AlertTriangle, Shield, Users, FileText } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

interface ScenarioTemplate {
  id: string
  name: string
  description: string
  severity: string
}

interface Entity {
  entity_id: string
  entity_name: string
  entity_type: string
}

interface ScenarioResult {
  scenario: string
  source_entity: { entity_name: string; entity_type: string; current_risk: number }
  impact: { current_risk: number; projected_risk: number; risk_delta: number }
  blast_radius: { total_affected: number; affected_systems: number; affected_controls: number; affected_users: number }
  impacted_entities: Array<{ entity_name: string; entity_type: string }>
}

const severityColor: Record<string, string> = {
  CRITICAL: 'bg-red-100 text-red-700',
  HIGH: 'bg-orange-100 text-orange-700',
  MEDIUM: 'bg-yellow-100 text-yellow-700',
  LOW: 'bg-green-100 text-green-700',
}

const scenarioIcons: Record<string, LucideIcon> = {
  BREACH: Shield,
  FAILURE: AlertTriangle,
  CONTRACT_EXPIRY: FileText,
  CERT_EXPIRED: FileText,
  IDENTITY_COMPROMISE: Users,
  CONFIG_DRIFT: AlertTriangle,
}

export default function ScenarioSimulatorPage() {
  const [templates, setTemplates] = useState<ScenarioTemplate[]>([])
  const [entities, setEntities] = useState<Entity[]>([])
  const [selectedEntity, setSelectedEntity] = useState('')
  const [selectedScenario, setSelectedScenario] = useState('BREACH')
  const [result, setResult] = useState<ScenarioResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    apiV2.get<{ data: { templates: ScenarioTemplate[] } }>('/scenario/templates').then(r => setTemplates(r.data.templates))
    apiV2.get<{ data: { entities: Entity[] } }>('/entities?size=100').then(r => setEntities(r.data.entities))
  }, [])

  const run = async () => {
    if (!selectedEntity) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await apiV2.post<{ data: { results: ScenarioResult } }>('/scenario/run', {
        entity_id: selectedEntity,
        scenario: selectedScenario,
      })
      setResult(res.data.results)
    } catch {
      setError('Failed to run scenario simulation')
    } finally {
      setLoading(false)
    }
  }

  const Icon = scenarioIcons[selectedScenario] || FlaskConical

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <FlaskConical className="w-6 h-6 text-sentinel-600" />
          Scenario Simulator
        </h1>
        <p className="text-gray-500 mt-1">Simulate risk events and analyze blast radius</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Entity</label>
            <select value={selectedEntity} onChange={e => setSelectedEntity(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sentinel-500">
              <option value="">Select entity...</option>
              {entities.map(e => (
                <option key={e.entity_id} value={e.entity_id}>{e.entity_name} ({e.entity_type})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Scenario Type</label>
            <select value={selectedScenario} onChange={e => setSelectedScenario(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sentinel-500">
              {templates.map(t => (
                <option key={t.id} value={t.id}>{t.name} ({t.severity})</option>
              ))}
            </select>
          </div>
        </div>

        <button onClick={run} disabled={!selectedEntity || loading}
          className="w-full py-2 bg-sentinel-600 text-white rounded-lg hover:bg-sentinel-700 disabled:opacity-50 flex items-center justify-center gap-2">
          <Icon className="w-4 h-4" />
          {loading ? 'Simulating...' : 'Run Simulation'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">{error}</div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">{result.scenario}</h2>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${severityColor[result.source_entity.current_risk > 80 ? 'CRITICAL' : result.source_entity.current_risk > 60 ? 'HIGH' : 'MEDIUM']}`}>
                {result.source_entity.entity_name}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-gray-900">{result.impact.current_risk}</div>
                <div className="text-xs text-gray-500 mt-1">Current Risk</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-risk-red">{result.impact.projected_risk}</div>
                <div className="text-xs text-gray-500 mt-1">Projected Risk</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-risk-red">+{result.impact.risk_delta}</div>
                <div className="text-xs text-gray-500 mt-1">Risk Delta</div>
              </div>
            </div>

            <h3 className="text-sm font-semibold text-gray-700 mb-3">Blast Radius</h3>
            <div className="grid grid-cols-4 gap-3">
              <div className="bg-red-50 rounded-lg p-3 text-center">
                <div className="text-lg font-bold text-risk-red">{result.blast_radius.total_affected}</div>
                <div className="text-xs text-gray-500">Total Affected</div>
              </div>
              <div className="bg-orange-50 rounded-lg p-3 text-center">
                <div className="text-lg font-bold text-orange-700">{result.blast_radius.affected_systems}</div>
                <div className="text-xs text-gray-500">Systems</div>
              </div>
              <div className="bg-yellow-50 rounded-lg p-3 text-center">
                <div className="text-lg font-bold text-yellow-700">{result.blast_radius.affected_controls}</div>
                <div className="text-xs text-gray-500">Controls</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-3 text-center">
                <div className="text-lg font-bold text-blue-700">{result.blast_radius.affected_users}</div>
                <div className="text-xs text-gray-500">Users</div>
              </div>
            </div>
          </div>

          {result.impacted_entities.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Impacted Entities</h3>
              <div className="space-y-2">
                {result.impacted_entities.slice(0, 10).map((e, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-gray-600">
                    <span className="w-2 h-2 rounded-full bg-risk-red" />
                    {e.entity_name} <span className="text-gray-400">({e.entity_type})</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
