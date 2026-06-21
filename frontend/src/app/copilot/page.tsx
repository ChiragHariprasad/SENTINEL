'use client'

import { useState } from 'react'
import { api } from '@/lib/api-client'
import { Send, Bot, User, Sparkles } from 'lucide-react'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const suggestions = [
  'Which vendors access PII?',
  'Show critical vendors',
  'Which certifications are expired?',
  'How many vendors are there?',
  'Which vendors have been breached?',
]

export default function CopilotPage() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hi! I can answer questions about your vendors, risk, certifications, and more. Try asking something like "Which vendors access PII?" or "Show critical vendors."' },
  ])
  const [loading, setLoading] = useState(false)

  const ask = async (q: string) => {
    if (!q.trim() || loading) return
    setMessages(prev => [...prev, { role: 'user', content: q }])
    setQuestion('')
    setLoading(true)

    try {
      const res = await api.post<{ data: { answer: string } }>('/copilot/query', { question: q })
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.answer }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try rephrasing your question.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Bot className="w-6 h-6 text-sentinel-600" />
          AI Copilot
        </h1>
        <p className="text-gray-500 mt-1">Ask questions about your vendor risk posture</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-4 h-[500px] flex flex-col">
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : ''}`}>
              {m.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-sentinel-100 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-sentinel-600" />
                </div>
              )}
              <div className={`max-w-[80%] p-3 rounded-lg text-sm ${
                m.role === 'user'
                  ? 'bg-sentinel-600 text-white'
                  : 'bg-gray-50 text-gray-700 border border-gray-200'
              }`}>
                <pre className="whitespace-pre-wrap font-sans">{m.content}</pre>
              </div>
              {m.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-gray-600" />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-sentinel-100 flex items-center justify-center">
                <Bot className="w-4 h-4 text-sentinel-600" />
              </div>
              <div className="p-3 rounded-lg bg-gray-50 border border-gray-200">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="space-y-2">
          {messages.length === 1 && (
            <div className="flex flex-wrap gap-2">
              {suggestions.map(s => (
                <button key={s} onClick={() => ask(s)}
                  className="flex items-center gap-1 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-full text-xs text-gray-600 hover:bg-gray-100">
                  <Sparkles className="w-3 h-3" /> {s}
                </button>
              ))}
            </div>
          )}
          <div className="flex gap-2">
            <input
              type="text"
              value={question}
              onChange={e => setQuestion(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && ask(question)}
              placeholder="Ask a question..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sentinel-500"
              disabled={loading}
            />
            <button onClick={() => ask(question)} disabled={loading || !question.trim()}
              className="px-4 py-2 bg-sentinel-600 text-white rounded-lg hover:bg-sentinel-700 disabled:opacity-50">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
