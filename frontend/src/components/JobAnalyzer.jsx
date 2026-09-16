import React, { useState } from 'react';
import {
  FileText,
  Search,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Tag,
  Loader2,
  Zap,
} from 'lucide-react';
import { analyzeJob, fetchSampleJob } from '../services/api';
import { DEFAULT_JOB_TEXT } from '../data/defaultData';

export default function JobAnalyzer({
  jobText,
  setJobText,
  onTailor,
  isTailoring,
  tailoredCV,
  aiSettings,
  onOpenSettings,
}) {
  const [analyzedData, setAnalyzedData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState('');

  const handleLoadSample = async () => {
    try {
      const data = await fetchSampleJob();
      setJobText(data.job_text || DEFAULT_JOB_TEXT);
      setAnalyzedData(null);
      setError('');
    } catch {
      setJobText(DEFAULT_JOB_TEXT);
      setAnalyzedData(null);
      setError('');
    }
  };

  const handleAnalyze = async () => {
    if (!jobText.trim()) { setError("Veuillez coller le texte de l'offre d'emploi."); return; }
    setError('');
    setIsAnalyzing(true);
    try {
      const res = await analyzeJob(jobText);
      setAnalyzedData(res);
    } catch {
      const commonTech = [
        'python', 'javascript', 'typescript', 'react', 'vue', 'angular', 'node', 'fastapi',
        'django', 'docker', 'kubernetes', 'aws', 'ci/cd', 'git', 'sql', 'postgresql', 'redis', 'linux'
      ];
      const lower = jobText.toLowerCase();
      const matched = commonTech.filter(t => lower.includes(t));
      const firstLine = jobText.trim().split('\n')[0].replace(/^offre\s*d['’]emploi\s*:\s*/i, '').slice(0, 60);
      setAnalyzedData({
        title: firstLine || 'Poste Cible',
        keywords: matched,
        count: matched.length,
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="glass-card rounded-2xl shadow-elevation p-5 sm:p-6 space-y-5">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="section-icon bg-brand-500/10">
            <FileText className="w-5 h-5 text-brand-400" />
          </div>
          <div>
            <h2 className="font-display text-lg font-extrabold text-white tracking-tight">
              Offre d'Emploi Ciblée
            </h2>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Collez la fiche de poste pour adapter automatiquement votre CV.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button type="button" onClick={handleLoadSample} className="btn-ghost text-xs">
            Exemple d'offre
          </button>
          <button type="button" onClick={onOpenSettings} className="btn-primary flex items-center gap-1.5 text-xs px-3 py-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span className="capitalize">{aiSettings.provider}</span>
          </button>
        </div>
      </div>

      {/* Textarea */}
      <div className="relative">
        <textarea
          rows={8}
          value={jobText}
          onChange={(e) => { setJobText(e.target.value); if (error) setError(''); }}
          placeholder="Collez ici l'intitulé, les missions et les compétences requises de l'offre d'emploi..."
          className="textarea-dark w-full font-mono text-xs"
        />
        {error && (
          <div className="mt-2 text-xs text-red-400 flex items-center gap-1.5 bg-red-500/10 px-3 py-2 rounded-xl border border-red-500/20">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
        <button
          type="button"
          onClick={handleAnalyze}
          disabled={isAnalyzing || isTailoring || !jobText.trim()}
          className="btn-ghost flex items-center justify-center gap-2 text-xs"
        >
          {isAnalyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4 text-slate-500" />}
          Analyser les Mots-Clés
        </button>

        <button
          type="button"
          onClick={onTailor}
          disabled={isTailoring || !jobText.trim()}
          className="btn-primary flex-1 flex items-center justify-center gap-2.5 py-3 text-sm pulse-glow"
        >
          {isTailoring ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Ciblage en cours…</>
          ) : (
            <><Zap className="w-4 h-4" /> Adapter mon CV pour ce poste</>
          )}
        </button>
      </div>

      {/* Keywords */}
      {analyzedData && (
        <div className="p-4 glass-card-elevated rounded-2xl space-y-3 animate-fade-in-up">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-slate-300">Poste : <span className="text-brand-400">{analyzedData.title}</span></span>
            <span className="text-slate-500 bg-white/[0.06] px-2.5 py-0.5 rounded-full border border-white/[0.06] text-[10px] font-bold">{analyzedData.count} mots-clés</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {analyzedData.keywords.map((kw) => (
              <span key={kw} className="tag-dark">
                <Tag className="w-2.5 h-2.5 text-brand-400" />{kw}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Tailored Summary */}
      {tailoredCV && (
        <div className="p-4 bg-emerald-500/[0.06] rounded-2xl border border-emerald-500/20 space-y-3 animate-fade-in-up">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <CheckCircle2 className="w-5 h-5 text-accent-emerald shrink-0" />
              <div>
                <h3 className="text-xs font-bold text-white">CV ciblé : {tailoredCV.target_role}</h3>
                <p className="text-[11px] text-slate-500">Prêt à être compilé en PDF avec le gabarit de votre choix.</p>
              </div>
            </div>
            {tailoredCV.matching_score && (
              <div className="flex items-center gap-1 text-xs font-bold text-accent-emerald bg-emerald-500/10 px-3 py-1.5 rounded-full border border-emerald-500/20">
                <TrendingUp className="w-3.5 h-3.5" />{tailoredCV.matching_score}%
              </div>
            )}
          </div>
          {tailoredCV.key_adaptations?.length > 0 && (
            <ul className="text-xs text-slate-400 space-y-1 pl-5 list-disc">
              {tailoredCV.key_adaptations.map((ad) => <li key={ad}>{ad}</li>)}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
