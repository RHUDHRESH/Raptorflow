import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import onboardingApi from '../api/onboarding';
import {
  ArrowRight,
  ArrowLeft,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Loader2,
  MapPin,
  Globe,
  Target,
  MousePointer2,
  RefreshCw,
  ChevronRight
} from 'lucide-react';
import { LuxeHeading, LuxeButton, LuxeCard, LuxeInput, LuxeTextarea } from './ui/PremiumUI';

const steps = [
  { id: 'brain_dump', title: 'Identity' },
  { id: 'context_review', title: 'Review' },
  { id: 'axis_selection', title: 'Audience' },
  { id: 'positioning_map', title: 'Value' },
  { id: 'final_recap', title: 'Narrative' },
  { id: 'battlefield', title: 'Battlefield' },
  { id: 'tribes', title: 'Tribes' }
];

export default function Onboarding() {
  const [currentStep, setCurrentStep] = useState('brain_dump');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // State
  const [inputs, setInputs] = useState({
    rawText: '',
    website: '',
    pitch: '',
    industry: ''
  });
  
  const [contextData, setContextData] = useState(null);
  const [axesData, setAxesData] = useState(null);
  const [selectedFrameId, setSelectedFrameId] = useState(null);
  const [position, setPosition] = useState({ x: 50, y: 50 });
  
  const [competitorData, setCompetitorData] = useState(null);
  const [icpData, setIcpData] = useState(null);
  const [selectedIcps, setSelectedIcps] = useState([]);

  const navigate = useNavigate();
  const { markOnboardingComplete, user } = useAuth();

  // Handlers
  const handleBrainDumpSubmit = async () => {
    if (!inputs.rawText) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await onboardingApi.analyzeContext({
        raw_text: inputs.rawText,
        website: inputs.website,
        pitch: inputs.pitch,
        industry: inputs.industry
      });
      
      if (response.extraction) {
         // Handle potential vertex AI raw response or structured JSON
         // For now assume it's structured or we parse it
         let extracted = response.extraction;
         if (typeof extracted === 'string') {
             try {
                 // Attempt to extract JSON block from markdown
                 const jsonMatch = extracted.match(/```json\n([\s\S]*?)\n```/) || extracted.match(/{[\s\S]*}/);
                 if (jsonMatch) {
                     extracted = JSON.parse(jsonMatch[1] || jsonMatch[0]);
                 }
             } catch (e) {
                 console.warn("Failed to parse JSON from AI", e);
                 // Fallback structure
                 extracted = {
                     core_line: "We are a business.",
                     narrative: { who_you_serve: "Customers", main_wound: "Problems" },
                     category: inputs.industry || "General"
                 };
             }
         }
         setContextData(extracted);
         setCurrentStep('context_review');
      }
    } catch (err) {
      console.error(err);
      setError("Failed to analyze context. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleContextConfirm = async () => {
      setIsLoading(true);
      try {
          const response = await onboardingApi.generateAxes({
              category: contextData.category,
              narrative: contextData.narrative,
              keywords: contextData.keywords || []
          });
          
          if (response.frames) {
              let frames = response.frames;
               if (typeof frames === 'string') {
                   try {
                       const jsonMatch = frames.match(/```json\n([\s\S]*?)\n```/) || frames.match(/{[\s\S]*}/);
                       if (jsonMatch) {
                           const parsed = JSON.parse(jsonMatch[1] || jsonMatch[0]);
                           frames = parsed.frames;
                       }
                   } catch (e) {
                       console.warn("Failed to parse Axes JSON", e);
                   }
               }
               // Ensure frames is an array
               if (!Array.isArray(frames) && frames.frames) frames = frames.frames;
               
              setAxesData(frames);
              setSelectedFrameId(frames[0]?.id);
              setCurrentStep('axis_selection');
          }
      } catch (err) {
          console.error(err);
          setError("Failed to generate positioning frames.");
      } finally {
          setIsLoading(false);
      }
  };
  
  const handleFrameSelect = () => {
      setCurrentStep('positioning_map');
  };

  const handlePositionConfirm = () => {
      setCurrentStep('final_recap');
  };
  
  const handleFinalLock = async () => {
      setIsLoading(true);
      try {
          const frame = axesData.find(f => f.id === selectedFrameId);
          
          // Save profile partial
          await onboardingApi.updateProfile({
              context: contextData,
              positioning: {
                  frame_id: selectedFrameId,
                  coordinates: position,
                  frame_data: frame
              },
              inputs: inputs
          });
          
          setCurrentStep('battlefield');
          
          // Trigger competitor analysis
          fetchCompetitors(frame);
          
      } catch (err) {
          console.error(err);
          setError("Failed to save positioning.");
          setIsLoading(false);
      } 
  };
  
  const fetchCompetitors = async (frame) => {
      setIsLoading(true);
      try {
          const response = await onboardingApi.analyzeCompetitors({
              industry: inputs.industry || contextData.category,
              context_summary: contextData,
              axis_frame: frame
          });
          
          if (response.analysis) {
               let data = response.analysis;
               if (typeof data === 'string') {
                   try {
                       const jsonMatch = data.match(/```json\n([\s\S]*?)\n```/) || data.match(/{[\s\S]*}/);
                       if (jsonMatch) {
                           data = JSON.parse(jsonMatch[1] || jsonMatch[0]);
                       }
                   } catch (e) { console.warn("Failed to parse competitor JSON", e); }
               }
               setCompetitorData(data);
          }
      } catch (err) {
          console.error(err);
          // Non-blocking error
      } finally {
          setIsLoading(false);
      }
  };
  
  const handleBattlefieldComplete = () => {
      setCurrentStep('tribes');
      fetchICPs();
  };
  
  const fetchICPs = async () => {
      setIsLoading(true);
      try {
          const frame = axesData.find(f => f.id === selectedFrameId);
          const response = await onboardingApi.proposeICPs({
              industry: inputs.industry || contextData.category,
              context_summary: contextData,
              positioning: {
                  frame_data: frame,
                  coordinates: position
              }
          });
          
          if (response.proposal) {
               let data = response.proposal;
               if (typeof data === 'string') {
                   try {
                       const jsonMatch = data.match(/```json\n([\s\S]*?)\n```/) || data.match(/{[\s\S]*}/);
                       if (jsonMatch) {
                           data = JSON.parse(jsonMatch[1] || jsonMatch[0]);
                       }
                   } catch (e) { console.warn("Failed to parse ICP JSON", e); }
               }
               setIcpData(data);
               if (data.icps) {
                   setSelectedIcps(data.icps.map((_, i) => i)); // Select all by default
               }
          }
      } catch (err) {
          console.error(err);
      } finally {
          setIsLoading(false);
      }
  };
  
  const handleTribesComplete = async () => {
      setIsLoading(true);
      try {
          // First save the selected tribes data
          await onboardingApi.updateProfile({
              competitors: competitorData,
              icps: selectedIcps.map(i => icpData?.icps[i]),
              onboarding_completed: true
          });
          
          // Then trigger the background guild (Act IV logic)
          if (sessionId) {
              await onboardingApi.complete(sessionId);
          }
          
          await markOnboardingComplete();
          navigate('/dashboard');
      } catch (err) {
          console.error(err);
          setError("Failed to complete onboarding.");
      } finally {
          setIsLoading(false);
      }
  };

  // Renderers
  const renderBrainDump = () => (
    <div className="max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
        {/* Left: Inputs (Task 20) */}
        <div className="space-y-8">
            <div className="space-y-4">
                <LuxeHeading level={2}>The Identity</LuxeHeading>
                <p className="text-lg text-neutral-500 leading-relaxed">
                    Strategy starts with the truth. Dump your pitch, your rant about competitors, or your website copy. We'll extract the signal from the noise.
                </p>
            </div>
            
            <div className="space-y-6">
                <LuxeTextarea
                    label="THE BRAIN DUMP *"
                    value={inputs.rawText}
                    onChange={e => setInputs({...inputs, rawText: e.target.value})}
                    className="h-64 text-base p-4 bg-white"
                    placeholder="e.g. We build software for dentists who hate technology. Our competitors are clunky and expensive..."
                />
                
                <div className="grid grid-cols-2 gap-6">
                    <LuxeInput
                        label="Website (Optional)"
                        value={inputs.website}
                        onChange={e => setInputs({...inputs, website: e.target.value})}
                        placeholder="https://..."
                    />
                    <LuxeInput
                        label="Industry / Category"
                        value={inputs.industry}
                        onChange={e => setInputs({...inputs, industry: e.target.value})}
                        placeholder="e.g. B2B SaaS"
                    />
                </div>
                
                <div className="pt-4">
                    <LuxeButton
                        onClick={handleBrainDumpSubmit}
                        disabled={!inputs.rawText || isLoading}
                        size="lg"
                        className="w-full"
                        isLoading={isLoading}
                        icon={Sparkles}
                    >
                        Analyze Identity
                    </LuxeButton>
                </div>
            </div>
        </div>

        {/* Right: Preview / Context (Task 20) */}
        <div className="hidden lg:block sticky top-8">
            <div className="bg-white border border-neutral-200 p-8 rounded-xl shadow-sm space-y-8">
                <div className="space-y-2">
                    <div className="text-xs font-bold uppercase tracking-widest text-neutral-400">Live Preview</div>
                    <h3 className="font-display text-2xl text-neutral-900">
                        {inputs.industry || "Your Category"}
                    </h3>
                </div>

                <div className="space-y-6">
                    <div className="p-6 bg-neutral-50 border border-neutral-100 rounded-lg">
                        <div className="flex items-start gap-3 mb-3">
                            <div className="w-8 h-8 rounded bg-white border border-neutral-200 flex items-center justify-center shrink-0">
                                <Target className="w-4 h-4 text-neutral-900" />
                            </div>
                            <div>
                                <div className="text-sm font-bold text-neutral-900">The Goal</div>
                                <p className="text-sm text-neutral-500 mt-1 leading-relaxed">
                                    We are looking for the "Single Minded Proposition" — the one thing you can own in the prospect's mind.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="p-6 bg-neutral-50 border border-neutral-100 rounded-lg">
                        <div className="flex items-start gap-3 mb-3">
                            <div className="w-8 h-8 rounded bg-white border border-neutral-200 flex items-center justify-center shrink-0">
                                <AlertCircle className="w-4 h-4 text-neutral-900" />
                            </div>
                            <div>
                                <div className="text-sm font-bold text-neutral-900">The Anti-Position</div>
                                <p className="text-sm text-neutral-500 mt-1 leading-relaxed">
                                    Great positioning also defines who you are NOT. We will identify your enemies (old ways, bad habits, competitors).
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="pt-6 border-t border-neutral-100 text-center">
                    <p className="text-xs text-neutral-400 uppercase tracking-widest">Powered by RaptorFlow Intelligence</p>
                </div>
            </div>
        </div>
    </div>
  );
  
  const renderContextReview = () => (
      <div className="max-w-5xl mx-auto h-full flex flex-col">
          <div className="mb-8">
              <LuxeHeading level={2}>The Mirror</LuxeHeading>
              <p className="text-lg text-neutral-500 mt-2">Based on your input, this is your strategic signal.</p>
          </div>
          
          <div className="grid md:grid-cols-12 gap-8 flex-1">
              {/* Left: Parsed Summary */}
              <div className="md:col-span-4 space-y-6">
                  <LuxeCard title="We Heard">
                      <div className="space-y-4 text-sm">
                          <div>
                              <span className="font-bold block text-neutral-900">Category</span>
                              <span className="text-neutral-600">{contextData?.category}</span>
                          </div>
                          <div>
                              <span className="font-bold block text-neutral-900">Target</span>
                              <span className="text-neutral-600">{contextData?.narrative?.who_you_serve}</span>
                          </div>
                          <div>
                              <span className="font-bold block text-neutral-900">Main Pain</span>
                              <span className="text-neutral-600">{contextData?.narrative?.main_wound}</span>
                          </div>
                      </div>
                  </LuxeCard>
                  
                  <div className="bg-neutral-900 p-6 rounded-lg text-white">
                      <div className="flex items-start gap-3">
                          <Sparkles className="w-5 h-5 text-neutral-400 flex-shrink-0 mt-0.5" />
                          <p className="text-sm leading-relaxed text-neutral-300">
                              We've filtered out the noise. This is the strategic core you can build on.
                          </p>
                      </div>
                  </div>
              </div>
              
              {/* Right: Storycard */}
              <div className="md:col-span-8">
                  <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white border border-neutral-200 shadow-xl rounded-xl p-8 h-full flex flex-col relative overflow-hidden"
                  >
                      <div className="absolute top-0 left-0 w-full h-1 bg-neutral-900" />
                      <div className="flex-1">
                          <div className="mb-8">
                              <h3 className="text-3xl font-display font-medium leading-tight mb-6 text-neutral-900">
                                  {contextData?.core_line}
                              </h3>
                          </div>
                          
                          <div className="space-y-8">
                              <div>
                                  <h4 className="font-bold text-sm uppercase tracking-widest text-neutral-400 mb-3 flex items-center gap-2">
                                      The Promise
                                  </h4>
                                  <p className="text-lg text-neutral-700 leading-relaxed">
                                      You help <span className="font-medium text-neutral-900">{contextData?.narrative?.who_you_serve}</span> overcome <span className="font-medium text-neutral-900">{contextData?.narrative?.main_wound}</span>.
                                  </p>
                              </div>
                              
                              <div>
                                  <h4 className="font-bold text-sm uppercase tracking-widest text-neutral-400 mb-3 flex items-center gap-2">
                                      The Anti-Position
                                  </h4>
                                  <p className="text-lg text-neutral-700 leading-relaxed">
                                      You refuse to be: <span className="italic text-neutral-900">{contextData?.narrative?.what_you_are_not}</span>.
                                  </p>
                              </div>
                              
                              {contextData?.proof_points?.length > 0 && (
                                  <div>
                                      <h4 className="font-bold text-sm uppercase tracking-widest text-neutral-400 mb-3">Evidence</h4>
                                      <ul className="space-y-2 text-neutral-600">
                                          {contextData.proof_points.map((p, i) => (
                                              <li key={i} className="flex items-start gap-2">
                                                  <div className="w-1.5 h-1.5 rounded-full bg-neutral-300 mt-2 shrink-0" />
                                                  {p}
                                              </li>
                                          ))}
                                      </ul>
                                  </div>
                              )}
                          </div>
                      </div>
                      
                      <div className="pt-8 mt-8 border-t border-neutral-100 flex justify-end gap-4">
                          <LuxeButton 
                            variant="ghost"
                            onClick={() => setCurrentStep('brain_dump')}
                          >
                              Edit Identity
                          </LuxeButton>
                          <LuxeButton 
                            onClick={handleContextConfirm}
                            disabled={isLoading}
                            isLoading={isLoading}
                            icon={CheckCircle2}
                          >
                             Confirm Strategy
                          </LuxeButton>
                      </div>
                  </motion.div>
              </div>
          </div>
      </div>
  );
  
  const renderAxisSelection = () => (
      <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
              <LuxeHeading level={2} className="mb-4">Choose your Battlefield.</LuxeHeading>
              <p className="text-lg text-neutral-500">How do you want to frame your value against competitors?</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
              {axesData?.map((frame) => {
                  const isSelected = selectedFrameId === frame.id;
                  return (
                      <motion.div
                        key={frame.id}
                        onClick={() => setSelectedFrameId(frame.id)}
                        whileHover={{ y: -4 }}
                        className={`
                            cursor-pointer text-left p-8 rounded-xl border transition-all duration-200 h-full flex flex-col
                            ${isSelected 
                                ? 'border-neutral-900 bg-neutral-900 text-white shadow-2xl ring-1 ring-neutral-900' 
                                : 'border-neutral-200 bg-white hover:border-neutral-300 hover:shadow-md'
                            }
                        `}
                      >
                          <div className="mb-8">
                              <h3 className="font-display text-xl font-medium mb-2">{frame.name}</h3>
                          </div>
                          
                          <div className="space-y-4 flex-1">
                              <div className={`p-4 rounded-lg ${isSelected ? 'bg-white/10' : 'bg-neutral-50'}`}>
                                  <div className="text-[10px] uppercase tracking-widest opacity-60 mb-1">X-Axis</div>
                                  <div className="font-medium text-sm">{frame.x_axis.label}</div>
                              </div>
                              <div className={`p-4 rounded-lg ${isSelected ? 'bg-white/10' : 'bg-neutral-50'}`}>
                                  <div className="text-[10px] uppercase tracking-widest opacity-60 mb-1">Y-Axis</div>
                                  <div className="font-medium text-sm">{frame.y_axis.label}</div>
                              </div>
                          </div>
                          
                          <div className="mt-8 pt-6 border-t border-white/10 flex items-center gap-3 text-sm font-medium opacity-80">
                              <div className={`w-5 h-5 rounded-full border flex items-center justify-center ${isSelected ? 'border-white' : 'border-neutral-300'}`}>
                                  {isSelected && <div className="w-2.5 h-2.5 bg-white rounded-full" />}
                              </div>
                              {isSelected ? 'Selected Frame' : 'Select Frame'}
                          </div>
                      </motion.div>
                  );
              })}
          </div>
          
          <div className="mt-12 flex justify-center">
              <LuxeButton
                onClick={handleFrameSelect}
                disabled={!selectedFrameId}
                size="lg"
                icon={ArrowRight}
              >
                  Map My Position
              </LuxeButton>
          </div>
      </div>
  );
  
  const renderPositioningMap = () => {
      const frame = axesData?.find(f => f.id === selectedFrameId);
      if (!frame) return null;
      
      return (
          <div className="max-w-6xl mx-auto grid md:grid-cols-12 gap-12 h-full items-center">
              {/* Controls */}
              <div className="md:col-span-4 space-y-10">
                  <div className="space-y-4">
                      <LuxeHeading level={2}>Where do you sit?</LuxeHeading>
                      <p className="text-lg text-neutral-500">Be honest. You can't be everything to everyone.</p>
                  </div>
                  
                  <div className="space-y-8">
                      <div className="space-y-4">
                          <label className="font-bold text-sm block text-neutral-900">{frame.x_axis.question}</label>
                          <div className="flex justify-between text-[10px] text-neutral-400 font-bold uppercase tracking-widest">
                              <span>{frame.x_axis.left_label}</span>
                              <span>{frame.x_axis.right_label}</span>
                          </div>
                          <input 
                            type="range" 
                            min="0" max="100" 
                            value={position.x}
                            onChange={e => setPosition({...position, x: parseInt(e.target.value)})}
                            className="w-full h-1 bg-neutral-200 rounded-lg appearance-none cursor-pointer accent-neutral-900"
                          />
                      </div>
                      
                      <div className="space-y-4">
                          <label className="font-bold text-sm block text-neutral-900">{frame.y_axis.question}</label>
                          <div className="flex justify-between text-[10px] text-neutral-400 font-bold uppercase tracking-widest">
                              <span>{frame.y_axis.bottom_label}</span>
                              <span>{frame.y_axis.top_label}</span>
                          </div>
                          <input 
                            type="range" 
                            min="0" max="100" 
                            value={position.y}
                            onChange={e => setPosition({...position, y: parseInt(e.target.value)})}
                            className="w-full h-1 bg-neutral-200 rounded-lg appearance-none cursor-pointer accent-neutral-900"
                          />
                      </div>
                  </div>
                  
                  <div className="pt-4">
                      <LuxeButton
                        onClick={handlePositionConfirm}
                        size="lg"
                        className="w-full"
                      >
                          Confirm Position
                      </LuxeButton>
                  </div>
              </div>
              
              {/* Map */}
              <div className="md:col-span-8 bg-white rounded-xl border border-neutral-200 shadow-lg p-12 relative flex items-center justify-center aspect-square">
                   <div className="relative w-full h-full border border-neutral-100">
                       {/* Grid Lines */}
                       <div className="absolute inset-0 grid grid-cols-2 grid-rows-2 pointer-events-none">
                           <div className="border-r border-b border-neutral-100"></div>
                           <div className="border-b border-neutral-100"></div>
                           <div className="border-r border-neutral-100"></div>
                           <div></div>
                       </div>
                       
                       {/* Axis Labels */}
                       <div className="absolute -left-12 top-1/2 -translate-y-1/2 -rotate-90 text-[10px] font-bold uppercase tracking-[0.2em] text-neutral-400 whitespace-nowrap">
                           {frame.y_axis.label}
                       </div>
                       <div className="absolute bottom-[-48px] left-1/2 -translate-x-1/2 text-[10px] font-bold uppercase tracking-[0.2em] text-neutral-400 whitespace-nowrap">
                           {frame.x_axis.label}
                       </div>
                       
                       {/* Quadrant Labels (Optional) */}
                       <div className="absolute top-4 right-4 text-[10px] text-neutral-300 font-bold uppercase tracking-widest text-right">
                           {frame.quadrants?.top_right || "Specialist / High Touch"}
                       </div>
                       <div className="absolute bottom-4 left-4 text-[10px] text-neutral-300 font-bold uppercase tracking-widest text-left">
                           {frame.quadrants?.bottom_left || "General / DIY"}
                       </div>
                       
                       {/* The Dot */}
                       <motion.div
                           className="absolute w-4 h-4 bg-neutral-900 rounded-full shadow-xl ring-4 ring-white cursor-grab active:cursor-grabbing z-10"
                           style={{
                               left: `${position.x}%`,
                               bottom: `${position.y}%`, // Use bottom for Y since range 0 is typically bottom
                               transform: 'translate(-50%, 50%)'
                           }}
                           drag
                           dragMomentum={false}
                           dragElastic={0}
                       >
                           <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-neutral-900 text-white text-[10px] font-bold px-2 py-1 rounded whitespace-nowrap">
                               YOU
                           </div>
                       </motion.div>
                   </div>
              </div>
          </div>
      );
  };
  
  const renderFinalRecap = () => (
      <div className="max-w-3xl mx-auto text-center">
          <div className="mb-12">
              <div className="w-16 h-16 bg-neutral-900 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
                  <CheckCircle2 className="w-8 h-8 text-white" />
              </div>
              <LuxeHeading level={1} className="mb-4">Strategy Locked.</LuxeHeading>
              <p className="text-xl text-neutral-500">
                  You have staked your claim. This will now drive your campaigns, ICPs, and content.
              </p>
          </div>
          
          <LuxeCard className="text-left max-w-2xl mx-auto mb-12 border-neutral-200 shadow-xl">
              <div className="border-b border-neutral-100 pb-4 mb-6">
                  <h3 className="font-bold text-neutral-400 uppercase tracking-widest text-xs">
                      Your Narrative
                  </h3>
              </div>
              
              <p className="text-3xl font-display font-medium leading-tight mb-8 text-neutral-900">
                  "{contextData?.core_line}"
              </p>
              
              <div className="grid grid-cols-2 gap-6 text-sm border-t border-neutral-100 pt-6">
                  <div>
                      <span className="block text-neutral-400 text-[10px] uppercase tracking-widest mb-1">Competing On</span>
                      <span className="font-medium text-neutral-900 text-lg">
                           {position.x > 50 ? axesData?.find(f => f.id === selectedFrameId)?.x_axis.right_label : axesData?.find(f => f.id === selectedFrameId)?.x_axis.left_label}
                      </span>
                  </div>
                  <div>
                      <span className="block text-neutral-400 text-[10px] uppercase tracking-widest mb-1">Delivery Model</span>
                      <span className="font-medium text-neutral-900 text-lg">
                           {position.y > 50 ? axesData?.find(f => f.id === selectedFrameId)?.y_axis.top_label : axesData?.find(f => f.id === selectedFrameId)?.y_axis.bottom_label}
                      </span>
                  </div>
              </div>
          </LuxeCard>
          
          <LuxeButton
            onClick={handleFinalLock}
            disabled={isLoading}
            isLoading={isLoading}
            size="lg"
            className="px-12"
            icon={ArrowRight}
          >
              Enter The Battlefield
          </LuxeButton>
      </div>
  );
  
  const renderBattlefield = () => {
      const frame = axesData?.find(f => f.id === selectedFrameId);
      
      if (isLoading && !competitorData) {
          return (
              <div className="flex flex-col items-center justify-center h-full py-20">
                  <Loader2 className="w-12 h-12 animate-spin mb-6 text-black" />
                  <h3 className="text-xl font-serif font-bold">Scanning the Horizon...</h3>
                  <p className="text-gray-500">Identifying key competitors and plotting their positions.</p>
              </div>
          );
      }

      return (
          <div className="max-w-6xl mx-auto">
              <div className="text-center mb-10">
                  <h1 className="text-4xl font-serif font-bold mb-4">The Battlefield</h1>
                  <p className="text-xl text-gray-600">
                      Here is where you stand against the noise.
                  </p>
              </div>
              
              <div className="grid md:grid-cols-12 gap-8">
                  <div className="md:col-span-8 bg-white border-2 border-black shadow-sm rounded-xl p-8 relative aspect-square">
                       {/* Grid Lines */}
                       <div className="absolute inset-0 grid grid-cols-2 grid-rows-2 pointer-events-none">
                           <div className="border-r border-b border-gray-100"></div>
                           <div className="border-b border-gray-100"></div>
                           <div className="border-r border-gray-100"></div>
                           <div></div>
                       </div>
                       
                       {/* Axes */}
                       <div className="absolute -left-8 top-1/2 -translate-y-1/2 -rotate-90 text-xs font-bold uppercase tracking-widest text-gray-400 whitespace-nowrap">
                           {frame?.y_axis.label}
                       </div>
                       <div className="absolute bottom-[-32px] left-1/2 -translate-x-1/2 text-xs font-bold uppercase tracking-widest text-gray-400 whitespace-nowrap">
                           {frame?.x_axis.label}
                       </div>

                        {/* YOU */}
                       <div
                           className="absolute w-6 h-6 bg-black rounded-full shadow-xl border-2 border-white z-20"
                           style={{
                               left: `${position.x}%`,
                               bottom: `${position.y}%`,
                               transform: 'translate(-50%, 50%)'
                           }}
                       >
                           <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black text-white text-[10px] font-bold px-2 py-1 rounded whitespace-nowrap">
                               YOU
                           </div>
                       </div>
                       
                       {/* Competitors */}
                       {competitorData?.competitors?.map((comp, i) => (
                           <div
                                key={i}
                                className="absolute w-4 h-4 bg-gray-400 rounded-full border border-white z-10 hover:bg-red-500 transition-colors cursor-help group"
                                style={{
                                    left: `${comp.x}%`,
                                    bottom: `${comp.y}%`,
                                    transform: 'translate(-50%, 50%)'
                                }}
                           >
                               <div className="absolute top-6 left-1/2 -translate-x-1/2 bg-white border border-gray-200 text-gray-900 text-xs px-2 py-1 rounded shadow-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                                   <span className="font-bold block">{comp.name}</span>
                                   <span className="text-[10px] text-gray-500">{comp.label}</span>
                               </div>
                           </div>
                       ))}
                       
                       {/* Growth Vectors */}
                       {competitorData?.growth_vectors?.map((vec, i) => (
                           <div key={i} className="absolute z-0 pointer-events-none">
                               <svg className="absolute top-0 left-0 overflow-visible">
                                   <defs>
                                       <marker id={`arrow-${i}`} markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
                                           <path d="M0,0 L0,6 L9,3 z" fill="#10B981" />
                                       </marker>
                                   </defs>
                                   {/* Simple line representation, converting % to approximate pixels relative to container is hard in pure SVG without knowing dimensions. 
                                       Skipping actual SVG lines for MVP robustness, or could use inline styles if container is fixed. 
                                       Let's just list them on the side.
                                   */}
                               </svg>
                           </div>
                       ))}
                  </div>
                  
                  <div className="md:col-span-4 space-y-6">
                      <div className="bg-gray-50 p-6 rounded-xl border border-gray-200">
                          <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                              <Target className="w-4 h-4" />
                              Competitors
                          </h3>
                          <ul className="space-y-3 text-sm">
                              {competitorData?.competitors?.map((comp, i) => (
                                  <li key={i} className="flex justify-between items-center">
                                      <span className="font-medium">{comp.name}</span>
                                      <span className="text-xs text-gray-500 px-2 py-1 bg-white rounded border">{comp.label}</span>
                                  </li>
                              ))}
                          </ul>
                      </div>
                      
                      <div className="bg-green-50 p-6 rounded-xl border border-green-100">
                          <h3 className="font-bold text-green-900 mb-4 flex items-center gap-2">
                              <Sparkles className="w-4 h-4" />
                              Growth Vectors
                          </h3>
                          <div className="space-y-4">
                              {competitorData?.growth_vectors?.map((vec, i) => (
                                  <div key={i} className="text-sm">
                                      <div className="font-bold text-green-800 mb-1">{vec.title}</div>
                                      <p className="text-green-700 leading-snug opacity-90">{vec.description}</p>
                                  </div>
                              ))}
                          </div>
                      </div>
                      
                      <button
                        onClick={handleBattlefieldComplete}
                        className="w-full py-4 bg-black text-white rounded-lg font-bold hover:bg-gray-900 transition-colors"
                      >
                          Confirm & Next
                      </button>
                  </div>
              </div>
          </div>
      );
  };
  
  const renderTribes = () => {
      if (isLoading && !icpData) {
          return (
              <div className="flex flex-col items-center justify-center h-full py-20">
                  <Loader2 className="w-12 h-12 animate-spin mb-6 text-black" />
                  <h3 className="text-xl font-serif font-bold">Summoning the Tribes...</h3>
                  <p className="text-gray-500">Defining your ideal customer profiles.</p>
              </div>
          );
      }

      return (
          <div className="max-w-6xl mx-auto">
              <div className="text-center mb-10">
                  <h1 className="text-4xl font-serif font-bold mb-4">The Tribes</h1>
                  <p className="text-xl text-gray-600">
                      Who are we fighting for? Select your core ICPs.
                  </p>
              </div>
              
              <div className="grid md:grid-cols-3 gap-6 mb-10">
                  {icpData?.icps?.map((icp, i) => {
                      const isSelected = selectedIcps.includes(i);
                      return (
                          <motion.div
                            key={i}
                            whileHover={{ y: -5 }}
                            onClick={() => {
                                if (isSelected) setSelectedIcps(selectedIcps.filter(idx => idx !== i));
                                else setSelectedIcps([...selectedIcps, i]);
                            }}
                            className={`
                                cursor-pointer p-6 rounded-xl border-2 transition-all duration-200 relative
                                ${isSelected 
                                    ? 'border-black bg-black text-white shadow-xl' 
                                    : 'border-gray-200 bg-white hover:border-gray-300'
                                }
                            `}
                          >
                              {isSelected && (
                                  <div className="absolute top-4 right-4">
                                      <CheckCircle2 className="w-6 h-6 text-green-400" />
                                  </div>
                              )}
                              
                              <h3 className="font-bold text-xl mb-3 pr-8">{icp.title}</h3>
                              <p className={`text-sm mb-4 leading-relaxed ${isSelected ? 'text-gray-300' : 'text-gray-600'}`}>
                                  {icp.summary}
                              </p>
                              
                              <div className={`text-xs p-3 rounded-lg ${isSelected ? 'bg-white/10' : 'bg-gray-50'}`}>
                                  <span className={`block font-bold uppercase mb-1 ${isSelected ? 'text-gray-400' : 'text-gray-500'}`}>Why Target</span>
                                  {icp.why_target}
                              </div>
                          </motion.div>
                      );
                  })}
              </div>
              
              <div className="flex justify-center">
                  <button
                    onClick={handleTribesComplete}
                    disabled={isLoading || selectedIcps.length === 0}
                    className="px-12 py-4 bg-black text-white rounded-full font-bold text-lg hover:scale-105 transition-transform disabled:opacity-50"
                  >
                      {isLoading ? 'Finalizing...' : 'Enter RaptorFlow'}
                  </button>
              </div>
          </div>
      );
  };

  return (
    <div className="min-h-screen bg-white text-neutral-900 flex flex-col">
        {/* Header (Task 19) */}
        <div className="px-12 py-8 border-b border-neutral-100 flex justify-between items-center bg-white z-10 relative">
            <div className="flex items-center gap-4">
                <div className="w-8 h-8 bg-neutral-900 rounded flex items-center justify-center text-white font-bold font-serif">R</div>
                <span className="font-display text-xl font-medium tracking-tight">Positioning Engine</span>
            </div>
            
            {/* High-fashion Stepper (Task 19) */}
            <div className="hidden md:flex items-center gap-4">
                {steps.map((s, i) => {
                    const isActive = s.id === currentStep;
                    const isPast = steps.findIndex(st => st.id === currentStep) > i;
                    
                    return (
                        <div key={s.id} className="flex items-center gap-2">
                            {i > 0 && <div className={`w-8 h-px ${isPast ? 'bg-neutral-900' : 'bg-neutral-200'}`} />}
                            <div className={`flex items-center gap-2 ${isActive ? 'opacity-100' : isPast ? 'opacity-50' : 'opacity-30'}`}>
                                <span className={`text-xs font-bold uppercase tracking-widest ${isActive ? 'text-neutral-900' : 'text-neutral-500'}`}>
                                    {String(i + 1).padStart(2, '0')}
                                </span>
                                <span className={`text-xs font-medium ${isActive ? 'text-neutral-900' : 'text-neutral-500 hidden lg:block'}`}>
                                    {s.title}
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
        
        {/* Main Content */}
        <div className="flex-1 p-8 md:p-12 flex items-start justify-center relative overflow-hidden bg-neutral-50/30">
             <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-100/20 rounded-full blur-3xl pointer-events-none -z-10" />
             <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-red-100/20 rounded-full blur-3xl pointer-events-none -z-10" />
        
            <AnimatePresence mode="wait">
                <motion.div
                    key={currentStep}
                    initial={{ opacity: 0, y: 20, filter: 'blur(10px)' }}
                    animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                    exit={{ opacity: 0, y: -20, filter: 'blur(10px)' }}
                    transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                    className="w-full"
                >
                    {currentStep === 'brain_dump' && renderBrainDump()}
                    {currentStep === 'context_review' && renderContextReview()}
                    {currentStep === 'axis_selection' && renderAxisSelection()}
                    {currentStep === 'positioning_map' && renderPositioningMap()}
                    {currentStep === 'final_recap' && renderFinalRecap()}
                    {currentStep === 'battlefield' && renderBattlefield()}
                    {currentStep === 'tribes' && renderTribes()}
                </motion.div>
            </AnimatePresence>
        </div>
        
    </div>
  );
}
