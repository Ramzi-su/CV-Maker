import React, { useState, useRef } from 'react';
import {
  X,
  Upload,
  FileCode,
  FileText,
  Loader2,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
} from 'lucide-react';
import { extractFromLatex, extractFromPdf } from '../services/api';

export default function ImportModal({ isOpen, onClose, onImport, aiSettings }) {
  const [activeTab, setActiveTab] = useState('latex');
  const [latexCode, setLatexCode] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const [previewData, setPreviewData] = useState(null);
  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  const handleExtractLatex = async () => {
    if (!latexCode.trim()) {
      setError('Veuillez coller le code source LaTeX de votre CV.');
      return;
    }
    setIsProcessing(true);
    setError('');
    setPreviewData(null);
    try {
      const data = await extractFromLatex(latexCode, aiSettings);
      setPreviewData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Seuls les fichiers PDF sont acceptés.');
      return;
    }
    setIsProcessing(true);
    setError('');
    setPreviewData(null);
    try {
      const data = await extractFromPdf(file, aiSettings);
      setPreviewData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleConfirmImport = () => {
    if (previewData) {
      const cleaned = { ...previewData };
      delete cleaned._raw_text;
      onImport(cleaned);
      onClose();
      setPreviewData(null);
      setLatexCode('');
      setError('');
    }
  };

  const handleClose = () => {
    onClose();
    setPreviewData(null);
    setLatexCode('');
    setError('');
  };

  return (
    <div className="modal-overlay">
      <div className="modal-container max-w-2xl w-full">
        {/* Header */}
        <div className="bg-gradient-to-r from-surface-100 to-surface-200 text-white px-6 py-5 flex items-center justify-between border-b border-white/[0.06]">
          <div>
            <h2 className="font-display text-lg font-bold flex items-center gap-2.5">
              <Upload className="w-5 h-5 text-brand-400" />
              Importer un CV existant
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Extrayez automatiquement les informations depuis un fichier LaTeX ou PDF
            </p>
          </div>
          <button onClick={handleClose} className="text-slate-500 hover:text-white p-1.5 rounded-lg hover:bg-white/[0.06] transition-smooth">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-white/[0.06] bg-surface-50/50">
          <button
            onClick={() => { setActiveTab('latex'); setPreviewData(null); setError(''); }}
            className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-semibold transition-smooth border-b-2 ${
              activeTab === 'latex'
                ? 'border-brand-500 text-brand-400 bg-brand-500/[0.04]'
                : 'border-transparent text-slate-500 hover:text-slate-300'
            }`}
          >
            <FileCode className="w-4 h-4" />
            Code source LaTeX
          </button>
          <button
            onClick={() => { setActiveTab('pdf'); setPreviewData(null); setError(''); }}
            className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-semibold transition-smooth border-b-2 ${
              activeTab === 'pdf'
                ? 'border-brand-500 text-brand-400 bg-brand-500/[0.04]'
                : 'border-transparent text-slate-500 hover:text-slate-300'
            }`}
          >
            <FileText className="w-4 h-4" />
            Fichier PDF
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
          {activeTab === 'latex' && !previewData && (
            <>
              <p className="text-xs text-slate-500">
                Collez le code source <code className="bg-white/[0.06] text-brand-400 px-1.5 py-0.5 rounded font-mono text-[11px]">.tex</code> de votre CV existant. Le système extraira automatiquement le nom, les expériences, compétences et formations.
              </p>
              <textarea
                rows={12}
                value={latexCode}
                onChange={(e) => { setLatexCode(e.target.value); setError(''); }}
                placeholder={'\\documentclass{article}\n\\begin{document}\n  % Collez votre CV LaTeX ici...\n\\end{document}'}
                className="w-full font-mono text-xs code-editor rounded-xl p-4 focus:outline-none focus:ring-2 focus:ring-brand-500/30 leading-relaxed"
                spellCheck={false}
              />
              <button
                onClick={handleExtractLatex}
                disabled={isProcessing || !latexCode.trim()}
                className="btn-primary w-full flex items-center justify-center gap-2 py-2.5 text-sm"
              >
                {isProcessing ? (
                  <><Loader2 className="w-4 h-4 animate-spin" /> Extraction en cours...</>
                ) : (
                  <><FileCode className="w-4 h-4" /> Extraire les informations du LaTeX</>
                )}
              </button>
            </>
          )}

          {activeTab === 'pdf' && !previewData && (
            <>
              <p className="text-xs text-slate-500">
                Téléversez un fichier <code className="bg-white/[0.06] text-brand-400 px-1.5 py-0.5 rounded font-mono text-[11px]">.pdf</code> de votre CV existant. Le texte sera extrait automatiquement et analysé.
              </p>
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="w-full border-2 border-dashed border-white/[0.08] hover:border-brand-500/40 rounded-2xl p-12 text-center cursor-pointer transition-smooth hover:bg-brand-500/[0.03] group"
              >
                <Upload className="w-10 h-10 text-slate-600 group-hover:text-brand-400 mx-auto mb-3 transition-smooth" />
                <p className="text-sm font-semibold text-slate-400 group-hover:text-brand-400 transition-smooth">
                  Cliquez pour sélectionner un PDF
                </p>
                <p className="text-xs text-slate-600 mt-1">ou glissez-déposez votre fichier ici</p>
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                className="hidden"
              />
              {isProcessing && (
                <div className="flex items-center justify-center gap-2 py-4 text-sm text-brand-400 font-medium">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Extraction et analyse du PDF en cours...
                </div>
              )}
            </>
          )}

          {/* Error */}
          {error && (
            <div className="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-xs text-red-400">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-400" />
              <span>{error}</span>
            </div>
          )}

          {/* Preview Results */}
          {previewData && (
            <div className="space-y-4 animate-fade-in-up">
              <div className="flex items-center gap-2 text-sm font-bold text-accent-emerald">
                <CheckCircle2 className="w-5 h-5" />
                Extraction réussie — Vérifiez les données ci-dessous :
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                {[
                  { label: 'Nom', value: previewData.contact?.full_name || '—' },
                  { label: 'Email', value: previewData.contact?.email || '—' },
                  { label: 'Expériences', value: `${previewData.experiences?.length || 0} détectées` },
                  { label: 'Compétences', value: `${previewData.skill_categories?.length || 0} catégories` },
                  { label: 'Formations', value: `${previewData.education?.length || 0} détectées` },
                  { label: 'Projets', value: `${previewData.projects?.length || 0} détectés` },
                ].map((item) => (
                  <div key={item.label} className="glass-card-elevated rounded-xl p-3">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">{item.label}</span>
                    <p className="font-semibold text-slate-200 mt-0.5">{item.value}</p>
                  </div>
                ))}
              </div>

              {previewData.summary && (
                <div className="glass-card-elevated rounded-xl p-3 text-xs text-slate-300">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-brand-400">Résumé extrait</span>
                  <p className="mt-1 leading-relaxed">{previewData.summary.substring(0, 300)}{previewData.summary.length > 300 ? '...' : ''}</p>
                </div>
              )}

              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => setPreviewData(null)}
                  className="btn-ghost flex-1 py-2.5 text-sm"
                >
                  Recommencer
                </button>
                <button
                  onClick={handleConfirmImport}
                  className="btn-primary flex-1 flex items-center justify-center gap-2 py-2.5 text-sm"
                >
                  Importer dans mon profil
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
