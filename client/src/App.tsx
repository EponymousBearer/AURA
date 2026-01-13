import { useState, useEffect, useRef } from 'react'
import { 
  Upload, 
  Activity, 
  ShieldAlert, 
  Stethoscope, 
  Beaker,
  ChevronRight,
  CheckCircle2,
  AlertCircle,
  FileText,
  X,
  Dna,
  Zap,
  Clock,
  ClipboardCheck,
  PieChart
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
  
  const [file, setFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [formData, setFormData] = useState({
    patient: {
      age_years: 56,
      sex: 'female',
      syndrome: 'empiric sepsis/bacteremia',
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
      .then(data => { setHealth(data); setLoadingHealth(false); console.log(data)})
      .catch(() => setLoadingHealth(false))
  }, [])

  const syndromes = [
    { value: "empiric sepsis/bacteremia", label: "Empiric sepsis (source unknown)" },
    { value: "Gram-positive bacteremia (alternative)", label: "Gram-negative bacteremia" },
    { value: "MRSA/Enterococcus bacteremia", label: "MRSA/Enterococcus bacteremia" },
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
      setError(null)
    }
  }

  const handleAnalyze = async () => {
    if (!file) {
      setError("Please upload a microbiology culture report.")
      return
    }
    setError(null)
    setAnalyzing(true)
    setResult(null)

    try {
      const reader = new FileReader()
      const text = await new Promise<string>((resolve, reject) => {
        reader.onload = (e) => resolve(e.target?.result as string || "")
        reader.onerror = reject
        if (file.type === "text/plain" || file.name.endsWith(".txt")) {
          reader.readAsText(file)
        } else {
          // Fallback for demo: send descriptive tag
          resolve(`[BINARY_DATA:${file.name}] Clinical report extracted from ${file.type}`)
        }
      })

      const payload = {
        // report_text: text || `Analysis request for ${file.name}`,
          report_text: "Specimen Desc. : BLOOD C/S\\nResult :\\n1: E. COLI\\nANTIBIOTIC SUSCEPTIBILITY\\n1   PIPERACILLIN-TAZOBACTAM   S\\n2   AMIKACIN                  S\\n3   GENTAMICIN                S\\n",
        specimen_hint: null,
        patient: formData.patient,
        debug: true
      }

      console.log('Sending Payload:', JSON.stringify(payload, null, 2))

      const response = await fetch('http://127.0.0.1:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail?.[0]?.msg || 'Analysis request failed.')
      }
      const data = await response.json()
      setResult(data)
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.')
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#FBFBFD] text-black font-sans selection:bg-emerald-100 antialiased overflow-x-hidden">
      {/* Background Soft Glow */}
      <div className="fixed inset-0 pointer-events-none opacity-30">
        <div className="absolute top-[-5%] left-[-5%] w-[30%] h-[30%] bg-[#E8F5E9] blur-[100px] rounded-full"></div>
        <div className="absolute bottom-[-5%] right-[-5%] w-[30%] h-[30%] bg-[#E3F2FD] blur-[100px] rounded-full"></div>
      </div>

      {/* Compact Nav */}
      <nav className="sticky top-0 z-[100] w-full bg-white/90 backdrop-blur-xl border-b border-black/5 h-12 flex items-center shadow-sm">
        <div className="max-w-[1200px] mx-auto w-full px-28 flex items-center justify-between">
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <Dna className="w-5 h-5 text-emerald-600" />
              <span className="text-[18px] font-bold tracking-tight text-black uppercase">AURA</span>
            </div>
            <div className="hidden md:flex space-x-6 text-[12px] font-bold tracking-tight uppercase">
            </div>
          </div>
          
          <div className="flex items-center">
            <div className={cn(
              "px-2.5 py-0.5 rounded-full text-[9px] font-black tracking-widest uppercase border flex items-center space-x-1.5",
              health?.ok ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-red-50 text-red-700 border-red-200"
            )}>
              <span className={cn("w-1.5 h-1.5 rounded-full", health?.ok ? "bg-emerald-500 animate-pulse" : "bg-red-500")}></span>
              <span>{loadingHealth ? 'Sync' : health?.ok ? 'Ready' : 'Offline'}</span>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-[1000px] mx-auto px-6 py-12 relative z-10 font-sans">
        <header className="mb-10 text-center md:text-left">
          <h1 className="text-[28px] md:text-[28px] font-bold tracking-tight text-black leading-tight">Clinical Command.</h1>
          <p className="text-[16px] md:text-[16px] text-black/60 mt-3 font-medium tracking-tight max-w-[600px] leading-snug">
            Precision prescribing powered by AURA. Transform complex microbiology into actionable insights.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          <div className="lg:col-span-8 flex flex-col gap-8">
            
            {/* Microbiology Interface: Compact Upload */}
            <section 
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              className="group relative bg-white border border-black/10 rounded-3xl p-8 transition-all hover:border-black/20 hover:shadow-xl flex flex-col items-center justify-center min-h-[280px] overflow-hidden"
            >
              {!file ? (
                <div className="flex flex-col items-center text-center animate-in fade-in duration-500">
                  <div className="w-16 h-16 bg-black/[0.03] rounded-full flex items-center justify-center mb-6">
                    <Upload className="w-7 h-7 text-black" />
                  </div>
                  <h3 className="text-[18px] font-bold tracking-tight mb-2 text-black uppercase">Microbiology Interface</h3>
                  <p className="text-[14px] text-black/50 max-w-[300px] leading-relaxed">
                    Upload clinical report files. Supports PDF, TXT, and Images.
                  </p>
                  <button 
                    onClick={() => fileInputRef.current?.click()}
                    className="mt-6 px-6 py-2.5 bg-black text-white rounded-full text-[13px] font-bold tracking-tight hover:scale-[1.02] active:scale-[0.98] transition-all shadow-lg"
                  >
                    Select Report
                  </button>
                </div>
              ) : (
                <div className="flex flex-col items-center animate-in zoom-in-95 duration-300">
                   <div className="w-14 h-14 bg-emerald-50 rounded-2xl flex items-center justify-center mb-4 shadow-sm">
                      <FileText className="w-7 h-7 text-emerald-600" />
                   </div>
                   <h4 className="text-[16px] font-bold text-black mb-1">{file.name}</h4>
                   <p className="text-[11px] text-black/40 font-bold mb-6 uppercase tracking-widest">{(file.size / 1024).toFixed(1)} KB — Locked</p>
                   <button 
                    onClick={() => setFile(null)}
                    className="flex items-center space-x-2 text-[12px] font-bold text-red-600 hover:bg-red-50 px-5 py-2 rounded-full transition-all"
                   >
                     <X className="w-3.5 h-3.5" />
                     <span>Discard Payload</span>
                   </button>
                </div>
              )}
              <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept=".pdf,.txt,.png,.jpg,.jpeg" />
            </section>

            {/* Clinical Parameters: Compact Grid */}
            <section className="bg-white border border-black/10 rounded-3xl p-8 shadow-sm">
              <div className="flex items-center space-x-4 mb-8">
                <div className="w-10 h-10 bg-black/5 rounded-xl flex items-center justify-center text-black">
                  <Stethoscope className="w-5 h-5" />
                </div>
                <h2 className="text-[20px] font-bold tracking-tight text-black">Clinical Context</h2>
              </div>

              <div className="space-y-10">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div>
                    <label className="text-[12px] font-bold text-black uppercase tracking-widest mb-4 block">Syndrome</label>
                    <div className="relative">
                      <select 
                        className="w-full bg-black/[0.03] border-none rounded-xl px-4 py-3 text-[14px] font- text-black focus:ring-2 focus:ring-black/5 outline-none appearance-none cursor-pointer"
                        value={formData.patient.syndrome}
                        onChange={(e) => setFormData(p => ({ ...p, patient: { ...p.patient, syndrome: e.target.value }}))}
                      >
                        {syndromes.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                      </select>
                      <ChevronRight className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-black rotate-90 pointer-events-none" />
                    </div>
                  </div>

                  <div>
                    <label className="text-[12px] font-bold text-black uppercase tracking-widest mb-4 block">Severity</label>
                    <div className="flex flex-wrap gap-2">
                       {severities.map(s => (
                         <button
                           key={s.value}
                           onClick={() => setFormData(p => ({ ...p, patient: { ...p.patient, severity: s.value as any }}))}
                           className={cn(
                             "px-4 py-2 rounded-xl text-[12px] font-semibold transition-all border",
                             formData.patient.severity === s.value 
                               ? "bg-black text-white border-black" 
                               : "bg-white text-black border-black/5 hover:border-black/10"
                           )}
                         >
                           {s.label}
                         </button>
                       ))}
                    </div>
                  </div>
                </div>

                <div className="pt-8 border-t border-black/5">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                       <span className="text-[12px] font-bold text-black uppercase tracking-widest mb-4 block">Renal Efficiency (eGFR)</span>
                       <div className="grid grid-cols-1 gap-2">
                          {renalBuckets.map(b => (
                            <button
                              key={b.value}
                              onClick={() => setFormData(p => ({ ...p, patient: { ...p.patient, renal_bucket: b.value as any }}))}
                              className={cn(
                                "flex items-center justify-between px-4 py-3 rounded-xl border text-[13px] font-semibold transition-all",
                                formData.patient.renal_bucket === b.value ? "bg-black text-white border-black" : "bg-white text-black border-black/5"
                              )}
                            >
                              <span>{b.label}</span>
                              {formData.patient.renal_bucket === b.value && <CheckCircle2 className="w-4 h-4 text-white" />}
                            </button>
                          ))}
                       </div>
                    </div>

                    <div className="space-y-4">
                       <button 
                        onClick={() => setFormData(p => ({ ...p, patient: { ...p.patient, beta_lactam_allergy: !p.patient.beta_lactam_allergy }}))}
                        className={cn(
                          "w-full flex items-center justify-between px-5 py-4 rounded-xl border transition-all text-[13px] font-semibold uppercase",
                          formData.patient.beta_lactam_allergy ? "border-red-600 bg-red-50 text-red-600 shadow-sm" : "border-black/5 bg-white text-black"
                        )}
                      >
                        <div className="flex items-center space-x-3">
                           <ShieldAlert className="w-5 h-5" />
                           <span>Beta-Lactam Warning</span>
                        </div>
                        {formData.patient.beta_lactam_allergy && <AlertCircle className="w-5 h-5 shadow-sm" />}
                      </button>

                      <div className="text-[11px] font-bold text-black/30 uppercase tracking-widest mb-2 px-1">Other Contraindications</div>
                      <div className="flex flex-wrap gap-1.5">
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
                              "px-3 py-1.5 rounded-lg text-[12px] font-semibold uppercase border transition-all",
                              formData.patient.other_allergies.includes(a) ? "bg-red-600 text-white border-red-600 shadow-sm" : "bg-white text-black border-black/10"
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

          <div className="lg:col-span-4 space-y-8">
            <section className="bg-white border border-black/10 rounded-3xl p-8 shadow-sm">
               <h3 className="text-[11px] font-bold text-black/30 uppercase tracking-widest mb-8">Patient Profile</h3>
               <div className="space-y-10">
                  <div>
                    <div className="flex items-center justify-between mb-4">
                       <label className="text-[14px] font-bold text-black">Age Group</label>
                       <span className="text-[24px] font-bold text-black">{formData.patient.age_years}</span>
                    </div>
                    <input 
                      type="range" min="18" max="110" 
                      className="w-full h-1.5 bg-black/5 rounded-full appearance-none cursor-pointer accent-black"
                      value={formData.patient.age_years}
                      onChange={(e) => setFormData(p => ({ ...p, patient: { ...p.patient, age_years: parseInt(e.target.value) }}))}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    {['male', 'female'].map(g => (
                      <button
                        key={g}
                        onClick={() => setFormData(p => ({ ...p, patient: { ...p.patient, sex: g }}))}
                        className={cn(
                          "py-3 rounded-xl text-[12px] font-bold uppercase tracking-widest border transition-all text-center",
                          formData.patient.sex === g ? "bg-black text-white border-black" : "bg-white text-black border-black/5"
                        )}
                      >
                        {g}
                      </button>
                    ))}
                  </div>

                  <button 
                    onClick={handleAnalyze} disabled={analyzing}
                    className={cn(
                      "w-full py-4 rounded-2xl font-bold text-[14px] uppercase tracking-widest transition-all flex items-center justify-center gap-3 mt-6 shadow-xl",
                      analyzing ? "bg-black/5 text-black/20" : "bg-emerald-600 text-white shadow-emerald-500/30 hover:bg-emerald-700"
                    )}
                  >
                    {analyzing ? <Activity className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
                    <span>Run Logic Engine</span>
                  </button>
               </div>
            </section>

            {result ? (
              <section className="bg-black text-white rounded-3xl p-8 shadow-2xl animate-in fade-in slide-in-from-bottom-5 duration-500 relative border border-emerald-500/20">
                <div className="flex items-center space-x-4 mb-8">
                  <div className="w-12 h-12 bg-white/10 rounded-2xl flex items-center justify-center text-emerald-400">
                    <CheckCircle2 className="w-7 h-7" />
                  </div>
                  <div>
                    <h3 className="text-[18px] font-bold tracking-tight uppercase">Regimen Plan</h3>
                    <p className="text-[12px] font-black text-emerald-400 uppercase tracking-widest mt-0.5">Verified</p>
                  </div>
                </div>

                <div className="space-y-8">
                  <div className="bg-white/10 p-6 rounded-2xl border border-white/5">
                    <span className="text-[11px] font-bold text-white/40 uppercase mb-3 block tracking-widest">Primary Molecule</span>
                    <h4 className="text-[22px] font-bold text-white mb-4 uppercase tracking-tight">{result.recommendation.primary?.drug}</h4>
                    <div className="flex flex-col gap-3 text-[13px] font-bold">
                      <div className="flex items-center space-x-3 text-emerald-400">
                         <Beaker className="w-4 h-4" />
                         <span>{result.recommendation.primary?.dose}</span>
                      </div>
                      <div className="flex items-center space-x-3 text-white/60">
                         <Clock className="w-4 h-4" />
                         <span>{result.recommendation.primary?.frequency}</span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                       <span className="text-[11px] font-bold text-white/40 uppercase block tracking-widest">Rationale</span>
                       <ul className="space-y-3">
                          {result.recommendation.rationale.slice(0, 3).map((r: string, i: number) => (
                             <li key={i} className="flex items-start space-x-3 text-[13px] leading-relaxed font-bold">
                                <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2 shrink-0"></div>
                                <span className="text-white/90">{r}</span>
                             </li>
                          ))}
                       </ul>
                  </div>

                  <div className="pt-6 border-t border-white/10 flex items-center justify-between">
                     <div className="flex items-center space-x-2 text-[11px] font-black uppercase text-emerald-400">
                        <ClipboardCheck className="w-4 h-4" />
                        <span>Analysis Confirmed</span>
                     </div>
                  </div>
                </div>
              </section>
            ) : error ? (
              <div className="bg-red-600 text-white rounded-3xl p-6 flex items-start space-x-4 animate-in shake shadow-xl shadow-red-200/50">
                <AlertCircle className="w-6 h-6 shrink-0 mt-0.5 text-white" />
                <p className="text-[13px] font-bold uppercase tracking-tight leading-snug">{error}</p>
              </div>
            ) : (
              <div className="bg-white rounded-3xl py-12 px-6 text-center border-2 border-dashed border-black/5">
                 <Activity className="w-10 h-10 text-black/10 mx-auto mb-4" />
                 <p className="text-[13px] font-bold text-black/20 uppercase tracking-widest">Awaiting Clinical Payload</p>
              </div>
            )}
          </div>
        </div>
      </main>

     
    </div>
  )
}
