import React, { useState } from 'react';
import {
  User,
  Briefcase,
  GraduationCap,
  FolderGit2,
  Wrench,
  Plus,
  Trash2,
  Save,
  RotateCcw,
  Check,
  Upload,
} from 'lucide-react';

const InputField = ({ label, value, onChange: onCh, placeholder, type = 'text', className = '' }) => (
  <div className={className}>
    <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">{label}</label>
    <input
      type={type}
      value={value}
      onChange={onCh}
      placeholder={placeholder}
      className="input-dark w-full"
    />
  </div>
);

export default function ProfileEditor({ profile, onChange, onSave, onReset, onOpenImport }) {
  const [activeTab, setActiveTab] = useState('contact');
  const [saveSuccess, setSaveSuccess] = useState(false);

  if (!profile) return null;

  const updateContact = (field, val) => {
    onChange({ ...profile, contact: { ...profile.contact, [field]: val } });
  };

  const handleSave = async () => {
    await onSave();
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2500);
  };

  const addExperience = () => {
    const newExp = {
      id: `exp-${Date.now()}`,
      role: 'Nouveau Poste',
      company: 'Entreprise',
      location: '',
      start_date: '2023',
      end_date: 'Présent',
      highlights: ['Responsabilité ou réalisation clé'],
      technologies: [],
    };
    onChange({ ...profile, experiences: [newExp, ...profile.experiences] });
  };

  const updateExperience = (index, field, val) => {
    const updated = [...profile.experiences];
    updated[index] = { ...updated[index], [field]: val };
    onChange({ ...profile, experiences: updated });
  };

  const removeExperience = (index) => {
    onChange({ ...profile, experiences: profile.experiences.filter((_, i) => i !== index) });
  };

  const addSkillCategory = () => {
    onChange({ ...profile, skill_categories: [...profile.skill_categories, { category: 'Nouvelle Catégorie', skills: ['Compétence 1'] }] });
  };

  const updateCategoryName = (catIndex, name) => {
    const updated = [...profile.skill_categories];
    updated[catIndex] = { ...updated[catIndex], category: name };
    onChange({ ...profile, skill_categories: updated });
  };

  const addSkillToCat = (catIndex, skillName) => {
    if (!skillName.trim()) return;
    const updated = [...profile.skill_categories];
    if (!updated[catIndex].skills.includes(skillName.trim())) {
      updated[catIndex] = { ...updated[catIndex], skills: [...updated[catIndex].skills, skillName.trim()] };
      onChange({ ...profile, skill_categories: updated });
    }
  };

  const removeSkillFromCat = (catIndex, skillIndex) => {
    const updated = [...profile.skill_categories];
    updated[catIndex] = { ...updated[catIndex], skills: updated[catIndex].skills.filter((_, i) => i !== skillIndex) };
    onChange({ ...profile, skill_categories: updated });
  };

  const TABS = [
    { id: 'contact', label: 'Coordonnées', icon: User },
    { id: 'experiences', label: `Expériences (${profile.experiences?.length || 0})`, icon: Briefcase },
    { id: 'skills', label: 'Compétences', icon: Wrench },
    { id: 'education', label: 'Formations', icon: GraduationCap },
    { id: 'projects', label: 'Projets', icon: FolderGit2 },
  ];

  return (
    <div className="glass-card rounded-2xl shadow-elevation overflow-hidden flex flex-col">
      {/* Header */}
      <div className="px-5 sm:px-6 py-4 border-b border-white/[0.06] flex flex-wrap items-center justify-between gap-4 bg-gradient-surface">
        <div>
          <h2 className="font-display text-lg font-extrabold text-white tracking-tight">Profil Maître</h2>
          <p className="text-[11px] text-slate-500 mt-0.5">
            Centralise l'intégralité de vos compétences. L'IA sélectionnera les plus pertinentes pour chaque offre.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {onOpenImport && (
            <button
              onClick={onOpenImport}
              className="btn-ghost flex items-center gap-1.5 text-xs text-accent-purple"
            >
              <Upload className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Importer</span>
            </button>
          )}
          <button
            onClick={onReset}
            className="btn-ghost flex items-center gap-1.5 text-xs"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Exemple</span>
          </button>
          <button
            onClick={handleSave}
            className={`flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-white rounded-xl shadow-sm transition-smooth ${
              saveSuccess ? 'bg-accent-emerald shadow-emerald-500/20' : 'btn-primary'
            }`}
          >
            {saveSuccess ? <Check className="w-3.5 h-3.5" /> : <Save className="w-3.5 h-3.5" />}
            <span>{saveSuccess ? 'Enregistré !' : 'Sauvegarder'}</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-white/[0.06] bg-surface-50/50 px-4 sm:px-6 gap-1 text-sm overflow-x-auto">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 py-3 px-3 border-b-[3px] font-semibold text-xs tracking-wide transition-smooth whitespace-nowrap rounded-t-lg ${
                activeTab === tab.id
                  ? 'border-brand-500 text-brand-400 bg-brand-500/[0.06]'
                  : 'border-transparent text-slate-500 hover:text-slate-300 hover:bg-white/[0.03]'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div className="p-5 sm:p-6 flex-1 overflow-y-auto max-h-[calc(100vh-220px)] lg:max-h-[calc(100vh-180px)]">
        {/* ===== Contact ===== */}
        {activeTab === 'contact' && (
          <div className="space-y-5 animate-fade-in-up">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField label="Nom Complet" value={profile.contact?.full_name || ''} onChange={(e) => updateContact('full_name', e.target.value)} />
              <InputField label="Titre Professionnel" value={profile.contact?.title || ''} onChange={(e) => updateContact('title', e.target.value)} />
              <InputField label="Email" type="email" value={profile.contact?.email || ''} onChange={(e) => updateContact('email', e.target.value)} />
              <InputField label="Téléphone" value={profile.contact?.phone || ''} onChange={(e) => updateContact('phone', e.target.value)} />
              <InputField label="Localisation" value={profile.contact?.location || ''} onChange={(e) => updateContact('location', e.target.value)} />
              <InputField label="LinkedIn" value={profile.contact?.linkedin || ''} onChange={(e) => updateContact('linkedin', e.target.value)} placeholder="linkedin.com/in/..." />
              <InputField label="GitHub" value={profile.contact?.github || ''} onChange={(e) => updateContact('github', e.target.value)} placeholder="github.com/..." />
              <InputField label="Site Web" value={profile.contact?.website || ''} onChange={(e) => updateContact('website', e.target.value)} placeholder="https://..." />
            </div>
            <div>
              <label htmlFor="profile-summary" className="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">Résumé Professionnel</label>
              <textarea
                id="profile-summary"
                rows={4}
                value={profile.summary || ''}
                onChange={(e) => onChange({ ...profile, summary: e.target.value })}
                placeholder="Votre pitch professionnel global..."
                className="textarea-dark w-full"
              />
            </div>
          </div>
        )}

        {/* ===== Experiences ===== */}
        {activeTab === 'experiences' && (
          <div className="space-y-5 animate-fade-in-up">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
              <p className="text-xs text-slate-500">L'algorithme sélectionnera et adaptera les expériences les plus pertinentes pour chaque offre.</p>
              <button onClick={addExperience} className="btn-ghost flex items-center gap-1.5 text-xs text-brand-400 shrink-0">
                <Plus className="w-3.5 h-3.5" /> Ajouter
              </button>
            </div>

            {profile.experiences?.map((exp, idx) => (
              <div key={exp.id || idx} className="glass-card-interactive rounded-2xl p-5 space-y-4 relative group">
                <button onClick={() => removeExperience(idx)} className="absolute top-4 right-4 text-slate-600 hover:text-red-400 p-1.5 rounded-lg hover:bg-red-500/10 transition-smooth opacity-0 group-hover:opacity-100" title="Supprimer">
                  <Trash2 className="w-4 h-4" />
                </button>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pr-10">
                  <div>
                    <label htmlFor={`exp-role-${exp.id || idx}`} className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Poste</label>
                    <input id={`exp-role-${exp.id || idx}`} type="text" value={exp.role} onChange={(e) => updateExperience(idx, 'role', e.target.value)} className="input-dark w-full font-semibold mt-1" />
                  </div>
                  <div>
                    <label htmlFor={`exp-company-${exp.id || idx}`} className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Entreprise</label>
                    <input id={`exp-company-${exp.id || idx}`} type="text" value={exp.company} onChange={(e) => updateExperience(idx, 'company', e.target.value)} className="input-dark w-full mt-1" />
                  </div>
                  <div>
                    <label htmlFor={`exp-start-${exp.id || idx}`} className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Période</label>
                    <div className="flex items-center gap-2 mt-1">
                      <input id={`exp-start-${exp.id || idx}`} type="text" value={exp.start_date} onChange={(e) => updateExperience(idx, 'start_date', e.target.value)} placeholder="Début" className="input-dark w-1/2 text-xs" />
                      <span className="text-slate-600 text-xs">→</span>
                      <input type="text" value={exp.end_date} onChange={(e) => updateExperience(idx, 'end_date', e.target.value)} placeholder="Fin" className="input-dark w-1/2 text-xs" />
                    </div>
                  </div>
                  <div>
                    <label htmlFor={`exp-location-${exp.id || idx}`} className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Lieu</label>
                    <input id={`exp-location-${exp.id || idx}`} type="text" value={exp.location || ''} onChange={(e) => updateExperience(idx, 'location', e.target.value)} className="input-dark w-full mt-1" />
                  </div>
                </div>

                <div>
                  <label htmlFor={`exp-highlights-${exp.id || idx}`} className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Réalisations (1 par ligne)</label>
                  <textarea
                    id={`exp-highlights-${exp.id || idx}`}
                    rows={3}
                    value={exp.highlights?.join('\n') || ''}
                    onChange={(e) => updateExperience(idx, 'highlights', e.target.value.split('\n').filter((l) => l.trim().length > 0))}
                    className="textarea-dark w-full text-xs mt-1"
                  />
                </div>

                <div>
                  <label htmlFor={`exp-technologies-${exp.id || idx}`} className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Technologies (virgules)</label>
                  <input
                    id={`exp-technologies-${exp.id || idx}`}
                    type="text"
                    value={exp.technologies?.join(', ') || ''}
                    onChange={(e) => updateExperience(idx, 'technologies', e.target.value.split(',').map((t) => t.trim()).filter(Boolean))}
                    placeholder="Python, Docker, React..."
                    className="input-dark w-full text-xs mt-1"
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ===== Skills ===== */}
        {activeTab === 'skills' && (
          <div className="space-y-5 animate-fade-in-up">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
              <p className="text-xs text-slate-500">Organisez vos compétences par familles technologiques.</p>
              <button onClick={addSkillCategory} className="btn-ghost flex items-center gap-1.5 text-xs text-brand-400 shrink-0">
                <Plus className="w-3.5 h-3.5" /> Catégorie
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {profile.skill_categories?.map((cat, catIdx) => (
                <div key={cat.id || cat.category} className="glass-card-interactive rounded-2xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <input
                      type="text"
                      value={cat.category}
                      onChange={(e) => updateCategoryName(catIdx, e.target.value)}
                      className="text-sm font-bold text-white bg-transparent border-b-2 border-transparent hover:border-white/10 focus:border-brand-500 focus:outline-none px-1 py-0.5 transition-smooth"
                    />
                    <button onClick={() => onChange({ ...profile, skill_categories: profile.skill_categories.filter((_, i) => i !== catIdx) })} className="text-slate-600 hover:text-red-400 p-1 rounded transition-smooth">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {cat.skills?.map((skill, sIdx) => (
                      <span key={skill} className="tag-dark">
                        {skill}
                        <button onClick={() => removeSkillFromCat(catIdx, sIdx)} className="text-slate-500 hover:text-red-400 ml-0.5">&times;</button>
                      </span>
                    ))}
                  </div>
                  <input
                    type="text"
                    placeholder="+ Ajouter (Entrée)"
                    onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addSkillToCat(catIdx, e.target.value); e.target.value = ''; } }}
                    className="input-dark w-full text-xs"
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ===== Education ===== */}
        {activeTab === 'education' && (
          <div className="space-y-4 animate-fade-in-up">
            {profile.education?.map((edu, idx) => (
              <div key={edu.id || `${edu.degree}-${edu.institution}`} className="glass-card-interactive rounded-2xl p-5">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <InputField label="Diplôme" value={edu.degree} onChange={(e) => { const u = [...profile.education]; u[idx] = { ...u[idx], degree: e.target.value }; onChange({ ...profile, education: u }); }} />
                  <InputField label="Établissement" value={edu.institution} onChange={(e) => { const u = [...profile.education]; u[idx] = { ...u[idx], institution: e.target.value }; onChange({ ...profile, education: u }); }} />
                  <InputField label="Période" value={edu.year} onChange={(e) => { const u = [...profile.education]; u[idx] = { ...u[idx], year: e.target.value }; onChange({ ...profile, education: u }); }} />
                  <InputField label="Détails / Mention" value={edu.details || ''} onChange={(e) => { const u = [...profile.education]; u[idx] = { ...u[idx], details: e.target.value }; onChange({ ...profile, education: u }); }} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ===== Projects ===== */}
        {activeTab === 'projects' && (
          <div className="space-y-4 animate-fade-in-up">
            {profile.projects?.map((proj, idx) => (
              <div key={proj.id || proj.name} className="glass-card-interactive rounded-2xl p-5">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <InputField label="Nom du Projet" value={proj.name} onChange={(e) => { const u = [...profile.projects]; u[idx] = { ...u[idx], name: e.target.value }; onChange({ ...profile, projects: u }); }} />
                  <InputField label="Lien" value={proj.link || ''} onChange={(e) => { const u = [...profile.projects]; u[idx] = { ...u[idx], link: e.target.value }; onChange({ ...profile, projects: u }); }} placeholder="https://..." />
                  <InputField label="Période" value={proj.year || ''} onChange={(e) => { const u = [...profile.projects]; u[idx] = { ...u[idx], year: e.target.value }; onChange({ ...profile, projects: u }); }} />
                  <InputField label="Société / Organisation" value={proj.company || ''} onChange={(e) => { const u = [...profile.projects]; u[idx] = { ...u[idx], company: e.target.value }; onChange({ ...profile, projects: u }); }} />
                </div>
                <div className="mt-3">
                  <label htmlFor={`proj-desc-${proj.id || idx}`} className="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">Description</label>
                  <input
                    id={`proj-desc-${proj.id || idx}`}
                    type="text"
                    value={proj.description}
                    onChange={(e) => { const u = [...profile.projects]; u[idx] = { ...u[idx], description: e.target.value }; onChange({ ...profile, projects: u }); }}
                    className="input-dark w-full"
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
