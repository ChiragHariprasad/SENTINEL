import React, { useState, useRef, useEffect } from 'react';
import { Bot, User, Send, FileText, Loader, Zap } from 'lucide-react';
import { copilotApi } from '../api';

export default function Copilot() {
  const [messages, setMessages] = useState([
    { id: 1, sender: 'bot', text: 'Hello! I am SENTINEL AI Copilot. I can help you analyze vendor risk, parse contracts, or generate compliance reports. How can I assist you today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = { id: Date.now(), sender: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // API integration
      // const res = await copilotApi.query(userMsg.text);
      // const botMsg = { id: Date.now() + 1, sender: 'bot', text: res.data.answer };
      
      // Simulate API delay for mockup
      setTimeout(() => {
        const botMsg = { 
          id: Date.now() + 1, 
          sender: 'bot', 
          text: `Based on current telemetry, the most critical risk is an expired SOC2 certification for "Acme Cloud Services". I recommend initiating a vendor assessment workflow immediately. Would you like me to generate a detailed risk report?`
        };
        setMessages(prev => [...prev, botMsg]);
        setLoading(false);
      }, 1500);

    } catch (error) {
      const errorMsg = { id: Date.now() + 1, sender: 'bot', text: 'Sorry, I encountered an error while processing your request.' };
      setMessages(prev => [...prev, errorMsg]);
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="copilot-container h-[calc(100vh-140px)] flex flex-col">
      <div className="page-header mb-4 shrink-0">
        <h1 className="text-2xl font-bold text-main flex items-center gap-2">
          <Bot className="text-[var(--accent)]" />
          AI Risk Copilot
        </h1>
        <p className="text-muted text-sm mt-1">Generative AI assistant for vendor intelligence and decision support.</p>
      </div>

      <div className="card flex-1 flex flex-col overflow-hidden p-0 border border-[var(--accent)] shadow-[var(--shadow-glow)]">
        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6 bg-[rgba(21,28,44,0.4)]">
          {messages.map(msg => (
            <div key={msg.id} className={`flex gap-4 max-w-[80%] ${msg.sender === 'user' ? 'ml-auto flex-row-reverse' : ''}`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${msg.sender === 'user' ? 'bg-[var(--primary)] text-white' : 'bg-[var(--accent)] text-white'}`}>
                {msg.sender === 'user' ? <User size={20} /> : <Bot size={20} />}
              </div>
              <div className={`p-4 rounded-lg ${msg.sender === 'user' ? 'bg-[var(--primary)] text-white' : 'bg-[var(--bg-surface-hover)] border border-[var(--border)] text-main'}`}>
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.text}</p>
                {msg.sender === 'bot' && msg.id > 1 && (
                  <div className="mt-3 pt-3 border-t border-[rgba(255,255,255,0.1)] flex gap-2">
                    <button className="btn btn-ghost text-xs px-2 py-1"><FileText size={14}/> Generate Report</button>
                    <button className="btn btn-ghost text-xs px-2 py-1"><Zap size={14}/> Take Action</button>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-4 max-w-[80%]">
              <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 bg-[var(--accent)] text-white">
                <Bot size={20} />
              </div>
              <div className="p-4 rounded-lg bg-[var(--bg-surface-hover)] border border-[var(--border)] flex items-center gap-2 text-muted">
                <Loader className="animate-spin" size={16} /> Analyzing repository data...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-[var(--bg-surface)] border-t border-[var(--border)] shrink-0">
          <div className="relative">
            <textarea
              className="form-input w-full pr-12 resize-none bg-[rgba(0,0,0,0.2)] focus:bg-[rgba(0,0,0,0.4)] transition-colors"
              rows={2}
              placeholder="Ask about a vendor, contract risk, or compliance status..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
            />
            <button 
              className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-2 rounded-full transition-colors ${input.trim() ? 'bg-[var(--accent)] text-white hover:bg-[#7c3aed]' : 'text-muted bg-transparent cursor-not-allowed'}`}
              onClick={handleSend}
              disabled={!input.trim() || loading}
            >
              <Send size={18} className={input.trim() ? 'translate-x-[1px] translate-y-[1px]' : ''} />
            </button>
          </div>
          <div className="flex gap-2 mt-3 text-xs text-muted">
            <span>Suggestions:</span>
            <button className="hover:text-[var(--primary)] transition-colors" onClick={() => setInput("Which vendors have expired SOC2 certifications?")}>"Which vendors have expired SOC2?"</button>
            <span className="opacity-50">|</span>
            <button className="hover:text-[var(--primary)] transition-colors" onClick={() => setInput("Summarize Acme Cloud's recent anomaly alerts.")}>"Summarize Acme Cloud's recent anomaly alerts."</button>
          </div>
        </div>
      </div>
    </div>
  );
}
