import React, { useState, useRef, useEffect, useMemo } from 'react';
import { ArrowRight, Sparkles, Search, Check, Loader2, AlertTriangle, ChevronDown, X, Brain, Users, Target } from 'lucide-react';
import { motion } from 'framer-motion';
import { MapContainer, TileLayer, Marker, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';

// Fix for Leaflet default marker
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

import MarketPositionSnapshot from './MarketPositionSnapshot';
import CohortsBuilder from './CohortsBuilder';
import { 
  generateAnswerSuggestions, 
  generateICPFromAnswers, 
  generatePositioningInsights, 
  generateVertexAIQuestions 
} from '../lib/ai';
import { supabase } from '../lib/supabase';
import { useAuth } from '../context/AuthContext';

const GOOGLE_MAPS_API_KEY =
  import.meta.env.VITE_GOOGLE_MAPS_API_KEY ||
  'AIzaSyGT2XWp6X7UJLZ1EkL3mxV4m7Gx4nv6wU';

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

const loadGoogleMapsScript = (apiKey, onLoad, onError) => {
  if (!apiKey) {
    onError?.('missing-key')
    return
  }
  if (window.google && window.google.maps) {
    onLoad?.();
    return;
  }
  if (document.getElementById('google-maps-script')) {
     const checkInterval = setInterval(() => {
        if (window.google && window.google.maps) {
           clearInterval(checkInterval);
           onLoad?.();
        }
     }, 500);
     return; 
  }
  const script = document.createElement('script');
  script.id = 'google-maps-script';
  script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`;
  script.async = true;
  script.defer = true;
  script.onload = onLoad;
  script.onerror = () => onError?.('script-error');
  document.head.appendChild(script);
};

const GrainOverlay = () => (
  <div className="absolute inset-0 pointer-events-none z-0 opacity-[0.03] mix-blend-multiply" 
       style={{ 
         backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='1'/%3E%3C/svg%3E")` 
       }}>
  </div>
);

const curatedCities = [
  { label: 'Hyderabad, Telangana, India', lat: '17.3850', lon: '78.4867' },
  { label: 'Bengaluru, Karnataka, India', lat: '12.9716', lon: '77.5946' },
  { label: 'Mumbai, Maharashtra, India', lat: '19.0760', lon: '72.8777' },
  { label: 'Chennai, Tamil Nadu, India', lat: '13.0827', lon: '80.2707' },
  { label: 'Delhi, India', lat: '28.6139', lon: '77.2090' }
]

const ManualLocationFallback = ({ onLocationSelect, initialValue }) => {
  const [manualAddress, setManualAddress] = useState(initialValue?.address || '')
  const [manualLat, setManualLat] = useState(initialValue?.lat || '')
  const [manualLng, setManualLng] = useState(initialValue?.lng || '')
  const [suggestions, setSuggestions] = useState([])
  const [isSearching, setIsSearching] = useState(false)
  const [advancedOpen, setAdvancedOpen] = useState(false)

  useEffect(() => {
    onLocationSelect({
      address: manualAddress,
      lat: manualLat || undefined,
      lng: manualLng || undefined
    })
  }, [manualAddress, manualLat, manualLng, onLocationSelect])

  useEffect(() => {
    if (!manualAddress || manualAddress.length < 3) {
      setSuggestions([])
      return
    }
    const controller = new AbortController()
    const timeout = setTimeout(async () => {
      setIsSearching(true)
      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(manualAddress)}&limit=5`,
          { signal: controller.signal, headers: { 'Accept-Language': 'en' } }
        )
        if (response.ok) {
          const data = await response.json()
          setSuggestions(
            data.map((item) => ({
              label: item.display_name,
              lat: item.lat,
              lon: item.lon
            }))
          )
        }
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.error('Location search failed', error)
        }
      } finally {
        setIsSearching(false)
      }
    }, 350)
    return () => {
      controller.abort()
      clearTimeout(timeout)
    }
  }, [manualAddress])

  const handleSuggestionClick = (suggestion) => {
    setManualAddress(suggestion.label)
    setManualLat(suggestion.lat)
    setManualLng(suggestion.lon)
    setSuggestions([])
  }

  return (
    <div className="w-full max-w-xl space-y-6 rounded-3xl border border-neutral-200 bg-white/70 p-6 text-left">
      <div>
        <p className="text-sm uppercase tracking-[0.4em] text-neutral-500">Location</p>
        <p className="font-display text-2xl text-neutral-900">Manual Entry</p>
        <p className="text-sm text-neutral-500">Describe where you operate—we will geocode it later.</p>
      </div>
      <div className="space-y-4">
        <div className="relative">
          <label htmlFor="location-address-input" className="text-xs uppercase tracking-[0.3em] text-neutral-500">Address or Region</label>
          <input
            id="location-address-input"
            type="text"
            className="mt-2 w-full rounded-2xl border border-neutral-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-neutral-900"
            placeholder="e.g., Paris, France"
            value={manualAddress}
            onChange={(e) => setManualAddress(e.target.value)}
            aria-label="Enter your business location address or region"
            aria-describedby="location-help-text"
            aria-autocomplete="list"
            aria-controls={suggestions.length > 0 ? "location-suggestions" : undefined}
          />
          {(isSearching || suggestions.length > 0 || manualAddress.length >= 3) && (
            <div
              id="location-suggestions"
              className="absolute left-0 right-0 top-[92%] z-10 mt-2 overflow-hidden rounded-3xl border border-neutral-200 bg-white shadow-2xl"
              role="listbox"
              aria-label="Location suggestions"
            >
              {isSearching && (
                <div className="px-4 py-3 text-xs uppercase tracking-[0.3em] text-neutral-400" role="status" aria-live="polite">
                  searching...
                </div>
              )}
              {!isSearching && suggestions.length > 0 && (
                <>
                  <div className="px-4 pt-3 text-[10px] uppercase tracking-[0.4em] text-neutral-400">
                    Matches
                  </div>
                  {suggestions.map((suggestion) => (
                    <button
                      key={suggestion.label}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="block w-full px-4 py-3 text-left text-sm text-neutral-800 hover:bg-neutral-50"
                      role="option"
                      aria-label={`Select location: ${suggestion.label}`}
                    >
                      {suggestion.label}
                    </button>
                  ))}
                </>
              )}
              {!isSearching && suggestions.length === 0 && manualAddress.length >= 3 && (
                <>
                  <div className="px-4 pt-3 text-[10px] uppercase tracking-[0.4em] text-neutral-400">
                    Try These
                  </div>
                  {curatedCities
                    .filter((city) =>
                      city.label.toLowerCase().includes(manualAddress.toLowerCase())
                    )
                    .concat(
                      curatedCities.slice(0, 2)
                    )
                    .slice(0, 5)
                    .map((city) => (
                      <button
                        key={city.label}
                        onClick={() => handleSuggestionClick(city)}
                        className="block w-full px-4 py-3 text-left text-sm text-neutral-800 hover:bg-neutral-50"
                      >
                        {city.label}
                      </button>
                    ))}
                  <div className="px-4 py-3 text-xs text-neutral-500">
                    No exact matches; press Enter to keep your custom location.
                  </div>
                </>
              )}
            </div>
          )}
        </div>
        <button
          type="button"
          onClick={() => setAdvancedOpen(!advancedOpen)}
          className="text-xs uppercase tracking-[0.3em] text-neutral-500 hover:text-neutral-900"
        >
          {advancedOpen ? 'Hide advanced coordinates' : 'Show advanced coordinates'}
        </button>
        {advancedOpen && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs uppercase tracking-[0.3em] text-neutral-500">Latitude</label>
              <input
                type="number"
                className="mt-2 w-full rounded-2xl border border-neutral-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-neutral-900"
                placeholder="48.8566"
                value={manualLat}
                onChange={(e) => setManualLat(e.target.value)}
              />
            </div>
            <div>
              <label className="text-xs uppercase tracking-[0.3em] text-neutral-500">Longitude</label>
              <input
                type="number"
                className="mt-2 w-full rounded-2xl border border-neutral-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-neutral-900"
                placeholder="2.3522"
                value={manualLng}
                onChange={(e) => setManualLng(e.target.value)}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

const LeafletMap = ({ onLocationSelect, initialValue, error }) => {
  const [searchQuery, setSearchQuery] = useState(initialValue?.address || '');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [position, setPosition] = useState(
    initialValue?.lat 
      ? { lat: Number(initialValue.lat), lng: Number(initialValue.lng) } 
      : null
  );

  // Default center (India)
  const defaultCenter = { lat: 20.5937, lng: 78.9629 };
  const center = position || defaultCenter;
  const zoom = position ? 12 : 4;

  // Component to handle map clicks
  const MapEvents = () => {
    useMapEvents({
      click(e) {
        const newPos = { lat: e.latlng.lat, lng: e.latlng.lng };
        setPosition(newPos);
        onLocationSelect({
          lat: newPos.lat,
          lng: newPos.lng,
          address: `Pinned Location (${newPos.lat.toFixed(4)}, ${newPos.lng.toFixed(4)})`
        });
      },
    });
    return null;
  };

  // Component to update map view when position changes
  const MapUpdater = ({ center, zoom }) => {
    const map = useMap();
    useEffect(() => {
      map.setView(center, zoom);
    }, [center, zoom, map]);
    return null;
  };

  const handleSearch = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
  };

  // Effect for search debounce
  useEffect(() => {
    if (!searchQuery || searchQuery.length < 3) {
      setSearchResults([]);
      return;
    }
    
    const timer = setTimeout(async () => {
      try {
        setIsSearching(true);
        const response = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&limit=5`
        );
        if (response.ok) {
            const data = await response.json();
            setSearchResults(data);
        }
      } catch (err) {
        console.error("Search failed", err);
      } finally {
        setIsSearching(false);
      }
    }, 500);
    
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const selectResult = (result) => {
    const newPos = { lat: parseFloat(result.lat), lng: parseFloat(result.lon) };
    setPosition(newPos);
    setSearchQuery(result.display_name);
    setSearchResults([]);
    onLocationSelect({
      address: result.display_name,
      lat: newPos.lat,
      lng: newPos.lng
    });
  };

  return (
    <div className="w-full flex flex-col items-center space-y-6 animate-in fade-in slide-in-from-bottom-8 duration-1000">
      <div className="relative w-full max-w-xl z-20">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400" size={18} />
        <input 
          type="text" 
          value={searchQuery}
          onChange={handleSearch}
          placeholder="Search for your city..." 
          className="w-full bg-white border border-neutral-200 rounded-full py-4 pl-12 pr-6 text-neutral-800 shadow-xl shadow-neutral-200/50 focus:outline-none focus:ring-2 focus:ring-black transition-all font-sans text-sm"
        />
        {searchResults.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-xl border border-neutral-100 overflow-hidden z-50 max-h-60 overflow-y-auto">
             {searchResults.map((result, idx) => (
               <button
                 key={idx}
                 onClick={() => selectResult(result)}
                 className="w-full text-left px-4 py-3 hover:bg-neutral-50 text-xs text-neutral-700 border-b border-neutral-50 last:border-0 truncate"
               >
                 {result.display_name}
               </button>
             ))}
          </div>
        )}
      </div>

      <div className="w-full h-[40vh] md:h-[50vh] bg-neutral-100 relative border border-neutral-200 overflow-hidden shadow-inner rounded-xl z-0">
         {error && (
            <div className="absolute top-0 left-0 right-0 bg-amber-50/90 text-amber-800 text-[10px] uppercase font-bold py-2 text-center z-[400] flex items-center justify-center space-x-2 backdrop-blur-sm">
               <AlertTriangle size={12} />
               <span>Google Maps unavailable - switched to OpenStreetMap</span>
            </div>
         )}
         
         <MapContainer 
           center={center} 
           zoom={zoom} 
           style={{ height: '100%', width: '100%' }}
           zoomControl={false}
         >
           <TileLayer
             attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
             url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
           />
           {position && <Marker position={position} />}
           <MapEvents />
           <MapUpdater center={center} zoom={zoom} />
         </MapContainer>
      </div>
      
      {position && (
        <div className="flex items-center space-x-2 text-green-600 bg-green-50 px-4 py-2 border border-green-100 rounded-full">
           <Check size={14} />
           <span className="text-[10px] font-mono uppercase tracking-[0.2em]">Location Locked</span>
        </div>
      )}
    </div>
  );
};

const InteractiveMap = ({ onLocationSelect, initialValue }) => {
  const mapRef = useRef(null);
  const searchInputRef = useRef(null);
  const mapObj = useRef(null);
  const markerObj = useRef(null);
  const [scriptLoaded, setScriptLoaded] = useState(false);
  const [authWarning, setAuthWarning] = useState(false);
  const [mapError, setMapError] = useState('');

  // Memoize map styles to prevent recreation on every render
  const mapStyles = useMemo(() => [
    { "elementType": "geometry", "stylers": [{ "color": "#f5f5f5" }] },
    { "elementType": "labels.icon", "stylers": [{ "visibility": "off" }] },
    { "elementType": "labels.text.fill", "stylers": [{ "color": "#616161" }] },
    { "elementType": "labels.text.stroke", "stylers": [{ "color": "#f5f5f5" }] },
    { "featureType": "administrative.land_parcel", "elementType": "labels.text.fill", "stylers": [{ "color": "#bdbdbd" }] },
    { "featureType": "poi", "elementType": "geometry", "stylers": [{ "color": "#eeeeee" }] },
    { "featureType": "poi", "elementType": "labels.text.fill", "stylers": [{ "color": "#757575" }] },
    { "featureType": "road", "elementType": "geometry", "stylers": [{ "color": "#ffffff" }] },
    { "featureType": "road.arterial", "elementType": "labels.text.fill", "stylers": [{ "color": "#757575" }] },
    { "featureType": "road.highway", "elementType": "geometry", "stylers": [{ "color": "#dadada" }] },
    { "featureType": "road.highway", "elementType": "labels.text.fill", "stylers": [{ "color": "#616161" }] },
    { "featureType": "water", "elementType": "geometry", "stylers": [{ "color": "#e9e9e9" }] },
    { "featureType": "water", "elementType": "labels.text.fill", "stylers": [{ "color": "#9e9e9e" }] }
  ], []);
  
  useEffect(() => {
    window.gm_authFailure = () => {
      console.warn("Google Maps API Key Warning - Map may be degraded");
      setAuthWarning(true);
      // If auth fails, switch to Leaflet fallback
      setMapError('Authentication failed for Google Maps API key. Switching to fallback.');
    };

    if (!GOOGLE_MAPS_API_KEY) {
      // If no key is present, immediately switch to fallback
      setMapError('Google Maps API key missing. Add VITE_GOOGLE_MAPS_API_KEY to your .env file.');
      setAuthWarning(true);
      return;
    }

    loadGoogleMapsScript(
      GOOGLE_MAPS_API_KEY,
      () => {
        if (
          window.google &&
          window.google.maps &&
          typeof window.google.maps.Map === "function"
        ) {
          setScriptLoaded(true);
        } else {
          console.error("Google Maps failed to initialize.");
          setAuthWarning(true);
          setMapError('Google Maps failed to initialize. Please verify your API key permissions.');
        }
      },
      (reason) => {
        setAuthWarning(true);
        setMapError(
          reason === 'missing-key'
            ? 'Google Maps API key missing. Add VITE_GOOGLE_MAPS_API_KEY to your .env file.'
            : 'Unable to load Google Maps. Check your network connection or API key.'
        );
      }
    );
  }, []);

  useEffect(() => {
    if (!scriptLoaded || !mapRef.current || !window.google) return;
    try {
        const indiaCenter = { lat: 20.5937, lng: 78.9629 };
        const map = new window.google.maps.Map(mapRef.current, {
          center: initialValue?.lat ? { lat: Number(initialValue.lat), lng: Number(initialValue.lng) } : indiaCenter,
          zoom: initialValue?.lat ? 10 : 5,
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
            searchBox.setOptions({
              componentRestrictions: { country: 'in' }
            });
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
  }, [scriptLoaded, initialValue, onLocationSelect, mapStyles]);

  useEffect(() => {
    if (!initialValue || !markerObj.current || !mapObj.current) return
    const position = {
      lat: Number(initialValue.lat),
      lng: Number(initialValue.lng),
    }
    markerObj.current.setPosition(position)
    markerObj.current.setVisible(true)
    mapObj.current.setCenter(position)
    mapObj.current.setZoom(10)
  }, [initialValue])

  // Fallback to Leaflet if Google Maps fails or key is missing
  if (mapError) {
    return (
      <LeafletMap
        onLocationSelect={onLocationSelect}
        initialValue={initialValue}
        error={mapError}
      />
    )
  }

  return (
    <div className="w-full flex flex-col items-center space-y-6 animate-in fade-in slide-in-from-bottom-8 duration-1000">
      <div className="relative w-full max-w-xl z-20">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400" size={18} />
        <input 
          ref={searchInputRef}
          type="text" 
          placeholder="Search for your city..." 
          className="w-full bg-white border border-neutral-200 rounded-full py-4 pl-12 pr-6 text-neutral-800 shadow-xl shadow-neutral-200/50 focus:outline-none focus:ring-2 focus:ring-black transition-all font-sans text-sm"
        />
      </div>
      <div className="w-full h-[40vh] md:h-[50vh] bg-neutral-100 relative border border-neutral-200 overflow-hidden shadow-inner">
         {(authWarning) && (
            <div className="absolute top-0 left-0 right-0 bg-amber-100/90 text-amber-800 text-[10px] uppercase font-bold py-2 text-center z-30 flex items-center justify-center space-x-2 backdrop-blur-sm">
               <AlertTriangle size={12} />
               <span>{mapError || 'Maps API issue - functionality limited'}</span>
            </div>
         )}
         <div ref={mapRef} className="w-full h-full" />
         {!scriptLoaded && !mapError && (
           <div className="absolute inset-0 flex items-center justify-center text-neutral-400 text-xs font-mono z-0">
             INITIALIZING SATELLITE UPLINK...
           </div>
         )}
      </div>
      {initialValue && initialValue.address && (
        <div className="flex items-center space-x-2 text-green-600 bg-green-50 px-4 py-2 border border-green-100">
           <Check size={14} />
           <span className="text-[10px] font-mono uppercase tracking-[0.2em]">Location Locked</span>
        </div>
      )}
    </div>
  );
};

// Custom Dropdown Component with styled menu
const CustomDropdown = ({ value, options, onChange, placeholder = "Select an option" }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);
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
    setFocusedIndex(-1);
  };

  const handleKeyDown = (e) => {
    if (!isOpen) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
        e.preventDefault();
        setIsOpen(true);
        setFocusedIndex(0);
      }
      return;
    }

    switch (e.key) {
      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        setFocusedIndex(-1);
        break;
      case 'ArrowDown':
        e.preventDefault();
        setFocusedIndex((prev) => (prev < options.length - 1 ? prev + 1 : 0));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setFocusedIndex((prev) => (prev > 0 ? prev - 1 : options.length - 1));
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (focusedIndex >= 0) {
          handleSelect(options[focusedIndex]);
        }
        break;
      default:
        break;
    }
  };

  const displayValue = value || placeholder;
  const isPlaceholder = !value;

  return (
    <div className="relative w-full" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        className={`w-full bg-white/50 backdrop-blur-sm border border-neutral-200 rounded-lg px-6 py-4 pr-10 text-lg font-serif italic transition-all appearance-none cursor-pointer shadow-sm text-left flex items-center justify-between ${
          isPlaceholder ? 'text-neutral-400' : 'text-neutral-900'
        } hover:border-neutral-300 focus:outline-none focus:ring-2 focus:ring-black focus:border-black ${
          isOpen ? 'border-black ring-2 ring-black' : ''
        }`}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label={`Select option: ${displayValue}`}
      >
        <span>{displayValue}</span>
        <ChevronDown
          size={18}
          className={`text-neutral-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          aria-hidden="true"
        />
      </button>

      {isOpen && (
        <div
          className="absolute z-50 w-full mt-2 bg-white border border-neutral-200 rounded-lg shadow-lg overflow-hidden"
          style={{ animation: 'dropdownFadeIn 0.15s ease-out' }}
          role="listbox"
          aria-label="Options"
        >
          <div className="py-2">
            {options.map((option, idx) => (
              <button
                key={option}
                type="button"
                onClick={() => handleSelect(option)}
                onKeyDown={handleKeyDown}
                className={`w-full px-6 py-3 text-left text-lg font-serif italic transition-colors ${
                  value === option
                    ? 'bg-neutral-100 text-neutral-900 font-medium'
                    : idx === focusedIndex
                    ? 'bg-neutral-100 text-neutral-900'
                    : 'text-neutral-700 hover:bg-neutral-50 hover:text-neutral-900'
                } ${idx === 0 ? 'rounded-t-lg' : ''} ${idx === options.length - 1 ? 'rounded-b-lg' : ''}`}
                role="option"
                aria-selected={value === option}
                tabIndex={-1}
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
    <div className="w-full max-w-6xl animate-in fade-in slide-in-from-bottom-12 duration-1000 ease-out">
      <p className="font-serif text-3xl md:text-5xl text-black mb-24 leading-tight text-center">
        {question.prompt}
      </p>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-16 w-full">
        {question.fields.map((field, idx) => (
          <div key={field.id} className="flex flex-col items-center space-y-6 group w-full">
             <label className="font-sans text-[10px] font-bold uppercase tracking-[0.2em] text-neutral-400 group-focus-within:text-black transition-colors text-center">
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
                  className="w-full bg-transparent border-b border-neutral-200 py-4 text-xl font-serif italic text-neutral-900 focus:outline-none focus:border-black transition-all placeholder:text-neutral-300 text-center resize-none min-h-[60px]"
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

const StandardInput = ({ question, value, onChange, onBlur, aiSuggestions, loadingSuggestions, showSuggestions, onApplySuggestion }) => {
  return (
    <div className="group animate-in fade-in slide-in-from-bottom-12 duration-1000 ease-[cubic-bezier(0.22,1,0.36,1)] flex flex-col items-center text-center w-full z-10 max-w-4xl">
      <label
        htmlFor={`input-${question.id}`}
        className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-8 group-focus-within:text-black transition-colors duration-700"
      >
        {question.title}
      </label>
      <p className="font-serif text-4xl md:text-6xl text-black mb-16 leading-[1.1] tracking-tight antialiased" id={`question-${question.id}`}>
        {question.prompt}
      </p>
      <div className="relative w-full max-w-2xl space-y-6">
        <textarea
          id={`input-${question.id}`}
          autoFocus={true}
          value={value || ''}
          onChange={(e) => onChange(question.id, e.target.value)}
          onBlur={() => onBlur && onBlur(question.id)}
          placeholder={question.placeholder}
          className="w-full bg-transparent border-b border-neutral-200 text-2xl md:text-3xl text-neutral-900 py-8 focus:outline-none focus:border-neutral-900 transition-all duration-700 ease-[cubic-bezier(0.22,1,0.36,1)] placeholder:text-neutral-200 placeholder:font-light font-serif italic resize-none h-40 text-center leading-relaxed selection:bg-black selection:text-white"
          aria-labelledby={`question-${question.id}`}
          aria-describedby={`label-${question.id}`}
          aria-required={question.required || false}
        />

        {/* AI Suggestions */}
        {(loadingSuggestions || (showSuggestions && aiSuggestions.length > 0)) && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-2xl space-y-3"
          >
            <div className="flex items-center gap-2 justify-center">
              <Sparkles className="w-4 h-4 text-neutral-400" />
              <p className="text-xs uppercase tracking-widest text-neutral-400 font-bold">
                AI Suggestions
              </p>
            </div>

            {loadingSuggestions && (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="w-5 h-5 animate-spin text-neutral-400" />
              </div>
            )}

            {!loadingSuggestions && showSuggestions && aiSuggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => onApplySuggestion(suggestion)}
                className="w-full p-4 text-left bg-neutral-50 hover:bg-neutral-100 border border-neutral-200 rounded-lg transition-all duration-200 group/suggestion"
              >
                <p className="text-sm text-neutral-700 group-hover/suggestion:text-neutral-900 font-serif italic">
                  "{suggestion}"
                </p>
                <p className="text-xs text-neutral-400 mt-2 uppercase tracking-wider font-sans font-bold">
                  Click to apply
                </p>
              </button>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
};

const ProcessingScreen = ({ onSkip }) => (
   <div className="flex flex-col items-center justify-center space-y-8 animate-in fade-in duration-1000" role="status" aria-live="polite">
      <Loader2 className="animate-spin text-black" size={56} aria-hidden="true" />
      <div className="text-center space-y-4 max-w-2xl">
        <p className="font-serif text-3xl italic">Analyzing your business...</p>
        <div className="space-y-3">
          <p className="font-sans text-xs uppercase tracking-widest text-neutral-400">Running AI Analysis</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="runway-card p-4 text-center">
              <Brain className="w-6 h-6 mx-auto mb-2 text-neutral-600" />
              <p className="text-xs font-bold uppercase tracking-wider text-neutral-700">Strategy Gaps</p>
              <p className="text-[10px] text-neutral-500 mt-1">Identifying missing insights</p>
            </div>
            <div className="runway-card p-4 text-center">
              <Users className="w-6 h-6 mx-auto mb-2 text-neutral-600" />
              <p className="text-xs font-bold uppercase tracking-wider text-neutral-700">ICP Generation</p>
              <p className="text-[10px] text-neutral-500 mt-1">Creating ideal customer profiles</p>
            </div>
            <div className="runway-card p-4 text-center">
              <Target className="w-6 h-6 mx-auto mb-2 text-neutral-600" />
              <p className="text-xs font-bold uppercase tracking-wider text-neutral-700">Positioning</p>
              <p className="text-[10px] text-neutral-500 mt-1">Analyzing market position</p>
            </div>
          </div>
        </div>
      </div>
      {onSkip && (
        <button
          onClick={onSkip}
          className="mt-8 font-sans text-[10px] font-bold uppercase tracking-widest border-b border-transparent hover:border-black transition-all duration-500 pb-1 text-neutral-400 hover:text-black"
          aria-label="Skip AI analysis and continue to next step"
        >
          Skip analysis
        </button>
      )}
   </div>
);

const ProgressBar = ({ current, total }) => {
  const progress = ((current + 1) / total) * 100;
  return (
    <div className="fixed bottom-0 left-0 w-full z-50 bg-white pt-4 pb-0" role="progressbar" aria-valuenow={current + 1} aria-valuemin={1} aria-valuemax={total} aria-label={`Onboarding progress: step ${current + 1} of ${total}`}>
       <div className="flex justify-between items-end px-8 pb-2 text-xs font-sans font-bold text-black uppercase tracking-widest">
          <span aria-hidden="true">{current + 1} / {total}</span>
       </div>
       <div className="h-3 bg-neutral-200 w-full">
          <div
            className="h-full bg-black transition-all duration-1000 ease-[cubic-bezier(0.22,1,0.36,1)]"
            style={{ width: `${progress}%` }}
            aria-hidden="true"
          ></div>
       </div>
    </div>
  );
};

export default function Onboarding({ onClose }) {
  const [questions, setQuestions] = useState(INITIAL_QUESTIONS);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [status, setStatus] = useState('input');
  const [showCohortsBuilder, setShowCohortsBuilder] = useState(false);

  // AI-powered features state
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [generatedICPs, setGeneratedICPs] = useState([]);
  const [positioningInsights, setPositioningInsights] = useState(null);
  const [showAISuggestions, setShowAISuggestions] = useState(false);
  const { user } = useAuth();

  const currentQuestion = questions[currentStepIndex];
  const mainScrollRef = useRef(null);
  const suggestionTimeoutRef = useRef(null);

  // Keyboard navigation support
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Only handle keyboard shortcuts if we're in input or followup mode
      if (status !== 'input' && status !== 'followup') return;

      // Escape to close
      if (e.key === 'Escape' && onClose) {
        e.preventDefault();
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [status, onClose]);

  const handleAnswer = (id, value) => {
    setAnswers(prev => ({ ...prev, [id]: value }));

    // Trigger AI suggestions after user pauses typing (debounced)
    if (currentQuestion && (currentQuestion.type === 'text' || currentQuestion.type === 'textarea')) {
      if (suggestionTimeoutRef.current) {
        clearTimeout(suggestionTimeoutRef.current);
      }

      // Only fetch suggestions if user has typed at least 10 characters
      if (value && value.length >= 10) {
        suggestionTimeoutRef.current = setTimeout(async () => {
          setLoadingSuggestions(true);
          const suggestions = await generateAnswerSuggestions(currentQuestion, value, answers);
          setAiSuggestions(suggestions);
          setLoadingSuggestions(false);
          if (suggestions.length > 0) {
            setShowAISuggestions(true);
          }
        }, 2000); // Wait 2 seconds after user stops typing
      } else {
        setAiSuggestions([]);
        setShowAISuggestions(false);
      }
    }
  };

  const applySuggestion = (suggestion) => {
    if (currentQuestion) {
      setAnswers(prev => ({ ...prev, [currentQuestion.id]: suggestion }));
      setShowAISuggestions(false);
      setAiSuggestions([]);
    }
  };

  const skipToMarketPosition = () => {
    setStatus('market-position');
  };

  const runAIAnalysis = async () => {
    setStatus('analyzing');

    // Add a shorter timeout - if analysis takes too long, skip to market position
    const timeoutId = setTimeout(() => {
      console.warn("AI analysis timeout - proceeding to market position");
      setStatus('market-position');
    }, 15000); // 15 second timeout for multiple AI operations

    try {
      // Run multiple AI analyses in parallel
      const [aiQuestions, icps, insights] = await Promise.all([
        generateVertexAIQuestions(answers, INITIAL_QUESTIONS).catch(err => {
          console.warn("AI questions failed:", err);
          return [];
        }),
        generateICPFromAnswers(answers).catch(err => {
          console.warn("ICP generation failed:", err);
          return [];
        }),
        generatePositioningInsights(answers).catch(err => {
          console.warn("Positioning insights failed:", err);
          return null;
        })
      ]);

      clearTimeout(timeoutId);

      // Store generated ICPs and insights
      if (icps && icps.length > 0) {
        setGeneratedICPs(icps);
      }
      if (insights) {
        setPositioningInsights(insights);
      }

      if (aiQuestions && aiQuestions.length > 0) {
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
        setStatus('followup');
        setCurrentStepIndex(prev => prev + 1);
      } else {
        // No AI questions generated, go straight to market position
        clearTimeout(timeoutId);
        setStatus('market-position');
      }
    } catch (error) {
      clearTimeout(timeoutId);
      console.error("AI Generation failed, proceeding to market position:", error);
      // Skip AI questions and go straight to market position
      setStatus('market-position');
    }
  };

  const nextStep = () => {
    // Special handling for q7 - triggers AI analysis
    if (currentQuestion && currentQuestion.id === 'q7') {
       runAIAnalysis();
       return;
    }
    // Check if we're at the last question (index equals last index)
    if (currentStepIndex < questions.length - 1) {
      // Move to next question
      setCurrentStepIndex(prev => prev + 1);
      if (mainScrollRef.current) mainScrollRef.current.scrollTop = 0;
    } else {
       // We're on the last question, so next click should go to market position
       setStatus('market-position');
       if (mainScrollRef.current) mainScrollRef.current.scrollTop = 0;
    }
  };

  const prevStep = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(prev => prev - 1);
    }
  };

  const handleMarketPositionComplete = (marketData) => {
    // Store market position data in answers
    setAnswers(prev => ({
      ...prev,
      market_position: marketData
    }));
    // Move to complete status
    setStatus('complete');
  };

  const handleMarketPositionBack = () => {
    // Go back to last question
    if (currentStepIndex > 0) {
      setCurrentStepIndex(questions.length - 1);
      setStatus('input');
    }
  };

  const renderInput = () => {
    if (status === 'analyzing') return <ProcessingScreen onSkip={skipToMarketPosition} />;
    if (status === 'market-position') {
      return (
        <MarketPositionSnapshot
          answers={answers}
          onComplete={handleMarketPositionComplete}
          onBack={handleMarketPositionBack}
        />
      );
    }
    if (status === 'complete') return (
      <div className="text-center animate-in zoom-in-95 duration-1000 flex flex-col items-center">
        <h1 className="font-serif text-6xl mb-6">All Set.</h1>
        <p className="text-neutral-500 font-sans uppercase tracking-widest text-xs mb-12">Protocol Complete</p>
        <button
            onClick={async () => {
              // Save onboarding data to Supabase
              if (user) {
                try {
                  const { error } = await supabase
                    .from('onboarding_responses')
                    .upsert([
                      { 
                        user_id: user.id, 
                        answers, 
                        generated_icps: generatedICPs, 
                        positioning_insights: positioningInsights,
                        completed_at: new Date().toISOString(),
                        progress_percentage: 100,
                        updated_at: new Date().toISOString()
                      }
                    ]);
                  
                  if (error) {
                    console.warn('Failed to save onboarding responses to Supabase:', error);
                    // Optional: save to localStorage as backup
                    localStorage.setItem('onboarding_backup', JSON.stringify({ answers, generatedICPs, positioningInsights }));
                  } else {
                    // Mark onboarding as complete in user profile
                    await supabase
                      .from('user_profiles')
                      .update({ onboarding_completed: true })
                      .eq('id', user.id);
                  }
                } catch (err) {
                  console.error('Error saving onboarding:', err);
                }
              }

              // Launch Cohorts Builder instead of closing
              setShowCohortsBuilder(true);
            }} 
            className="group relative bg-black text-white px-16 py-6 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-neutral-500/20"
        >
            <div className="relative z-10 flex items-center space-x-4">
                <span className="font-sans text-xs font-bold tracking-widest uppercase">
                    Let's Go
                </span>
                <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform duration-500" />
            </div>
            <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
        </button>
      </div>
    );

    // Safety check - if no current question, transition to market position
    if (!currentQuestion) {
      // This shouldn't happen, but if it does, go to market position
      if (status === 'input' || status === 'followup') {
        setStatus('market-position');
        return null;
      }
    }

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
             aiSuggestions={aiSuggestions}
             loadingSuggestions={loadingSuggestions}
             showSuggestions={showAISuggestions}
             onApplySuggestion={applySuggestion}
          />
        );
    }
  };

  // Show Cohorts Builder if triggered
  if (showCohortsBuilder) {
    return (
      <CohortsBuilder
        onClose={() => {
          setShowCohortsBuilder(false);
          onClose && onClose();
        }}
        onboardingData={{
          answers,
          aiGeneratedICPs: generatedICPs,
          positioningInsights: positioningInsights
        }}
      />
    );
  }

  return (
    <div className="fixed inset-0 z-[100] flex h-screen w-screen bg-white text-neutral-900 overflow-hidden font-sans selection:bg-black selection:text-white">
      <GrainOverlay />
      {onClose && (
        <button
          className="absolute top-8 left-8 z-50 p-2 text-neutral-400 hover:text-black transition-colors hover:bg-neutral-100"
          onClick={onClose}
          aria-label="Close onboarding"
          title="Close onboarding"
        >
          <X size={24} aria-hidden="true" />
        </button>
      )}
      <div ref={mainScrollRef} className="flex-grow flex flex-col justify-center items-center px-6 md:px-8 relative z-10">
        <div className="w-full flex flex-col items-center pb-12 max-w-7xl">
           {status !== 'analyzing' && status !== 'complete' && status !== 'market-position' && currentQuestion && (
             <div className="flex items-center space-x-4 mb-12 animate-in fade-in duration-1000 slide-in-from-top-4 ease-[cubic-bezier(0.22,1,0.36,1)]">
                <span className="font-sans font-bold text-[9px] text-white bg-black px-2 py-1 tracking-widest">
                  {currentQuestion.section}
                </span>
                <span className="font-sans font-bold text-[10px] uppercase tracking-[0.2em] text-neutral-400">
                  {currentQuestion.category}
                </span>
             </div>
           )}
           {renderInput()}
           {status !== 'analyzing' && status !== 'complete' && status !== 'market-position' && (
             <div className="mt-24 flex items-center space-x-12 animate-in fade-in duration-1000 delay-300 ease-out">
                <button
                    onClick={prevStep}
                    disabled={currentStepIndex === 0}
                    className={`font-sans text-[10px] font-bold uppercase tracking-widest border-b border-transparent hover:border-black transition-all duration-500 pb-1 ${currentStepIndex === 0 ? 'opacity-0 cursor-default' : 'text-neutral-400 hover:text-black'}`}
                    aria-label="Go to previous question"
                    aria-disabled={currentStepIndex === 0}
                >
                    Back
                </button>
                <button
                    onClick={nextStep}
                    className="group relative bg-black text-white px-12 py-5 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-neutral-500/20"
                    aria-label={currentQuestion && currentQuestion.id === 'q7' ? 'Analyze responses with AI' : (currentStepIndex === questions.length - 1 ? 'Finish onboarding' : 'Continue to next question')}
                >
                    <div className="relative z-10 flex items-center space-x-4">
                        <span className="font-sans text-xs font-bold tracking-widest uppercase">
                            {currentQuestion && currentQuestion.id === 'q7' ? 'Analyze' : (currentStepIndex === questions.length - 1 ? 'Finish' : 'Next')}
                        </span>
                        {currentQuestion && currentQuestion.id === 'q7' ? <Sparkles size={14} aria-hidden="true" /> : <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform duration-500" aria-hidden="true" />}
                    </div>
                    <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
                </button>
             </div>
           )}
        </div>
      </div>
      {status !== 'complete' && status !== 'market-position' && (
         <ProgressBar 
           current={currentStepIndex} 
           total={questions.length} 
         />
      )}
    </div>
  );
}

