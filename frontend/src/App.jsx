import React, { useState, useEffect } from 'react';
import {
  FileText,
  User,
  Sparkles,
  Settings,
  Layers,
  Upload,
  ChevronRight,
  Zap,
  Menu,
  X,
} from 'lucide-react';
import ProfileEditor from './components/ProfileEditor';
import JobAnalyzer from './components/JobAnalyzer';
import ResumePreview from './components/ResumePreview';
import AISettingsModal from './components/AISettingsModal';
import ImportModal from './components/ImportModal';
import {
  fetchProfile,
  saveProfile,
  fetchSampleJob,
  fetchTemplates,
  tailorResume,
} from './services/api';

const STEPS = [
  { id: 'profile', label: 'Profil Maître', shortLabel: 'Profil', icon: User, num: '1', desc: 'Vos informations complètes' },
  { id: 'job', label: 'Ciblage & Adaptation', shortLabel: 'Ciblage', icon: Sparkles, num: '2', desc: 'Analyser et adapter le CV' },
  { id: 'preview', label: 'Rendu & Export PDF', shortLabel: 'PDF', icon: Layers, num: '3', desc: 'Prévisualiser et télécharger' },
];

export default function App() {
  const [activeStep, setActiveStep] = useState('job');
  const [profile, setProfile] = useState(null);
  const [jobText, setJobText] = useState('');
  const [tailoredCV, setTailoredCV] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('modern');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isImportOpen, setIsImportOpen] = useState(false);
  const [isTailoring, setIsTailoring] = useState(false);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const [aiSettings, setAiSettings] = useState(() => {
    const saved = localStorage.getItem('cvmaker_ai_settings');
    return saved
      ? JSON.parse(saved)
      : { provider: 'heuristic', apiKey: '', modelName: '', ollamaUrl: 'http://localhost:11434' };
  });

  useEffect(() => {
    async function init() {
      try {
        const [profData, jobData, tplData] = await Promise.all([
          fetchProfile(),
          fetchSampleJob(),
          fetchTemplates(),
        ]);
        setProfile(profData);
        setJobText(jobData.job_text || '');
        setTemplates(tplData);
      } catch (err) {
        console.error('Initialization error:', err);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  const handleSaveSettings = (s) => {
    setAiSettings(s);
    localStorage.setItem('cvmaker_ai_settings', JSON.stringify(s));
  };

  const handleSaveProfile = async () => {
    if (profile) await saveProfile(profile);
  };

  const handleResetProfile = async () => {
    const profData = await fetchProfile();
    setProfile(profData);
  };

  const handleImport = (importedData) => {
    if (!importedData) return;
    const merged = {
      contact: { ...profile?.contact, ...importedData.contact },
      summary: importedData.summary || profile?.summary || '',
      experiences: importedData.experiences?.length ? importedData.experiences : (profile?.experiences || []),
      education: importedData.education?.length ? importedData.education : (profile?.education || []),
      projects: importedData.projects?.length ? importedData.projects : (profile?.projects || []),
      skill_categories: importedData.skill_categories?.length ? importedData.skill_categories : (profile?.skill_categories || []),
      languages: importedData.languages?.length ? importedData.languages : (profile?.languages || []),
      certifications: importedData.certifications?.length ? importedData.certifications : (profile?.certifications || []),
    };
    for (const key of Object.keys(merged.contact)) {
      if (!merged.contact[key] && profile?.contact?.[key]) {
        merged.contact[key] = profile.contact[key];
      }
    }
    setProfile(merged);
    setActiveStep('profile');
  };

  const handleTailor = async () => {
    if (!profile || !jobText.trim()) return;
    setIsTailoring(true);
    try {
      const res = await tailorResume({
        profile,
        jobText,
        provider: aiSettings.provider,
        apiKey: aiSettings.apiKey,
        modelName: aiSettings.modelName,
        ollamaUrl: aiSettings.ollamaUrl,
      });
      setTailoredCV(res);
      setActiveStep('preview');
    } catch (err) {
      alert(`Erreur lors de l'adaptation : ${err.message}`);
    } finally {
      setIsTailoring(false);
    }
  };

  const getPreviewData = () => {
    if (tailoredCV) return { ...tailoredCV, contact: profile?.contact || {} };
    return profile || {};
  };

  const handleStepChange = (stepId) => {
    setActiveStep(stepId);
    setMobileMenuOpen(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface bg-dot-pattern">
        <div className="flex flex-col items-center gap-5">
          <div className="w-14 h-14 bg-gradient-brand rounded-2xl flex items-center justify-center shadow-glow-md">
            <FileText className="w-7 h-7 text-white" />
          </div>
          <div className="flex items-center gap-3 text-slate-400 font-medium text-sm">
            <div className="w-5 h-5 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
            Chargement de CV-Maker…
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex bg-surface bg-dot-pattern">
      {/* ========== SIDEBAR (Desktop) ========== */}
      <aside className="hidden lg:flex flex-col w-[260px] fixed inset-y-0 left-0 bg-gradient-sidebar border-r border-white/[0.06] z-30">
        {/* Brand */}
        <div className="px-5 py-6 flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-brand rounded-xl flex items-center justify-center text-white shadow-glow-sm">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-display font-extrabold text-white tracking-tight text-base">CV-Maker</span>
            </div>
            <p className="text-[10px] text-slate-500 font-medium">LaTeX + IA · Générateur de CV</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 mt-2 space-y-1">
          <p className="px-3 text-[9px] font-bold uppercase tracking-[0.15em] text-slate-600 mb-3">Étapes</p>
          {STEPS.map((step) => {
            const isActive = activeStep === step.id;
            const isCompleted =
              (step.id === 'profile' && profile?.contact?.full_name) ||
              (step.id === 'job' && tailoredCV) ||
              false;
            let indicatorClass = 'step-indicator-default';
            if (isActive) {
              indicatorClass = 'step-indicator-active';
            } else if (isCompleted) {
              indicatorClass = 'step-indicator-complete';
            }

            return (
              <button
                key={step.id}
                onClick={() => handleStepChange(step.id)}
                className={`nav-item w-full text-left ${isActive ? 'active' : ''}`}
              >
                <span className={`step-indicator ${indicatorClass}`}>
                  {step.num}
                </span>
                <div className="flex-1 min-w-0">
                  <span className="block text-[13px] truncate">{step.label}</span>
                  <span className="block text-[10px] text-slate-500 font-normal truncate">{step.desc}</span>
                </div>
                {isActive && <ChevronRight className="w-3.5 h-3.5 text-brand-500 shrink-0" />}
              </button>
            );
          })}
        </nav>

        {/* Sidebar Footer Actions */}
        <div className="px-3 pb-5 space-y-2">
          <div className="h-px bg-white/[0.06] mx-2 mb-3" />
          <button
            onClick={() => setIsImportOpen(true)}
            className="btn-ghost w-full flex items-center gap-2 text-xs"
          >
            <Upload className="w-3.5 h-3.5 text-accent-purple" />
            <span>Importer un CV</span>
          </button>
          <button
            onClick={() => setIsSettingsOpen(true)}
            className="btn-ghost w-full flex items-center justify-between text-xs"
          >
            <span className="flex items-center gap-2">
              <Settings className="w-3.5 h-3.5" />
              Paramètres IA
            </span>
            <span className="text-[10px] font-bold text-brand-400 capitalize bg-brand-500/10 px-2 py-0.5 rounded-full">
              {aiSettings.provider}
            </span>
          </button>
        </div>
      </aside>

      {/* ========== MOBILE HEADER ========== */}
      <header className="lg:hidden fixed top-0 left-0 right-0 z-40 bg-surface-50/95 backdrop-blur-xl border-b border-white/[0.06]">
        <div className="flex items-center justify-between px-4 h-14">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-gradient-brand rounded-lg flex items-center justify-center text-white shadow-glow-sm">
              <FileText className="w-4 h-4" />
            </div>
            <span className="font-display font-bold text-white text-sm">CV-Maker</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="btn-ghost flex items-center gap-1.5 px-2.5 py-1.5 text-[11px]"
            >
              <Zap className="w-3 h-3 text-brand-400" />
              <span className="capitalize">{aiSettings.provider}</span>
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="w-9 h-9 rounded-xl flex items-center justify-center text-slate-400 hover:text-white hover:bg-white/[0.06] transition-smooth"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu Dropdown */}
        {mobileMenuOpen && (
          <div className="border-t border-white/[0.06] bg-surface-50/98 backdrop-blur-xl px-3 py-3 space-y-1 animate-fade-in-up">
            {STEPS.map((step) => {
              const isActive = activeStep === step.id;
              return (
                <button
                  key={step.id}
                  onClick={() => handleStepChange(step.id)}
                  className={`nav-item w-full text-left ${isActive ? 'active' : ''}`}
                >
                  <span className={`step-indicator ${isActive ? 'step-indicator-active' : 'step-indicator-default'}`}>
                    {step.num}
                  </span>
                  <span>{step.label}</span>
                </button>
              );
            })}
            <div className="h-px bg-white/[0.06] my-2" />
            <button onClick={() => { setIsImportOpen(true); setMobileMenuOpen(false); }} className="nav-item w-full text-left">
              <Upload className="w-4 h-4 text-accent-purple" />
              <span>Importer un CV</span>
            </button>
          </div>
        )}

        {/* Mobile Step Pills */}
        <div className="flex border-t border-white/[0.04] bg-surface/80">
          {STEPS.map((step) => (
            <button
              key={step.id}
              onClick={() => handleStepChange(step.id)}
              className={`flex-1 py-2.5 text-[11px] font-bold text-center transition-smooth ${
                activeStep === step.id
                  ? 'text-brand-400 border-b-2 border-brand-500 bg-brand-500/[0.06]'
                  : 'text-slate-600 border-b-2 border-transparent'
              }`}
            >
              {step.shortLabel}
            </button>
          ))}
        </div>
      </header>

      {/* ========== MAIN CONTENT ========== */}
      <main className="flex-1 lg:ml-[260px] min-h-screen pt-[108px] lg:pt-0">
        <div className="p-4 sm:p-6 lg:p-8 max-w-[1400px] mx-auto">
          {activeStep === 'profile' && profile && (
            <div className="animate-fade-in-up">
              <ProfileEditor
                profile={profile}
                onChange={setProfile}
                onSave={handleSaveProfile}
                onReset={handleResetProfile}
                onOpenImport={() => setIsImportOpen(true)}
              />
            </div>
          )}

          {activeStep === 'job' && (
            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start animate-fade-in-up">
              <div className="xl:col-span-7">
                <JobAnalyzer
                  jobText={jobText}
                  setJobText={setJobText}
                  onTailor={handleTailor}
                  isTailoring={isTailoring}
                  tailoredCV={tailoredCV}
                  aiSettings={aiSettings}
                  onOpenSettings={() => setIsSettingsOpen(true)}
                />
              </div>
              <div className="xl:col-span-5">
                <div className="glass-card rounded-2xl shadow-elevation p-6 space-y-5">
                  <div className="flex items-center gap-3">
                    <div className="section-icon bg-brand-500/10">
                      <Sparkles className="w-5 h-5 text-brand-400" />
                    </div>
                    <div>
                      <h3 className="font-display text-sm font-bold text-white">Comment fonctionne l'adaptation ?</h3>
                      <p className="text-[10px] text-slate-500 mt-0.5">Pipeline d'analyse et de ciblage automatique</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    {[
                      { n: '1', title: 'Extraction ATS', desc: "Analyse de l'offre d'emploi pour identifier les mots-clés, technologies et compétences prioritaires.", color: 'text-brand-400 bg-brand-500/10' },
                      { n: '2', title: 'Priorisation STAR', desc: "Réorganisation et reformulation de vos réalisations existantes sans inventer d'expériences.", color: 'text-accent-purple bg-purple-500/10' },
                      { n: '3', title: 'Compilation LaTeX', desc: 'Génération du document LaTeX avec échappement rigoureux et compilation automatique en PDF.', color: 'text-accent-emerald bg-emerald-500/10' },
                    ].map((step) => (
                      <div key={step.n} className="flex items-start gap-3 p-3 rounded-xl hover:bg-white/[0.02] transition-smooth">
                        <span className={`w-7 h-7 rounded-lg flex items-center justify-center text-[11px] font-bold shrink-0 mt-0.5 ${step.color}`}>
                          {step.n}
                        </span>
                        <div>
                          <p className="text-xs font-bold text-slate-200">{step.title}</p>
                          <p className="text-[11px] text-slate-500 leading-relaxed mt-0.5">{step.desc}</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  {tailoredCV && (
                    <div className="pt-3 border-t border-white/[0.06]">
                      <button
                        onClick={() => setActiveStep('preview')}
                        className="btn-primary w-full flex items-center justify-center gap-2 text-xs"
                      >
                        Voir la prévisualisation PDF
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeStep === 'preview' && (
            <div className="animate-fade-in-up">
              <ResumePreview
                cvData={getPreviewData()}
                templates={templates}
                selectedTemplate={selectedTemplate}
                setSelectedTemplate={setSelectedTemplate}
              />
            </div>
          )}
        </div>
      </main>

      {/* ========== MODALS ========== */}
      <AISettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        settings={aiSettings}
        onSave={handleSaveSettings}
      />
      <ImportModal
        isOpen={isImportOpen}
        onClose={() => setIsImportOpen(false)}
        onImport={handleImport}
      />
    </div>
  );
}
