'use client';

import React, { useEffect, useRef, useState } from 'react';
import { MapPin, Search, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LocationPickerProps {
  value?: {
    address: string;
    lat: number;
    lng: number;
    formattedAddress: string;
  };
  onChange: (location: {
    address: string;
    lat: number;
    lng: number;
    formattedAddress: string;
  }) => void;
  className?: string;
}

declare global {
  interface Window {
    google: typeof google;
    initMap: () => void;
  }
}

export function LocationPicker({ value, onChange, className }: LocationPickerProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<google.maps.Map | null>(null);
  const [marker, setMarker] = useState<google.maps.Marker | null>(null);
  const [searchQuery, setSearchQuery] = useState(value?.address || '');
  const [autocomplete, setAutocomplete] = useState<google.maps.places.Autocomplete | null>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load Google Maps API
  useEffect(() => {
    if (typeof window === 'undefined') {
      setIsLoading(false);
      return;
    }

    if (window.google) {
      setIsLoading(false);
      return;
    }

    const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
    if (!apiKey) {
      setIsLoading(false);
      return;
    }

    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`;
    script.async = true;
    script.defer = true;
    script.onload = () => {
      setIsLoading(false);
    };
    script.onerror = () => {
      setIsLoading(false);
    };
    document.head.appendChild(script);

    return () => {
      // Cleanup
    };
  }, []);

  // Initialize map
  useEffect(() => {
    if (typeof window === 'undefined' || !mapRef.current || !window.google || map) return;

    const newMap = new window.google.maps.Map(mapRef.current, {
      center: value
        ? { lat: value.lat, lng: value.lng }
        : { lat: 28.6139, lng: 77.209 }, // Default to India
      zoom: value ? 15 : 5,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
      styles: [
        {
          featureType: 'all',
          elementType: 'geometry',
          stylers: [{ color: '#f0f2f5' }],
        },
        {
          featureType: 'water',
          elementType: 'geometry',
          stylers: [{ color: '#ffffff' }],
        },
      ],
    });

    setMap(newMap);

    // Add click listener
    newMap.addListener('click', (e: google.maps.MapMouseEvent) => {
      if (e.latLng) {
        const lat = e.latLng.lat();
        const lng = e.latLng.lng();

        // Reverse geocode
        const geocoder = new window.google.maps.Geocoder();
        geocoder.geocode({ location: { lat, lng } }, (results, status) => {
          if (status === 'OK' && results && results[0]) {
            const address = results[0].formatted_address;
            onChange({
              address,
              lat,
              lng,
              formattedAddress: address,
            });
            setSearchQuery(address);
          }
        });
      }
    });
  }, [mapRef, value, onChange, map]);

  // Initialize autocomplete
  useEffect(() => {
    if (typeof window === 'undefined' || !searchInputRef.current || !window.google || autocomplete) return;

    const newAutocomplete = new window.google.maps.places.Autocomplete(
      searchInputRef.current,
      {
        types: ['establishment', 'geocode'],
        fields: ['formatted_address', 'geometry'],
      }
    );

    newAutocomplete.addListener('place_changed', () => {
      const place = newAutocomplete.getPlace();
      if (place.geometry && place.geometry.location) {
        const lat = place.geometry.location.lat();
        const lng = place.geometry.location.lng();
        const address = place.formatted_address || '';

        onChange({
          address,
          lat,
          lng,
          formattedAddress: address,
        });

        if (map) {
          map.setCenter({ lat, lng });
          map.setZoom(15);
        }
      }
    });

    setAutocomplete(newAutocomplete);
  }, [searchInputRef, autocomplete, map, onChange]);

  // Update marker when value changes
  useEffect(() => {
    if (typeof window === 'undefined' || !window.google || !map || !value) {
      if (marker) {
        marker.setMap(null);
        setMarker(null);
      }
      return;
    }

    if (marker) {
      marker.setPosition({ lat: value.lat, lng: value.lng });
    } else {
      const newMarker = new window.google.maps.Marker({
        position: { lat: value.lat, lng: value.lng },
        map,
        draggable: true,
      });

      newMarker.addListener('dragend', (e: google.maps.MapMouseEvent) => {
        if (e.latLng) {
          const lat = e.latLng.lat();
          const lng = e.latLng.lng();

          const geocoder = new window.google.maps.Geocoder();
          geocoder.geocode({ location: { lat, lng } }, (results, status) => {
            if (status === 'OK' && results && results[0]) {
              const address = results[0].formatted_address;
              onChange({
                address,
                lat,
                lng,
                formattedAddress: address,
              });
              setSearchQuery(address);
            }
          });
        }
      });

      setMarker(newMarker);
    }
  }, [map, value, marker, onChange]);

  const handleClear = () => {
    setSearchQuery('');
    if (marker) {
      marker.setMap(null);
      setMarker(null);
    }
    onChange({
      address: '',
      lat: 0,
      lng: 0,
      formattedAddress: '',
    });
  };

  if (isLoading) {
    return (
      <div className={cn('h-64 bg-rf-cloud rounded-lg flex items-center justify-center', className)}>
        <p className="text-sm text-rf-subtle">Loading map...</p>
      </div>
    );
  }

  if (!process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY) {
    return (
      <div className={cn('space-y-4', className)}>
        <div className="p-4 bg-rf-cloud rounded-lg border border-rf-cloud">
          <p className="text-sm text-rf-subtle mb-3">
            Google Maps API key not configured. Please add NEXT_PUBLIC_GOOGLE_MAPS_API_KEY to your environment variables.
          </p>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Enter your business address manually..."
            className="w-full px-4 py-3 rounded-lg border border-rf-cloud bg-rf-bg text-rf-ink placeholder:text-rf-muted focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20 text-sm"
            onBlur={() => {
              if (searchQuery) {
                onChange({
                  address: searchQuery,
                  lat: 0,
                  lng: 0,
                  formattedAddress: searchQuery,
                });
              }
            }}
          />
        </div>
      </div>
    );
  }

  return (
    <div className={cn('space-y-4', className)}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-rf-subtle" />
        <input
          ref={searchInputRef}
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search for your business location..."
          className={cn(
            'w-full pl-10 pr-10 py-3 rounded-lg border border-rf-cloud',
            'bg-rf-bg text-rf-ink placeholder:text-rf-muted',
            'focus:outline-none focus:border-rf-primary focus:ring-1 focus:ring-rf-primary/20',
            'text-sm'
          )}
        />
        {searchQuery && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-rf-subtle hover:text-rf-ink"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      <div
        ref={mapRef}
        className={cn('h-64 w-full rounded-lg border border-rf-cloud overflow-hidden', className)}
      />

      {value && value.lat !== 0 && (
        <div className="flex items-start gap-2 p-3 bg-rf-cloud rounded-lg">
          <MapPin className="w-4 h-4 text-rf-subtle mt-0.5 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-rf-ink">{value.formattedAddress}</p>
            <p className="text-xs text-rf-subtle mt-0.5">
              {value.lat.toFixed(6)}, {value.lng.toFixed(6)}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

