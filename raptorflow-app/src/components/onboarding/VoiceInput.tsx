'use client';

import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Mic, MicOff, Loader2, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
  className?: string;
}

type RecordingState = 'idle' | 'recording' | 'processing' | 'done';

/**
 * Voice-to-text input using Web Speech API
 */
export function VoiceInput({
  onTranscript,
  disabled,
  className,
}: VoiceInputProps) {
  const [state, setState] = useState<RecordingState>('idle');
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Check for browser support
    if (typeof window !== 'undefined') {
      const SpeechRecognition =
        (window as any).SpeechRecognition ||
        (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US';

        recognitionRef.current.onresult = (event: any) => {
          let interimTranscript = '';
          let finalTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript;
            } else {
              interimTranscript += transcript;
            }
          }

          setTranscript(finalTranscript || interimTranscript);
        };

        recognitionRef.current.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          setState('idle');
        };

        recognitionRef.current.onend = () => {
          if (state === 'recording') {
            setState('processing');
            setTimeout(() => {
              if (transcript) {
                onTranscript(transcript);
                setState('done');
                setTimeout(() => setState('idle'), 1500);
              } else {
                setState('idle');
              }
            }, 500);
          }
        };
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  const toggleRecording = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in your browser.');
      return;
    }

    if (state === 'recording') {
      recognitionRef.current.stop();
    } else {
      setTranscript('');
      setState('recording');
      recognitionRef.current.start();
    }
  };

  return (
    <div className={cn('flex flex-col items-center gap-3', className)}>
      <Button
        type="button"
        variant={state === 'recording' ? 'destructive' : 'outline'}
        size="lg"
        onClick={toggleRecording}
        disabled={disabled || state === 'processing'}
        className={cn(
          'h-14 w-14 rounded-full p-0 transition-all',
          state === 'recording' && 'animate-pulse'
        )}
      >
        {state === 'idle' && <Mic className="h-6 w-6" />}
        {state === 'recording' && <MicOff className="h-6 w-6" />}
        {state === 'processing' && <Loader2 className="h-6 w-6 animate-spin" />}
        {state === 'done' && <Check className="h-6 w-6" />}
      </Button>

      <span className="text-xs text-muted-foreground text-center">
        {state === 'idle' && 'Click to speak'}
        {state === 'recording' && 'Listening... Click to stop'}
        {state === 'processing' && 'Processing...'}
        {state === 'done' && 'Added to your response!'}
      </span>

      {state === 'recording' && transcript && (
        <div className="text-sm text-foreground italic max-w-xs text-center animate-in fade-in">
          "{transcript}"
        </div>
      )}
    </div>
  );
}
