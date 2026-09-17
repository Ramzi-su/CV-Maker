const API_BASE = (
  import.meta.env.VITE_API_BASE_URL ||
  (typeof window !== 'undefined' && (window.location.hostname.includes('vercel.app') || window.location.hostname.includes('onrender.com'))
    ? 'https://cv-maker-3r45.onrender.com/api'
    : '/api')
).replace(/\/$/, '');

export async function fetchProfile() {
  const res = await fetch(`${API_BASE}/profile`);
  if (!res.ok) throw new Error('Échec du chargement du profil');
  return res.json();
}

export async function saveProfile(profile) {
  const res = await fetch(`${API_BASE}/profile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
  });
  if (!res.ok) throw new Error('Échec de la sauvegarde du profil');
  return res.json();
}

export async function fetchSampleJob() {
  const res = await fetch(`${API_BASE}/sample-job`);
  if (!res.ok) throw new Error("Échec du chargement de l'offre d'exemple");
  return res.json();
}

export async function analyzeJob(jobText) {
  const res = await fetch(`${API_BASE}/analyze-job`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_text: jobText }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Échec de l'analyse de l'offre");
  }
  return res.json();
}

export async function tailorResume({ profile, jobText, provider, apiKey, modelName, ollamaUrl }) {
  const payload = {
    profile,
    job_text: jobText,
    provider: provider || 'heuristic',
    api_key: apiKey || null,
    model_name: modelName || null,
    ollama_url: ollamaUrl || 'http://localhost:11434',
  };

  const res = await fetch(`${API_BASE}/tailor`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Échec de l'adaptation du CV");
  }
  return res.json();
}

export async function renderLatex(template, cvData) {
  const res = await fetch(`${API_BASE}/render-latex`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ template, cv_data: cvData }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Échec du rendu LaTeX');
  }
  return res.json();
}

export async function compilePdf(template, cvData, latexCode = null) {
  const res = await fetch(`${API_BASE}/compile-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      template,
      cv_data: cvData,
      latex_code: latexCode,
    }),
  });

  const data = await res.json();
  if (!res.ok || !data.success) {
    throw new Error(data.error || 'Erreur lors de la compilation du PDF');
  }
  if (data.download_url && !data.download_url.startsWith('http')) {
    data.download_url = `${API_BASE.replace(/\/api$/, '')}${data.download_url}`;
  }
  return data;
}

export async function fetchTemplates() {
  const res = await fetch(`${API_BASE}/templates`);
  if (!res.ok) throw new Error('Échec du chargement des gabarits');
  return res.json();
}

export async function extractFromLatex(latexCode, aiSettings = {}) {
  const payload = {
    latex_code: latexCode,
    provider: aiSettings.provider || 'heuristic',
    api_key: aiSettings.apiKey || '',
    model_name: aiSettings.modelName || '',
    ollama_url: aiSettings.ollamaUrl || 'http://localhost:11434',
  };
  const res = await fetch(`${API_BASE}/extract-latex`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erreur lors de l'extraction du LaTeX");
  }
  return res.json();
}

export async function extractFromPdf(file, aiSettings = {}) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('provider', aiSettings.provider || 'heuristic');
  formData.append('api_key', aiSettings.apiKey || '');
  formData.append('model_name', aiSettings.modelName || '');
  formData.append('ollama_url', aiSettings.ollamaUrl || 'http://localhost:11434');

  const res = await fetch(`${API_BASE}/extract-pdf`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erreur lors de l'extraction du PDF");
  }
  return res.json();
}

export async function injectLatexWithAI(latexTemplate, cvData, aiSettings = {}) {
  const payload = {
    latex_template: latexTemplate,
    cv_data: cvData,
    provider: aiSettings.provider || 'heuristic',
    api_key: aiSettings.apiKey || '',
    model_name: aiSettings.modelName || '',
    ollama_url: aiSettings.ollamaUrl || 'http://localhost:11434',
  };
  const res = await fetch(`${API_BASE}/inject-latex-ai`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erreur lors de l'injection IA dans le LaTeX");
  }
  return res.json();
}
