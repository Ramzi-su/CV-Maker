import React, { useState } from 'react';
import {
  Download,
  FileText,
  RefreshCw,
  AlertTriangle,
  Layers,
  Code2,
  Loader2,
} from 'lucide-react';
import { compilePdf, renderLatex } from '../services/api';

export default function ResumePreview({
  cvData,
  templates,
  selectedTemplate,
  setSelectedTemplate,
}) {
  const [viewMode, setViewMode] = useState('pdf');
  const [latexCode, setLatexCode] = useState('');
  const [pdfUrl, setPdfUrl] = useState(null);
  const [isCompiling, setIsCompiling] = useState(false);
  const [compileError, setCompileError] = useState('');
  const [lastCompiledName, setLastCompiledName] = useState('');

  const handleCompile = async (codeToCompile = null) => {
    setIsCompiling(true);
    setCompileError('');
    try {
      const res = await compilePdf(selectedTemplate, cvData, codeToCompile || (viewMode === 'latex' ? latexCode : null));
      setPdfUrl(res.download_url);
      setLastCompiledName(res.filename);
      if (res.latex_code) setLatexCode(res.latex_code);
    } catch (err) {
      setCompileError(err.message || 'Erreur lors de la compilation du PDF.');
    } finally {
      setIsCompiling(false);
    }
  };

  const handleLoadLatex = async () => {
    try {
      const res = await renderLatex(selectedTemplate, cvData);
      setLatexCode(res.latex_code);
      setViewMode('latex');
    } catch (err) {
      setCompileError(err.message || 'Erreur de rendu LaTeX.');
    }
  };

  const handleTemplateChange = async (tplId) => {
    setSelectedTemplate(tplId);
    if (viewMode === 'latex') {
      try {
        const res = await renderLatex(tplId, cvData);
        setLatexCode(res.latex_code);
      } catch (err) {
        setCompileError(err.message);
      }
    }
  };

  return (
    <div className="glass-card rounded-2xl shadow-elevation overflow-hidden flex flex-col min-h-[650px] lg:min-h-[calc(100vh-80px)]">
      {/* Toolbar */}
      <div className="px-4 sm:px-6 py-4 border-b border-white/[0.06] bg-gradient-surface flex flex-wrap items-center justify-between gap-4">
        {/* Template Pills */}
        <div className="flex items-center gap-3">
          <div className="section-icon bg-surface-300 w-8 h-8 rounded-lg">
            <Layers className="w-4 h-4 text-slate-400" />
          </div>
          <div className="flex bg-white/[0.04] p-1 rounded-xl gap-0.5 border border-white/[0.04]">
            {templates.map((tpl) => (
              <button
                key={tpl.id}
                onClick={() => handleTemplateChange(tpl.id)}
                title={tpl.description}
                className={`text-xs px-3.5 py-2 rounded-lg font-semibold transition-smooth ${
                  selectedTemplate === tpl.id
                    ? 'bg-brand-500/15 text-brand-400 shadow-sm border border-brand-500/20'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-white/[0.04]'
                }`}
              >
                {tpl.name}
              </button>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <div className="flex bg-white/[0.04] p-1 rounded-xl gap-0.5 border border-white/[0.04]">
            <button
              onClick={() => setViewMode('pdf')}
              className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg font-semibold transition-smooth ${
                viewMode === 'pdf' ? 'bg-brand-500/15 text-brand-400 border border-brand-500/20' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <FileText className="w-3.5 h-3.5" /> PDF
            </button>
            <button
              onClick={handleLoadLatex}
              className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg font-semibold transition-smooth ${
                viewMode === 'latex' ? 'bg-purple-500/15 text-accent-purple border border-purple-500/20' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <Code2 className="w-3.5 h-3.5" /> LaTeX
            </button>
          </div>

          <button
            onClick={() => handleCompile()}
            disabled={isCompiling}
            className="btn-primary flex items-center gap-1.5 px-4 py-2 text-xs"
          >
            {isCompiling ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
            {isCompiling ? 'Compilation…' : 'Compiler'}
          </button>

          {pdfUrl && (
            <a
              href={pdfUrl}
              download={lastCompiledName || 'cv.pdf'}
              className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-accent-emerald bg-emerald-500/10 hover:bg-emerald-500/15 rounded-xl transition-smooth border border-emerald-500/20"
            >
              <Download className="w-3.5 h-3.5" /> Télécharger
            </a>
          )}
        </div>
      </div>

      {/* Error */}
      {compileError && (
        <div className="mx-4 sm:mx-6 mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-xs text-red-400 flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 shrink-0 text-red-400 mt-0.5" />
          <div className="flex-1 overflow-x-auto">
            <span className="font-bold">Erreur de compilation :</span>
            <pre className="mt-1 font-mono text-[11px] whitespace-pre-wrap text-red-300">{compileError}</pre>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 p-4 sm:p-6 flex flex-col">
        {viewMode === 'pdf' ? (
          pdfUrl ? (
            <div className="flex-1 w-full border border-white/[0.06] rounded-2xl overflow-hidden shadow-dark-elevation bg-surface-100 flex flex-col min-h-[550px]">
              <iframe src={`${pdfUrl}#toolbar=0&navpanes=0`} className="w-full flex-1 rounded-2xl" title="Prévisualisation PDF" />
            </div>
          ) : (
            <div className="flex-1 border-2 border-dashed border-white/[0.08] rounded-2xl flex flex-col items-center justify-center p-8 sm:p-12 text-center">
              <div className="w-16 h-16 bg-surface-300/50 rounded-2xl flex items-center justify-center mb-4">
                <FileText className="w-8 h-8 text-slate-600" />
              </div>
              <h3 className="font-display text-sm font-bold text-slate-300 mb-1">Aucun PDF généré</h3>
              <p className="text-xs text-slate-500 max-w-sm mb-5">
                Cliquez ci-dessous pour compiler votre CV avec le gabarit sélectionné et prévisualiser le résultat.
              </p>
              <button
                onClick={() => handleCompile()}
                disabled={isCompiling}
                className="btn-primary flex items-center gap-2 px-6 py-3 text-sm"
              >
                {isCompiling ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                Générer le PDF
              </button>
            </div>
          )
        ) : (
          <div className="flex-1 flex flex-col space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-500">
              <span>Modifiez le code source LaTeX puis recompilez :</span>
              <button onClick={() => handleCompile(latexCode)} disabled={isCompiling} className="text-xs font-bold text-accent-purple hover:text-purple-300 transition-smooth">
                Recompiler
              </button>
            </div>
            <textarea
              value={latexCode}
              onChange={(e) => setLatexCode(e.target.value)}
              className="flex-1 w-full min-h-[500px] font-mono text-xs code-editor rounded-2xl p-5 focus:outline-none focus:ring-2 focus:ring-purple-500/30 leading-relaxed"
              spellCheck={false}
            />
          </div>
        )}
      </div>
    </div>
  );
}
