import React from 'react';
import { X, Sparkles, Cpu, Key, Server, Check, Globe, Thermometer, ChevronDown } from 'lucide-react';

const PROVIDERS = [
  { id: 'heuristic', name: 'Heuristique', desc: '100% Hors-ligne, instantané', badge: 'Recommandé', badgeColor: 'bg-emerald-500/15 text-emerald-400', needsKey: false, needsModel: false, needsUrl: false },
  { id: 'ollama', name: 'Ollama Local', desc: 'Modèles locaux privés & gratuits', badge: 'Privé', badgeColor: 'bg-amber-500/15 text-amber-400', needsKey: false, needsModel: true, needsUrl: true, defaultModel: 'llama3', models: ['llama3', 'llama3.1', 'mistral', 'qwen2.5', 'codellama', 'gemma2', 'phi3', 'deepseek-coder-v2'] },
  { id: 'gemini', name: 'Google Gemini', desc: 'Haute fidélité via Google AI', badge: 'Cloud', badgeColor: 'bg-blue-500/15 text-blue-400', needsKey: true, needsModel: true, needsUrl: false, defaultModel: 'gemini-2.5-flash', models: ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash'] },
  { id: 'openai', name: 'OpenAI / ChatGPT', desc: 'GPT-4o et modèles OpenAI', badge: 'Cloud', badgeColor: 'bg-purple-500/15 text-purple-400', needsKey: true, needsModel: true, needsUrl: false, defaultModel: 'gpt-4o-mini', models: ['gpt-4o-mini', 'gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'] },
  { id: 'groq', name: 'Groq', desc: 'Inférence ultra-rapide (LPU)', badge: 'Cloud', badgeColor: 'bg-orange-500/15 text-orange-400', needsKey: true, needsModel: true, needsUrl: false, defaultModel: 'openai/gpt-oss-120b', models: ['openai/gpt-oss-120b', 'llama-3.1-70b-versatile', 'llama-3.1-8b-instant', 'mixtral-8x7b-32768', 'gemma2-9b-it'] },
  { id: 'deepseek', name: 'DeepSeek', desc: 'Modèles de raisonnement avancé', badge: 'Cloud', badgeColor: 'bg-cyan-500/15 text-cyan-400', needsKey: true, needsModel: true, needsUrl: false, defaultModel: 'deepseek-chat', models: ['deepseek-chat', 'deepseek-reasoner'] },
];

export default function AISettingsModal({ isOpen, onClose, settings, onSave }) {
  const [formData, setFormData] = React.useState({ ...settings });

  React.useEffect(() => { setFormData({ ...settings }); }, [settings]);

  if (!isOpen) return null;

  const selectedProvider = PROVIDERS.find(p => p.id === formData.provider) || PROVIDERS[0];

  const handleProviderSelect = (provId) => {
    const prov = PROVIDERS.find(p => p.id === provId);
    setFormData({
      ...formData,
      provider: provId,
      modelName: '',
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
    onClose();
  };

  return (
    <div className="modal-overlay">
      <div className="modal-container max-w-xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-surface-100 to-surface-200 text-white px-6 py-5 flex items-center justify-between border-b border-white/[0.06] shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 bg-gradient-brand rounded-xl flex items-center justify-center shadow-glow-sm">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <h2 className="font-display font-bold text-base">Configuration IA</h2>
              <p className="text-[11px] text-slate-500">Fournisseur, modèle et paramètres d'inférence</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-white rounded-lg p-1.5 hover:bg-white/[0.06] transition-smooth">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Provider Grid */}
          <div>
            <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-3">Fournisseur</label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {PROVIDERS.map((prov) => (
                <div
                  key={prov.id}
                  onClick={() => handleProviderSelect(prov.id)}
                  className={`cursor-pointer rounded-xl p-3 border-2 transition-smooth ${
                    formData.provider === prov.id
                      ? 'border-brand-500 bg-brand-500/[0.08] shadow-glow-sm'
                      : 'border-white/[0.06] hover:border-white/[0.12] bg-white/[0.02]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-[11px] text-white leading-tight">{prov.name}</span>
                    {formData.provider === prov.id && (
                      <div className="w-4 h-4 bg-gradient-brand rounded-full flex items-center justify-center">
                        <Check className="w-2.5 h-2.5 text-white" />
                      </div>
                    )}
                  </div>
                  <p className="text-[10px] text-slate-500 leading-snug">{prov.desc}</p>
                  <span className={`inline-block text-[8px] font-bold uppercase tracking-wider mt-2 px-1.5 py-0.5 rounded-full ${prov.badgeColor}`}>
                    {prov.badge}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Separator */}
          <div className="h-px bg-white/[0.06]" />

          {/* Provider-Specific Config */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <div className="w-5 h-5 rounded-md bg-brand-500/10 flex items-center justify-center">
                <Cpu className="w-3 h-3 text-brand-400" />
              </div>
              <span className="font-bold">Configuration {selectedProvider.name}</span>
            </div>

            {/* API Key */}
            {selectedProvider.needsKey && (
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5 flex items-center gap-1.5">
                  <Key className="w-3 h-3" /> Clé API <span className="text-red-400">*</span>
                </label>
                <input
                  type="password"
                  placeholder={
                    formData.provider === 'gemini' ? 'AIzaSy...' :
                    formData.provider === 'groq' ? 'gsk_...' :
                    formData.provider === 'deepseek' ? 'sk-...' :
                    'sk-...'
                  }
                  value={formData.apiKey || ''}
                  onChange={(e) => setFormData({ ...formData, apiKey: e.target.value })}
                  className="input-dark w-full"
                />
                <p className="text-[10px] text-slate-600 mt-1 flex items-center gap-1">
                  <span className="w-1 h-1 rounded-full bg-emerald-400 inline-block" />
                  Stockée uniquement dans votre navigateur (localStorage).
                </p>
              </div>
            )}

            {/* Model Selection */}
            {selectedProvider.needsModel && (
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5 flex items-center gap-1.5">
                  <Cpu className="w-3 h-3" /> Modèle
                </label>
                <div className="relative">
                  <select
                    value={formData.modelName || ''}
                    onChange={(e) => setFormData({ ...formData, modelName: e.target.value })}
                    className="input-dark w-full appearance-none pr-8 cursor-pointer"
                  >
                    <option value="">Par défaut ({selectedProvider.defaultModel})</option>
                    {selectedProvider.models?.map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-500 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                </div>
                {formData.provider === 'ollama' && (
                  <p className="text-[10px] text-slate-600 mt-1">
                    Vous pouvez aussi taper un nom de modèle personnalisé dans le champ ci-dessous.
                  </p>
                )}
              </div>
            )}

            {/* Custom model name input for Ollama */}
            {formData.provider === 'ollama' && (
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5 flex items-center gap-1.5">
                  <Cpu className="w-3 h-3" /> Modèle personnalisé (optionnel)
                </label>
                <input
                  type="text"
                  placeholder="ex: llama3:70b, codestral, etc."
                  value={formData.modelName || ''}
                  onChange={(e) => setFormData({ ...formData, modelName: e.target.value })}
                  className="input-dark w-full text-xs"
                />
              </div>
            )}

            {/* Ollama URL */}
            {selectedProvider.needsUrl && (
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5 flex items-center gap-1.5">
                  <Server className="w-3 h-3" /> URL du serveur Ollama
                </label>
                <input
                  type="text"
                  placeholder="http://localhost:11434"
                  value={formData.ollamaUrl || 'http://localhost:11434'}
                  onChange={(e) => setFormData({ ...formData, ollamaUrl: e.target.value })}
                  className="input-dark w-full"
                />
                <p className="text-[10px] text-slate-600 mt-1">
                  Assurez-vous qu'Ollama est démarré (<code className="bg-white/[0.06] px-1 py-0.5 rounded text-brand-400 font-mono">ollama serve</code>).
                </p>
              </div>
            )}
          </div>

          {/* Info Box */}
          <div className="glass-card-elevated rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
              <Globe className="w-3.5 h-3.5 text-brand-400" />
              Guide rapide
            </div>
            <div className="text-[11px] text-slate-500 leading-relaxed space-y-1.5">
              {formData.provider === 'heuristic' && (
                <p>Mode 100% hors-ligne. Aucune configuration nécessaire. L'algorithme trie et priorise vos expériences par matching de mots-clés. Rapide mais moins sophistiqué qu'un LLM.</p>
              )}
              {formData.provider === 'ollama' && (
                <>
                  <p>1. Installez Ollama : <code className="bg-white/[0.06] px-1 py-0.5 rounded text-brand-400 font-mono">curl -fsSL https://ollama.ai/install.sh | sh</code></p>
                  <p>2. Téléchargez un modèle : <code className="bg-white/[0.06] px-1 py-0.5 rounded text-brand-400 font-mono">ollama pull llama3</code></p>
                  <p>3. Lancez le serveur : <code className="bg-white/[0.06] px-1 py-0.5 rounded text-brand-400 font-mono">ollama serve</code></p>
                </>
              )}
              {formData.provider === 'gemini' && (
                <p>Obtenez votre clé API sur <code className="bg-white/[0.06] px-1 py-0.5 rounded text-brand-400 font-mono">aistudio.google.com</code>. Le modèle <strong>gemini-2.5-flash</strong> offre un excellent rapport qualité/vitesse.</p>
              )}
              {formData.provider === 'openai' && (
                <p>Clé API disponible sur <code className="bg-white/[0.06] px-1 py-0.5 rounded text-brand-400 font-mono">platform.openai.com</code>. Le modèle <strong>gpt-4o-mini</strong> est recommandé pour son rapport coût/qualité.</p>
              )}
              {formData.provider === 'groq' && (
                <p>Obtenez une clé gratuite sur <code className="bg-white/[0.06] px-1 py-0.5 rounded text-brand-400 font-mono">console.groq.com</code>. Inférence ultra-rapide grâce au hardware LPU. Idéal pour les itérations rapides.</p>
              )}
              {formData.provider === 'deepseek' && (
                <p>Clé API sur <code className="bg-white/[0.06] px-1 py-0.5 rounded text-brand-400 font-mono">platform.deepseek.com</code>. Le modèle <strong>deepseek-chat</strong> excelle en raisonnement et en compréhension de contexte.</p>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="pt-3 flex items-center justify-end gap-3 border-t border-white/[0.06]">
            <button type="button" onClick={onClose} className="btn-ghost px-4 py-2.5 text-sm">
              Annuler
            </button>
            <button type="submit" className="btn-primary px-6 py-2.5 text-sm">
              Enregistrer
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
