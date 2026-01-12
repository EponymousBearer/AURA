import { useState, useEffect } from 'react'
import { 
  Upload, 
  Activity, 
  ShieldAlert, 
  Stethoscope, 
  Beaker,
  ChevronRight,
  CheckCircle2,
  AlertCircle,
  Clock,
  User,
  Zap,
  Check
} from 'lucide-react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export default function App() {
  const [health, setHealth] = useState<{ ok: boolean } | null>(null)
  const [loadingHealth, setLoadingHealth] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  
  const [reportText, setReportText] = useState('')
  const [formData, setFormData] = useState({
    patient: {
      age_years: 56,
      sex: 'female',
      syndrome: 'empiric_sepsis_unknown',
      severity: 'stable',
      egfr_ml_min: 80,
      renal_bucket: 'normal',
      beta_lactam_allergy: false,
      other_allergies: [] as string[],
      pregnancy: false,
      hepatic_impairment: false,
      interactions: [] as string[]
    }
  })

  useEffect(() => {
    fetch('http://127.0.0.1:8000/health')
      .then(res => res.json())
      .then(data => { setHealth(data); setLoadingHealth(false); })
      .catch(() => setLoadingHealth(false))
  }, [])

  const syndromes = [
    { value: "empiric_sepsis_unknown", label: "Empiric sepsis (source unknown)" },
    { value: "gn_bacteremia", label: "Gram-negative bacteremia" },
    { value: "mrsa_bacteremia", label: "MRSA bacteremia" },
    { value: "enterococcus_bacteremia", label: "Enterococcus bacteremia" },
    { value: "line_related_bacteremia", label: "Central line–associated bacteremia" },
    { value: "uti_source_bacteremia", label: "UTI-source bacteremia" },
    { value: "pneumonia_source_bacteremia", label: "Pneumonia-source bacteremia" }
  ]

  const severities = [
    { value: "stable", label: "Stable (ward patient)" },
    { value: "sepsis", label: "Sepsis" },
    { value: "septic_shock", label: "Septic shock / ICU" },
    { value: "unknown", label: "Unknown" }
  ]

  const renalBuckets = [
    { value: "normal", label: "Normal (≥ 90)" },
    { value: "mild", label: "Mild (60–89)" },
    { value: "moderate", label: "Moderate (30–59)" },
    { value: "severe", label: "Severe (< 30)" }
  ]

  const allergiesOptions = ["Vancomycin", "Fluoroquinolones", "Sulfonamides", "Macrolides", "Aminoglycosides"]
  const interactionsOptions = ["Warfarin", "Phenytoin", "Methotrexate", "Statins", "QT-prolonging drugs"]

  const handleAnalyze = async () => {
    if (!reportText.trim()) {
      setError("Please provide a microbiology report text.")
      return
    }
    setError(null)
    setAnalyzing(true)
    setResult(null)

    try {
      const response = await fetch('http://127.0.0.1:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          report_text: reportText,
          patient: formData.patient,
          debug: true
        })
      })

      if (!response.ok) throw new Error('Analysis request failed.')
      const data = await response.json()
      setResult(data)
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.')
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div className="min-h-screen bg-white text-black font-sans selection:bg-emerald-100 antialiased overflow-x-hidden">
      {/* Background Soft Glow */}
      <div className="fixed inset-0 pointer-events-none opacity-40">
        <div className="absolute top-[-5%] left-[-5%] w-[40%] h-[40%] bg-[#E8F5E9] blur-[100px] rounded-full"></div>
        <div className="absolute bottom-[-5%] right-[-5%] w-[40%] h-[40%] bg-[#E3F2FD] blur-[100px] rounded-full"></div>
      </div>

      {/* Apple Style Nav */}
      <nav className="sticky top-0 z-[100] w-full bg-white/90 backdrop-blur-xl border-b border-black/5 h-14 flex items-center shadow-sm">
        <div className="max-w-[1200px] mx-auto w-full px-6 flex items-center justify-between">
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <Dna className="w-6 h-6 text-emerald-600" />
              <span className="text-[18px] font-bold tracking-tight text-black">AURA</span>
            </div>
            <div className="hidden md:flex space-x-8 text-[13px] font-bold tracking-tight uppercase text-black/50">
              <span className="text-black">Analysis</span>
              <span className="opacity-40 cursor-not-allowed">Stewardship</span>
              <span className="opacity-40 cursor-not-allowed">Analytics</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className={cn(
              "px-3 py-1 rounded-full text-[11px] font-bold tracking-widest uppercase border transition-all flex items-center space-x-2",
              health?.ok ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-red-50 text-red-700 border-red-200"
            )}>
              <span className={cn("w-2 h-2 rounded-full", health?.ok ? "bg-emerald-500 animate-pulse" : "bg-red-500")}></span>
              <span>{loadingHealth ? 'Syncing' : health?.ok ? 'Ready' : 'Offline'}</span>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-[1100px] mx-auto px-6 py-16 relative z-10">
        <header className="mb-16">
          <h1 className="text-[48px] md:text-[56px] font-bold tracking-tight text-black leading-tight">Clinical Command.</h1>
          <p className="text-[22px] md:text-[24px] text-black/60 mt-4 font-medium tracking-tight max-w-[700px]">
            Precision prescribing powered by AURA. Transform complex microbiology into actionable logic.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
          
          {/* Main Workspace */}
          <div className="lg:col-span-8 flex flex-col gap-10">
            
            {/* Microbiology Interface: Strict Upload */}
            <section 
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              className="group relative bg-white border border-black/10 rounded-[40px] p-12 transition-all hover:border-black/20 hover:shadow-2xl hover:shadow-black/5 flex flex-col items-center justify-center min-h-[380px] overflow-hidden"
            >
              <div className="absolute right-8 top-8 text-[12px] font-black text-black/20 uppercase tracking-[0.3em]">Module 01</div>
              
              {!file ? (
                <div className="flex flex-col items-center text-center animate-in fade-in duration-700">
                  <div className="w-24 h-24 bg-black/[0.03] rounded-full flex items-center justify-center mb-8 group-hover:scale-105 transition-transform duration-500">
                    <Upload className="w-10 h-10 text-black" />
                  </div>
                  <h3 className="text-[24px] font-bold tracking-tight mb-4 text-black">Microbiology Interface</h3>
                  <p className="text-[17px] text-black/50 max-w-[340px] leading-relaxed font-medium">
                    Upload clinical report files. Supports PDF, TXT, and high-res imagery for deep analysis.
                  </p>
                  <button 
                    onClick={() => fileInputRef.current?.click()}
                    className="mt-10 px-8 py-3.5 bg-black text-white rounded-full text-[15px] font-bold tracking-tight hover:scale-[1.02] active:scale-[0.98] transition-all"
                  >
                    Select Culture Report
                  </button>
                </div>
              ) : (
                <div className="flex flex-col items-center animate-in zoom-in-95 duration-300">
                   <div className="w-20 h-20 bg-emerald-50 rounded-[32px] flex items-center justify-center mb-6 shadow-sm">
                      <FileText className="w-10 h-10 text-emerald-600" />
                   </div>
                   <h4 className="text-[22px] font-bold text-black mb-2">{file.name}</h4>
                   <p className="text-[15px] text-black/40 font-bold mb-8 uppercase tracking-widest">{(file.size / 1024).toFixed(1)} KB — Locked</p>
                   <button 
                    onClick={() => setFile(null)}
                    className="flex items-center space-x-2 text-[14px] font-bold text-red-600 hover:bg-red-50 px-6 py-2.5 rounded-full transition-all"
                   >
                     <X className="w-4 h-4" />
                     <span>Discard Analysis</span>
                   </button>
                </div>
              )}
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileChange} 
                className="hidden" 
                accept=".pdf,.txt,.png,.jpg,.jpeg"
              />
            </section>

            {/* Clinical Parameters */}
            <section className="bg-white border border-black/10 rounded-[40px] p-12 shadow-sm">
              <div className="flex items-center justify-between mb-12">
                <div className="flex items-center space-x-5">
                  <div className="w-12 h-12 bg-black/5 rounded-2xl flex items-center justify-center text-black">
                    <Stethoscope className="w-6 h-6" />
                  </div>
                  <h2 className="text-[28px] font-bold tracking-tight text-black">Clinical Parameters</h2>
                </div>
              </div>

              <div className="space-y-14">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                  <div>
                    <label className="text-[15px] font-bold text-black uppercase tracking-widest mb-5 block">Syndrome Classification</label>
                    <div className="relative">
                      <select 
                        className="w-full bg-black/[0.03] border-none rounded-2xl px-6 py-5 text-[18px] font-bold text-black focus:ring-4 focus:ring-black/5 outline-none transition-all appearance-none cursor-pointer"
                        value={formData.patient.syndrome}
                        onChange={(e) => setFormData(p => ({ ...p, patient: { ...p.patient, syndrome: e.target.value }}))}
                      >
                        {syndromes.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                      </select>
                      <ChevronRight className="absolute right-6 top-1/2 -translate-y-1/2 w-5 h-5 text-black rotate-90 pointer-events-none" />
                    </div>
                  </div>

                  <div>
                    <label className="text-[15px] font-bold text-black uppercase tracking-widest mb-5 block">Clinical Severity</label>
                    <div className="flex flex-wrap gap-3">
                       {severities.map(s => (
                         <button
                           key={s.value}
                           onClick={() => setFormData(p => ({ ...p, patient: { ...p.patient, severity: s.value as any }}))}
                           className={cn(
                             "px-8 py-5 rounded-2xl text-[16px] font-bold transition-all shadow-sm border-2",
                             formData.patient.severity === s.value 
                               ? "bg-black text-white border-black" 
                               : "bg-white text-black border-black/5 hover:border-black/20"
                           )}
                         >
                           {s.label}
                         </button>
                       ))}
                    </div>
                  </div>
                </div>

                <div className="pt-12 border-t border-black/5">
                  <label className="text-[15px] font-bold text-black uppercase tracking-widest mb-8 block">Safety & Organ Balance</label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                    <div className="bg-black/[0.02] rounded-[32px] p-8 border border-black/[0.05]">
                       <span className="text-[14px] font-bold text-black uppercase tracking-wider mb-6 block">Renal Efficiency (eGFR)</span>
                       <div className="grid grid-cols-1 gap-3">
                          {renalBuckets.map(b => (
                            <button
                              key={b.value}
                              onClick={() => setFormData(p => ({ ...p, patient: { ...p.patient, renal_bucket: b.value as any }}))}
                              className={cn(
                                "flex items-center justify-between px-6 py-4 rounded-2xl border-2 text-[15px] font-bold transition-all",
                                formData.patient.renal_bucket === b.value 
                                  ? "bg-black text-white border-black shadow-lg" 
                                  : "bg-white text-black border-black/5"
                              )}
                            >
                              <span>{b.label}</span>
                              {formData.patient.renal_bucket === b.value && <CheckCircle2 className="w-5 h-5 text-white" />}
                            </button>
                          ))}
                       </div>
                    </div>

                    <div className="space-y-6">
                       <button 
                        onClick={() => setFormData(p => ({ ...p, patient: { ...p.patient, beta_lactam_allergy: !p.patient.beta_lactam_allergy }}))}
                        className={cn(
                          "w-full flex items-center justify-between px-7 py-5 rounded-2xl border-2 transition-all",
                          formData.patient.beta_lactam_allergy 
                            ? "border-red-600 bg-red-50 text-red-600 shadow-sm" 
                            : "border-black/5 bg-white text-black hover:border-black/20"
                        )}
                      >
                        <div className="flex items-center space-x-4">
                           <ShieldAlert className={cn("w-6 h-6", formData.patient.beta_lactam_allergy ? "text-red-600" : "text-black")} />
                           <span className="text-[16px] font-bold">Beta-Lactam Status</span>
                        </div>
                        {formData.patient.beta_lactam_allergy ? <AlertCircle className="w-6 h-6" /> : <div className="w-6 h-6 rounded-full border-2 border-black/10"></div>}
                      </button>

                      <div className="p-1 text-[13px] font-bold text-black/30 uppercase tracking-[0.2em] mb-2">Other Contraindications</div>
                      <div className="flex flex-wrap gap-2.5">
                        {allergiesOptions.map(a => (
                          <button
                            key={a}
                            onClick={() => setFormData(p => ({
                              ...p,
                              patient: {
                                ...p.patient,
                                other_allergies: p.patient.other_allergies.includes(a)
                                  ? p.patient.other_allergies.filter(x => x !== a)
                                  : [...p.patient.other_allergies, a]
                              }
                            }))}
                            className={cn(
                              "px-5 py-2.5 rounded-xl text-[12px] font-bold uppercase tracking-tight transition-all border-2",
                              formData.patient.other_allergies.includes(a) ? "bg-red-600 text-white border-red-600" : "bg-white text-black border-black/5 hover:border-black/20"
                            )}
                          >
                            {a}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </div>

          {/* Right Panel: Patient Profile & Actions */}
          <div className="lg:col-span-4 space-y-10">
            <section className="bg-white border border-black/10 rounded-[40px] p-10 shadow-sm">
               <h3 className="text-[13px] font-bold text-black/30 uppercase tracking-[0.3em] mb-10">Patient Profile</h3>
               <div className="space-y-12">
                  <div className="group">
                    <div className="flex items-center justify-between mb-5">
                       <label className="text-[16px] font-bold text-black">Age Target</label>
                       <span className="text-[28px] font-black text-black">{formData.patient.age_years}</span>
                    </div>
                    <input 
                      type="range" min="18" max="110" 
                      className="w-full h-2 bg-black/5 rounded-full appearance-none cursor-pointer accent-black"
                      value={formData.patient.age_years}
                      onChange={(e) => setFormData(p => ({ ...p, patient: { ...p.patient, age_years: parseInt(e.target.value) }}))}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    {['male', 'female'].map(g => (
                      <button
                        key={g}
                        onClick={() => setFormData(p => ({ ...p, patient: { ...p.patient, sex: g }}))}
                        className={cn(
                          "py-5 rounded-2xl text-[14px] font-bold uppercase tracking-widest border-2 transition-all text-center",
                          formData.patient.sex === g ? "bg-black text-white border-black shadow-lg" : "bg-white text-black border-black/5 hover:border-black/20"
                        )}
                      >
                        {g}
                      </button>
                    ))}
                  </div>

                  <button 
                    onClick={handleAnalyze}
                    disabled={analyzing}
                    className={cn(
                      "w-full py-6 rounded-3xl font-bold text-[18px] transition-all flex items-center justify-center gap-4 mt-8 shadow-2xl",
                      analyzing 
                        ? "bg-black/5 text-black/20 cursor-not-allowed" 
                        : "bg-emerald-600 text-white shadow-emerald-500/30 hover:bg-emerald-700 active:scale-[0.98]"
                    )}
                  >
                    {analyzing ? (
                      <Activity className="w-6 h-6 animate-spin" />
                    ) : (
                      <Zap className="w-6 h-6" />
                    )}
                    <span>Run Logic Engine</span>
                  </button>
               </div>
            </section>

            {/* Results Output */}
            {result ? (
              <section className="bg-black text-white rounded-[40px] p-10 shadow-3xl animate-in slide-in-from-bottom-10 duration-700 overflow-hidden relative">
                <div className="absolute right-0 top-0 w-32 h-32 bg-emerald-500/20 blur-3xl rounded-full"></div>
                
                <div className="flex items-center space-x-5 mb-10 relative z-10">
                  <div className="w-14 h-14 bg-white/10 rounded-2xl flex items-center justify-center text-emerald-400">
                    <CheckCircle2 className="w-8 h-8" />
                  </div>
                  <div>
                    <h3 className="text-[22px] font-bold tracking-tight">Regimen Alpha</h3>
                    <p className="text-[11px] font-bold text-emerald-400 uppercase tracking-widest mt-1">Stewardship Approved</p>
                  </div>
                </div>

                <div className="space-y-10 relative z-10">
                  <div className="bg-white/10 p-8 rounded-3xl border border-white/5">
                    <span className="text-[12px] font-bold text-white/40 uppercase mb-3 block">Primary Molecule</span>
                    <h4 className="text-[26px] font-bold text-white mb-4">{result.recommendation.primary?.drug}</h4>
                    <div className="flex flex-col gap-3 text-[15px] font-bold tracking-tight">
                      <div className="flex items-center space-x-3 text-emerald-400">
                         <Beaker className="w-5 h-5" />
                         <span>{result.recommendation.primary?.dose}</span>
                      </div>
                      <div className="flex items-center space-x-3 text-white/60">
                         <Clock className="w-5 h-5" />
                         <span>{result.recommendation.primary?.frequency}</span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-5">
                       <span className="text-[12px] font-bold text-white/40 uppercase block tracking-widest">Core Rationale</span>
                       <ul className="space-y-4">
                          {result.recommendation.rationale.slice(0, 3).map((r: string, i: number) => (
                             <li key={i} className="flex items-start space-x-4 text-[14px] leading-relaxed font-bold">
                                <div className="w-2 h-2 bg-emerald-500 rounded-full mt-2 shrink-0 shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
                                <span className="text-white/90">{r}</span>
                             </li>
                          ))}
                       </ul>
                  </div>

                  <div className="pt-8 border-t border-white/10 flex items-center justify-between">
                     <div className="flex items-center space-x-3 text-[13px] font-black uppercase text-emerald-400">
                        <ClipboardCheck className="w-5 h-5" />
                        <span>Analysis Confirmed</span>
                     </div>
                  </div>
                </div>
              </section>
            {error && (
               <div className="bg-red-50/80 border border-red-100 rounded-3xl p-6 text-red-600 flex items-start space-x-4 animate-in shake duration-500">
                 <AlertCircle className="w-6 h-6 shrink-0" />
                 <div>
                    <h4 className="font-black text-[10px] uppercase tracking-widest mb-1">Error Encountered</h4>
                    <p className="text-xs font-bold leading-normal">{error}</p>
                 </div>
               </div>
            )}
          </div>

        </div>
      </main>

      <footer className="max-w-7xl mx-auto px-6 py-12 border-t border-slate-200 mt-20 flex flex-col md:flex-row justify-between items-center bg-white/20 backdrop-blur-md">
        <div className="text-slate-400 text-[10px] font-black tracking-[0.3em] uppercase mb-6 md:mb-0">
          AURA &copy; 2026 Medical Intelligence Engine
        </div>
        <div className="flex gap-10 opacity-60">
           {['Antibiogram v2.4', 'GDPR', 'HIPAA'].map(tag => (
             <span key={tag} className="text-[9px] font-black text-slate-900 tracking-widest uppercase">{tag}</span>
           ))}
        </div>
      </footer>
    </div>
  )
}
