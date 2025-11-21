import React, { useState, useRef, useEffect } from 'react';

import { ArrowRight, Sparkles, Search, Check, Loader2, AlertTriangle, ChevronDown, X } from 'lucide-react';



// --- CONFIGURATION ---

const GOOGLE_MAPS_API_KEY = "AIzaSyGT2XWp6X7UJLZ1EkL3mxV4m7Gx4nv6wU";



/**

 * RaptorFlow v12: "Final Polish"

 * - Added: persistent "X" (Close) button on top-left.

 * - Added: "Let's Go" action button on the completion screen.

 * - UI: Maintained "Silent Focus" aesthetic.

 */



// --- THE FIXED 7 QUESTIONS ---

const INITIAL_QUESTIONS = [

  {

    id: 'q1',

    section: '01',

    category: 'Basics',

    title: 'What You Do',

    type: 'text',

    prompt: 'In simple words, what does your business do?',

    placeholder: 'e.g. "We build websites for small local shops" or "We sell a SaaS tool..."'

  },

  {

    id: 'q2',

    section: '01',

    category: 'Basics',

    title: 'The Offer',

    type: 'text',

    prompt: 'What do you actually sell, and what do people usually pay?',

    placeholder: 'Product/Service? One-time or Monthly? Rough price range?'

  },

  {

    id: 'q3',

    section: '02',

    category: 'Origin',

    title: 'Why',

    type: 'text',

    prompt: 'Why did you start this business?',

    placeholder: 'A few lines about what pushed you to do this.'

  },

  {

    id: 'q4',

    section: '02',

    category: 'Customers',

    title: 'Best Fit',

    type: 'text',

    prompt: 'Who are your best customers?',

    placeholder: 'Think of 2-3 examples. What business? What size? Who do you deal with?'

  },

  {

    id: 'q5',

    section: '02',

    category: 'Customers',

    title: 'Bad Fit',

    type: 'text',

    prompt: 'Who is usually not a good fit for you?',

    placeholder: 'Early stage? Low budget? Daily calls? Who do you avoid?'

  },

  {

    id: 'q6',

    section: '03',

    category: 'Location',

    title: 'Coordinates',

    type: 'map',

    prompt: 'Where is your business based, or where are most of your customers?',

    placeholder: 'Search for a city or drop a pin.'

  },

  {

    id: 'q7',

    section: '04',

    category: 'Reality',

    title: 'Snapshot',

    type: 'multi',

    prompt: "Let's look at where things stand right now.",

    fields: [

      { id: 'q7a', label: 'How do new customers find you right now?', placeholder: 'Referrals, Ads, Cold Email...' },

      { id: 'q7b', label: 'How much time can you spend on marketing weekly?', type: 'select', options: ['~2 hours', '3-5 hours', '6-10 hours', '10+ hours / Team'] },

      { id: 'q7c', label: 'If things go well in 3 months, what happens?', placeholder: 'e.g. "Book 5 calls/mo" or "Close 3 clients"' }

    ]

  }

];



// --- STATIC FALLBACK POOL ---

const FALLBACK_FOLLOW_UPS = [

  {

    category: 'Clarification',

    title: 'Focus',

    prompt: 'You mentioned a few different types of customers. For the next 3 months, which one do you want to focus on first?',

    placeholder: 'Pick one and describe it in a bit more detail.'

  },

  {

    category: 'Differentiation',

    title: 'The Edge',

    prompt: 'When someone chooses you instead of someone else, what do they usually say they liked about you?',

    placeholder: 'Why did they pick you over the other option?'

  }

];



// --- GEMINI API INTEGRATION ---



const generateGeminiQuestions = async (answers) => {

  const apiKey = import.meta.env.VITE_GEMINI_API_KEY || ""; // Use environment variable

  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`;



  let contextString = "Here is the client's onboarding intake so far:\n\n";

  

  INITIAL_QUESTIONS.forEach(q => {

    if (q.type === 'multi') {

      q.fields.forEach(field => {

        const ans = answers[field.id] || "Not answered";

        contextString += `Question: ${field.label}\nAnswer: ${ans}\n\n`;

      });

    } else if (q.type === 'map') {

       const loc = answers[q.id];

       const locStr = loc ? (loc.address || `${loc.lat}, ${loc.lng}`) : "Not provided";

       contextString += `Question: ${q.prompt}\nAnswer: ${locStr}\n\n`;

    } else {

      const ans = answers[q.id] || "Not answered";

      contextString += `Question: ${q.prompt}\nAnswer: ${ans}\n\n`;

    }

  });



  const systemInstruction = `

    You are an expert brand strategist reviewing a new client's intake form.

    Your goal is to identify 1-3 critical gaps, vague statements, or areas that need specific clarification to build a marketing strategy.

    

    Tone: Professional, "Normal Human", concise, slightly editorial. Not robotic.

    

    Task: Generate 1 to 3 follow-up questions based on their answers.

    - If they were vague about their customer, ask for specifics.

    - If they didn't mention constraints, ask about them.

    - If they didn't mention competitors, ask who they lose deals to.

    

    Return strictly a JSON array of objects. No markdown formatting.

  `;



  const payload = {

    contents: [{

      parts: [{ text: contextString + "\n\n" + systemInstruction }]

    }],

    generationConfig: {

      responseMimeType: "application/json",

      responseSchema: {

        type: "ARRAY",

        items: {

          type: "OBJECT",

          properties: {

            category: { type: "STRING" },

            title: { type: "STRING" },

            prompt: { type: "STRING" },

            placeholder: { type: "STRING" }

          },

          required: ["category", "title", "prompt", "placeholder"]

        }

      }

    }

  };



  const delays = [1000, 2000, 4000, 8000, 16000];

  

  for (let i = 0; i < delays.length; i++) {

    try {

      const response = await fetch(url, {

        method: 'POST',

        headers: { 'Content-Type': 'application/json' },

        body: JSON.stringify(payload)

      });



      if (!response.ok) throw new Error(`API Error: ${response.status}`);



      const data = await response.json();

      const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;

      

      if (!jsonText) throw new Error("No content generated");



      return JSON.parse(jsonText);



    } catch (error) {

      console.warn(`Gemini Attempt ${i + 1} failed:`, error);

      if (i === delays.length - 1) throw error; 

      await new Promise(resolve => setTimeout(resolve, delays[i]));

    }

  }

};



// --- HELPERS ---

const loadGoogleMapsScript = (callback) => {

  if (window.google && window.google.maps) {

    callback();

    return;

  }

  if (document.getElementById('google-maps-script')) {

     const checkInterval = setInterval(() => {

        if (window.google && window.google.maps) {

           clearInterval(checkInterval);

           callback();

        }

     }, 500);

     return; 

  }



  const script = document.createElement('script');

  script.id = 'google-maps-script';

  script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=places`;

  script.async = true;

  script.defer = true;

  script.onload = callback;

  document.head.appendChild(script);

};



// --- COMPONENTS ---



const GrainOverlay = () => (

  <div className="absolute inset-0 pointer-events-none z-0 opacity-[0.015] mix-blend-overlay" 

       style={{ 

         backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.6' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='1'/%3E%3C/svg%3E")` 

       }}>

  </div>

);



const InteractiveMap = ({ onLocationSelect, initialValue }) => {

  const mapRef = useRef(null);

  const searchInputRef = useRef(null);

  const mapObj = useRef(null);

  const markerObj = useRef(null);

  const [scriptLoaded, setScriptLoaded] = useState(false);

  const [authWarning, setAuthWarning] = useState(false);



  useEffect(() => {

    window.gm_authFailure = () => {

      console.warn("Google Maps API Key Warning - Map may be degraded");

      setAuthWarning(true);

    };



    loadGoogleMapsScript(() => {

        if (

          window.google &&

          window.google.maps &&

          typeof window.google.maps.Map === "function"

        ) {

          setScriptLoaded(true);

        } else {

          console.error("Google Maps failed to initialize.");

          setAuthWarning(true);

        }

    });

  }, []);



  useEffect(() => {

    if (!scriptLoaded || !mapRef.current || !window.google) return;



    try {

        const paris = { lat: 48.8566, lng: 2.3522 };

        const mapStyles = [

          { "elementType": "geometry", "stylers": [{ "color": "#fdfcf9" }] },

          { "elementType": "labels.icon", "stylers": [{ "visibility": "off" }] },

          { "elementType": "labels.text.fill", "stylers": [{ "color": "#56534b" }] },

          { "elementType": "labels.text.stroke", "stylers": [{ "color": "#fdfcf9" }] },

          { "featureType": "administrative.land_parcel", "elementType": "labels.text.fill", "stylers": [{ "color": "#a7a399" }] },

          { "featureType": "poi", "elementType": "geometry", "stylers": [{ "color": "#f7f5f0" }] },

          { "featureType": "poi", "elementType": "labels.text.fill", "stylers": [{ "color": "#7d7a72" }] },

          { "featureType": "road", "elementType": "geometry", "stylers": [{ "color": "#ffffff" }] },

          { "featureType": "road.arterial", "elementType": "labels.text.fill", "stylers": [{ "color": "#7d7a72" }] },

          { "featureType": "road.highway", "elementType": "geometry", "stylers": [{ "color": "#efede5" }] },

          { "featureType": "road.highway", "elementType": "labels.text.fill", "stylers": [{ "color": "#56534b" }] },

          { "featureType": "water", "elementType": "geometry", "stylers": [{ "color": "#f1ece4" }] },

          { "featureType": "water", "elementType": "labels.text.fill", "stylers": [{ "color": "#a7a399" }] }

        ];



        const map = new window.google.maps.Map(mapRef.current, {

          center: paris,

          zoom: 3,

          styles: mapStyles,

          disableDefaultUI: true,

          zoomControl: true,

        });



        const marker = new window.google.maps.Marker({

          map: map,

          draggable: true,

          animation: window.google.maps.Animation.DROP,

        });



        if (searchInputRef.current) {

            const searchBox = new window.google.maps.places.SearchBox(searchInputRef.current);



            map.addListener('bounds_changed', () => {

              searchBox.setBounds(map.getBounds());

            });



            searchBox.addListener('places_changed', () => {

              const places = searchBox.getPlaces();

              if (places.length === 0) return;



              const place = places[0];

              if (!place.geometry || !place.geometry.location) return;



              map.setCenter(place.geometry.location);

              map.setZoom(12);

              marker.setPosition(place.geometry.location);

              marker.setVisible(true);



              onLocationSelect({

                address: place.formatted_address,

                lat: place.geometry.location.lat(),

                lng: place.geometry.location.lng()

              });

            });

        }



        map.addListener('click', (e) => {

          marker.setPosition(e.latLng);

          marker.setVisible(true);

          

          onLocationSelect({

            lat: e.latLng.lat(),

            lng: e.latLng.lng(),

            address: `Pinned Location (${e.latLng.lat().toFixed(4)}, ${e.latLng.lng().toFixed(4)})`

          });

        });



        mapObj.current = map;

        markerObj.current = marker;

    } catch (e) {

        console.error("Map Init Error:", e);

    }



  }, [scriptLoaded]);



  return (

    <div className="w-full flex flex-col items-center space-y-8 animate-fade-in">

      <div className="relative w-full max-w-2xl z-20">

        <div className="absolute inset-0 bg-gradient-to-br from-white via-neutral-50 to-white rounded-[2rem] border border-neutral-200/70 shadow-[0_12px_30px_rgba(15,17,19,0.04)]" />

        <div className="relative flex items-center gap-4 p-6">

          <div className="flex-shrink-0 w-12 h-12 rounded-full border border-neutral-200 bg-white flex items-center justify-center shadow-sm">

            <Search className="text-neutral-500" size={18} />

          </div>

          <input 

            ref={searchInputRef}

            type="text" 

            placeholder="Search for your city or drop a pin on the map..." 

            className="flex-1 bg-transparent border-none outline-none text-neutral-900 placeholder:text-neutral-400 font-sans text-sm focus:ring-0"

          />

        </div>

      </div>



      <div className="w-full max-w-4xl h-[45vh] md:h-[55vh] relative rounded-[2rem] border border-neutral-200/70 overflow-hidden shadow-[0_12px_30px_rgba(15,17,19,0.04)] bg-neutral-50">

         {authWarning && (

            <div className="absolute top-4 left-4 right-4 bg-amber-50/95 backdrop-blur-sm text-amber-800 text-[10px] uppercase font-mono tracking-[0.2em] py-3 px-4 rounded-xl border border-amber-200 z-30 flex items-center justify-center space-x-2 shadow-lg">

               <AlertTriangle size={14} />

               <span>Maps API Key Issue - Functionality may be limited</span>

            </div>

         )}

         

         <div ref={mapRef} className="w-full h-full" />

         

         {!scriptLoaded && (

           <div className="absolute inset-0 flex items-center justify-center bg-neutral-50 text-neutral-400 text-xs font-mono uppercase tracking-[0.3em] z-0">

             <div className="flex flex-col items-center gap-3">

               <Loader2 className="animate-spin" size={20} />

               <span>Initializing Cartographic Interface</span>

             </div>

           </div>

         )}

      </div>

      

      {initialValue && initialValue.address && (

        <div className="flex items-center gap-3 text-neutral-700 bg-white px-6 py-3 border border-neutral-200 shadow-sm">

           <div className="w-6 h-6 rounded-full bg-neutral-900 flex items-center justify-center">

             <Check size={12} className="text-white" />

           </div>

           <div className="flex flex-col">

             <span className="text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-500">Location Selected</span>

             <span className="text-sm font-medium text-neutral-900">{initialValue.address}</span>

           </div>

        </div>

      )}

    </div>

  );

};

// Custom Dropdown Component with styled menu
const CustomDropdown = ({ value, options, onChange, placeholder = "Select an option" }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleSelect = (option) => {
    onChange(option);
    setIsOpen(false);
  };

  const displayValue = value || placeholder;
  const isPlaceholder = !value;

  return (
    <div className="relative w-full" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full bg-white/50 backdrop-blur-sm border border-neutral-200 rounded-lg px-6 py-4 pr-10 text-lg font-serif italic transition-all appearance-none cursor-pointer shadow-sm text-left flex items-center justify-between ${
          isPlaceholder ? 'text-neutral-400' : 'text-neutral-900'
        } hover:border-neutral-300 focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-neutral-900 ${
          isOpen ? 'border-neutral-900 ring-2 ring-neutral-900' : ''
        }`}
      >
        <span>{displayValue}</span>
        <ChevronDown 
          size={18} 
          className={`text-neutral-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-white border border-neutral-200 rounded-lg shadow-lg overflow-hidden" style={{ animation: 'dropdownFadeIn 0.15s ease-out' }}>
          <div className="py-2">
            {options.map((option, idx) => (
              <button
                key={option}
                type="button"
                onClick={() => handleSelect(option)}
                className={`w-full px-6 py-3 text-left text-lg font-serif italic transition-colors ${
                  value === option
                    ? 'bg-neutral-100 text-neutral-900 font-medium'
                    : 'text-neutral-700 hover:bg-neutral-50 hover:text-neutral-900'
                } ${idx === 0 ? 'rounded-t-lg' : ''} ${idx === options.length - 1 ? 'rounded-b-lg' : ''}`}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const MultiInputStep = ({ question, answers, onChange }) => {

  return (

    <div className="w-full max-w-6xl animate-fade-in">

      <p className="font-display text-3xl md:text-5xl text-neutral-900 mb-20 leading-tight text-center">

        {question.prompt}

      </p>

      

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 w-full">

        {question.fields.map((field, idx) => (

          <div key={field.id} className="flex flex-col items-center space-y-6 group w-full">

             <label className="text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-500 group-focus-within:text-neutral-900 transition-colors text-center">

               {field.label}

             </label>

             

             {field.type === 'select' ? (

                <CustomDropdown
                  value={answers[field.id] || ''}
                  options={field.options}
                  onChange={(value) => onChange(field.id, value)}
                  placeholder="Select an option"
                />

             ) : (

                <textarea

                  value={answers[field.id] || ''}

                  onChange={(e) => onChange(field.id, e.target.value)}

                  placeholder={field.placeholder}

                  rows={1}

                  className="w-full bg-transparent border-b border-neutral-200 py-4 text-xl font-serif italic text-neutral-900 focus:outline-none focus:border-neutral-900 transition-all placeholder:text-neutral-400 text-center resize-none min-h-[60px]"

                  onInput={(e) => {

                      e.target.style.height = 'auto';

                      e.target.style.height = e.target.scrollHeight + 'px';

                  }}

                />

             )}

          </div>

        ))}

      </div>

    </div>

  );

};



const StandardInput = ({ question, value, onChange, onBlur }) => {

  return (

    <div className="group animate-fade-in flex flex-col items-center text-center w-full z-10 max-w-5xl">

      <div className="flex items-center gap-3 mb-6">

        <span className="text-[10px] font-mono uppercase tracking-[0.4em] text-neutral-500">

          {question.title}

        </span>

        <span className="h-px w-8 bg-neutral-200" />

      </div>

      

      <p className="font-display text-4xl md:text-6xl text-neutral-900 mb-16 leading-[1.1] tracking-tight antialiased">

        {question.prompt}

      </p>



      <div className="relative w-full max-w-3xl">

        <div className="absolute inset-0 bg-gradient-to-br from-white via-neutral-50 to-white rounded-[2rem] border border-neutral-200/70 shadow-[0_12px_30px_rgba(15,17,19,0.04)]" />

        <textarea

          autoFocus={true}

          value={value || ''}

          onChange={(e) => onChange(question.id, e.target.value)}

          onBlur={() => onBlur && onBlur(question.id)}

          placeholder={question.placeholder}

          className="relative w-full bg-transparent border-none text-xl md:text-2xl text-neutral-900 py-8 px-8 focus:outline-none transition-all duration-700 placeholder:text-neutral-400 placeholder:font-light font-serif italic resize-none min-h-[120px] text-center leading-relaxed selection:bg-neutral-900 selection:text-white rounded-[2rem]"

        />

      </div>

    </div>

  );

};



const ProcessingScreen = () => (

   <div className="flex flex-col items-center justify-center space-y-8 animate-fade-in max-w-xl">

      <div className="relative">

        <div className="absolute inset-0 bg-gradient-to-br from-white via-neutral-50 to-white rounded-full border border-neutral-200/70 shadow-[0_12px_30px_rgba(15,17,19,0.04)] w-20 h-20" />

        <Loader2 className="relative animate-spin text-neutral-900" size={48} />

      </div>

      <div className="text-center space-y-3">

        <p className="font-display text-2xl text-neutral-900">Analyzing your inputs...</p>

        <p className="text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-500">Using Gemini 2.5 Flash to detect strategy gaps</p>

      </div>

   </div>

);



const ProgressBar = ({ current, total }) => {

  const progress = ((current + 1) / total) * 100;

  return (

    <div className="fixed bottom-0 left-0 w-full z-50 bg-white/80 backdrop-blur-xl border-t border-neutral-200/70 pt-4 pb-0 shadow-[0_-4px_20px_rgba(15,17,19,0.04)]">

       <div className="flex justify-between items-end px-8 pb-3 text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-500">

          <span>Protocol {String(current + 1).padStart(2, '0')} / {String(total).padStart(2, '0')}</span>

          <span>{Math.round(progress)}%</span>

       </div>

       <div className="h-1 bg-neutral-100 w-full">

          <div 

            className="h-full bg-neutral-900 transition-all duration-1000 ease-out" 

            style={{ width: `${progress}%` }}

          ></div>

       </div>

    </div>

  );

};



// --- MAIN APP ---



export default function RaptorFlow({ onClose }) {

  const [questions, setQuestions] = useState(INITIAL_QUESTIONS);

  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  const [answers, setAnswers] = useState({});

  const [status, setStatus] = useState('input'); 

  

  const currentQuestion = questions[currentStepIndex];

  const mainScrollRef = useRef(null);



  const handleAnswer = (id, value) => {

    setAnswers(prev => ({ ...prev, [id]: value }));

  };



  const runAIAnalysis = async () => {

    setStatus('analyzing');

    

    try {

      const aiQuestions = await generateGeminiQuestions(answers);

      

      // Process AI questions to fit our schema

      const processedQuestions = aiQuestions.map((q, idx) => ({

        id: `ai_${Date.now()}_${idx}`,

        section: 'AI CHECK',

        category: q.category,

        title: q.title,

        type: 'text',

        prompt: q.prompt,

        placeholder: q.placeholder

      }));



      setQuestions(prev => [...prev, ...processedQuestions]);

    } catch (error) {

      console.error("AI Generation failed, using fallbacks:", error);

      // Fallback logic

      const fallbackQs = FALLBACK_FOLLOW_UPS.map((q, idx) => ({

        id: `fallback_${idx}`,

        section: 'AI CHECK',

        category: q.category,

        title: q.title,

        type: 'text',

        prompt: q.prompt,

        placeholder: q.placeholder

      }));

      setQuestions(prev => [...prev, ...fallbackQs]);

    } finally {

      setStatus('followup');

      setCurrentStepIndex(prev => prev + 1);

    }

  };



  const nextStep = () => {

    if (currentQuestion.id === 'q7') {

       runAIAnalysis();

       return;

    }



    if (currentStepIndex < questions.length - 1) {

      setCurrentStepIndex(prev => prev + 1);

      if (mainScrollRef.current) mainScrollRef.current.scrollTop = 0;

    } else {

       setStatus('complete');

    }

  };



  const prevStep = () => {

    if (currentStepIndex > 0) {

      setCurrentStepIndex(prev => prev - 1);

    }

  };



  const renderInput = () => {

    if (status === 'analyzing') return <ProcessingScreen />;

    if (status === 'complete') return (

      <div className="text-center animate-fade-in flex flex-col items-center max-w-2xl">

        <div className="mb-8">

          <div className="text-[10px] font-mono uppercase tracking-[0.4em] text-neutral-500 mb-4">Protocol Complete</div>

          <h1 className="font-display text-5xl md:text-7xl mb-4 text-neutral-900">All Set.</h1>

          <p className="text-sm text-neutral-600 font-serif italic">Your couture intake has been captured.</p>

        </div>

        

        <button 

            onClick={() => {
              console.log("Submitting data:", answers);
              if (onClose) onClose();
            }} 

            className="group relative inline-flex items-center gap-3 border border-neutral-900 bg-neutral-900 text-white px-10 py-4 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-neutral-800 transition-all shadow-sm hover:shadow-lg mt-8"

        >

            <span>Let's Go</span>

            <span className="inline-flex h-6 w-6 items-center justify-center rounded-full border border-current text-[10px] group-hover:bg-white group-hover:text-neutral-900 transition-colors">

              →

            </span>

        </button>

      </div>

    );



    switch (currentQuestion.type) {

      case 'map':

        return (

          <InteractiveMap 

            onLocationSelect={(loc) => handleAnswer(currentQuestion.id, loc)} 

            initialValue={answers[currentQuestion.id]}

          />

        );

      case 'multi':

        return (

          <MultiInputStep 

             question={currentQuestion} 

             answers={answers} 

             onChange={handleAnswer} 

          />

        );

      default:

        return (

          <StandardInput 

             key={currentQuestion.id} 

             question={currentQuestion}

             value={answers[currentQuestion.id]}

             onChange={handleAnswer}

          />

        );

    }

  };



  return (

    <div className="fixed inset-0 z-[9999] flex h-screen w-screen bg-[var(--color-neutral-50)] text-neutral-900 overflow-hidden font-sans selection:bg-neutral-900 selection:text-white" style={{ backgroundImage: 'radial-gradient(circle at top left, rgba(255,255,255,0.9), transparent 55%), radial-gradient(circle at 20% 40%, rgba(255,255,255,0.7), transparent 50%)' }}>

      <GrainOverlay />



      {/* Persistent X Button */}

      <button 

        className="absolute top-8 left-8 z-50 w-10 h-10 flex items-center justify-center text-neutral-400 hover:text-neutral-900 transition-colors hover:bg-white rounded-full border border-neutral-200/70 shadow-sm backdrop-blur-sm"

        onClick={() => {
          if (onClose) {
            onClose();
          } else {
            window.location.reload();
          }
        }} 

      >

        <X size={18} />

      </button>



      <div ref={mainScrollRef} className="flex-grow flex flex-col justify-center items-center px-6 md:px-8 relative z-10">

        <div className="w-full flex flex-col items-center pb-12 max-w-7xl">

           

           {status !== 'analyzing' && status !== 'complete' && (

             <div className="flex items-center gap-4 mb-12 animate-fade-in">

                <div className="flex items-center gap-3 text-[10px] font-mono uppercase tracking-[0.4em] text-neutral-500">

                  <span className="bg-neutral-900 text-white px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.2em]">

                    {currentQuestion.section}

                  </span>

                  <span className="h-px w-6 bg-neutral-200" />

                  <span>{currentQuestion.category}</span>

                </div>

             </div>

           )}



           {renderInput()}



           {status !== 'analyzing' && status !== 'complete' && (

             <div className="mt-24 flex items-center space-x-12 animate-fade-in">

                <button 

                    onClick={prevStep}

                    disabled={currentStepIndex === 0}

                    className={`font-sans text-[10px] font-bold uppercase tracking-widest border-b border-transparent hover:border-black transition-all duration-500 pb-1 ${currentStepIndex === 0 ? 'opacity-0 cursor-default' : 'text-stone-400 hover:text-black'}`}

                >

                    Back

                </button>



                <button 

                    onClick={nextStep}

                    className="group relative inline-flex items-center gap-3 border border-neutral-900 bg-neutral-900 text-white px-8 py-4 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-neutral-800 transition-all shadow-sm hover:shadow-lg"

                >

                    <span>

                        {currentQuestion.id === 'q7' ? 'Analyze' : (currentStepIndex === questions.length - 1 ? 'Finish' : 'Next')}

                    </span>

                    <span className="inline-flex h-6 w-6 items-center justify-center rounded-full border border-current text-[10px] group-hover:bg-white group-hover:text-neutral-900 transition-colors">

                        {currentQuestion.id === 'q7' ? <Sparkles size={12} /> : '→'}

                    </span>

                </button>

             </div>

           )}

        </div>

      </div>

      

      {status !== 'complete' && (

         <ProgressBar 

           current={currentStepIndex} 

           total={questions.length} 

         />

      )}

    </div>

  );

}


