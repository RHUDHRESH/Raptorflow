"use client";

// Advanced Audio Engine for 10x Typing Experience
export interface SoundProfile {
  name: string;
  keySound: AudioBuffer;
  clickSound: AudioBuffer;
  backspaceSound: AudioBuffer;
  completionSound: AudioBuffer;
  characteristics: {
    bass: number;
    mid: number;
    high: number;
    resonance: number;
  };
}

export interface AudioConfig {
  volume: number;
  adaptiveVolume: boolean;
  spatialAudio: boolean;
  soundProfile: string;
  sensitivityMode: 'normal' | 'reduced' | 'minimal';
}

export class AudioEngine {
  private audioContext: AudioContext | null = null;
  private soundProfiles: Map<string, SoundProfile> = new Map();
  private gainNode: GainNode | null = null;
  private pannerNode: StereoPannerNode | null = null;
  private config: AudioConfig;
  private bufferPool: AudioBuffer[] = [];
  private isInitialized = false;

  constructor(config: AudioConfig) {
    this.config = config;
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Create audio context with proper fallback
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioContextClass) {
        console.warn('Web Audio API not supported');
        return;
      }

      this.audioContext = new AudioContextClass();

      // Resume audio context if suspended (browser requirement)
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }

      // Create gain node for volume control
      this.gainNode = this.audioContext.createGain();
      this.gainNode.gain.value = this.config.volume;

      // Create stereo panner for spatial audio
      this.pannerNode = this.audioContext.createStereoPanner();
      this.pannerNode.pan.value = 0;

      // Connect nodes
      this.gainNode.connect(this.audioContext.destination);
      this.pannerNode.connect(this.gainNode);

      // Initialize sound profiles
      await this.initializeSoundProfiles();

      this.isInitialized = true;
      console.log('Audio engine initialized successfully');

    } catch (error) {
      console.error('Failed to initialize audio engine:', error);
      throw error;
    }
  }

  private async initializeSoundProfiles(): Promise<void> {
    if (!this.audioContext) return;

    const sampleRate = this.audioContext.sampleRate;

    // Create Professional Profile
    const professionalProfile = await this.createProfessionalProfile(sampleRate);
    this.soundProfiles.set('professional', professionalProfile);

    // Create Creative Profile
    const creativeProfile = await this.createCreativeProfile(sampleRate);
    this.soundProfiles.set('creative', creativeProfile);

    // Create Gaming Profile
    const gamingProfile = await this.createGamingProfile(sampleRate);
    this.soundProfiles.set('gaming', gamingProfile);

    // Create Minimalist Profile
    const minimalistProfile = await this.createMinimalistProfile(sampleRate);
    this.soundProfiles.set('minimalist', minimalistProfile);
  }

  private async createProfessionalProfile(sampleRate: number): Promise<SoundProfile> {
    const duration = 0.06;
    const keyBuffer = this.audioContext!.createBuffer(1, duration * sampleRate, sampleRate);
    const keyData = keyBuffer.getChannelData(0);

    // Professional: Based on 432 Hz "Earth's natural frequency" for grounding
    for (let i = 0; i < keyData.length; i++) {
      const t = i / sampleRate;
      keyData[i] = Math.sin(2 * Math.PI * 216 * t) * 0.08 * Math.exp(-80 * t) +  // 432/2 - subharmonic
                  Math.sin(2 * Math.PI * 432 * t) * 0.04 * Math.exp(-100 * t) +  // 432 Hz - grounding
                  Math.sin(2 * Math.PI * 648 * t) * 0.02 * Math.exp(-120 * t); // 432*1.5 - harmonic
    }

    const clickBuffer = this.audioContext!.createBuffer(1, 0.015 * sampleRate, sampleRate);
    const clickData = clickBuffer.getChannelData(0);
    for (let i = 0; i < clickData.length; i++) {
      const t = i / sampleRate;
      clickData[i] = Math.sin(2 * Math.PI * 528 * t) * 0.06 * Math.exp(-400 * t); // 528 Hz - love frequency
    }

    const backspaceBuffer = this.audioContext!.createBuffer(1, 0.04 * sampleRate, sampleRate);
    const backspaceData = backspaceBuffer.getChannelData(0);
    for (let i = 0; i < backspaceData.length; i++) {
      const t = i / sampleRate;
      backspaceData[i] = Math.sin(2 * Math.PI * 174 * t) * 0.1 * Math.exp(-60 * t) +  // 174 Hz - physical relaxation
                        Math.sin(2 * Math.PI * 348 * t) * 0.04 * Math.exp(-80 * t);  // 174*2 - harmonic
    }

    const completionBuffer = this.audioContext!.createBuffer(1, 0.12 * sampleRate, sampleRate);
    const completionData = completionBuffer.getChannelData(0);
    for (let i = 0; i < completionData.length; i++) {
      const t = i / sampleRate;
      completionData[i] = (Math.sin(2 * Math.PI * 432 * t) * 0.12 +   // 432 Hz - grounding
                           Math.sin(2 * Math.PI * 528 * t) * 0.08 +   // 528 Hz - emotional balance
                           Math.sin(2 * Math.PI * 639 * t) * 0.04) *  // 639 Hz - harmony
                          Math.exp(-4 * t); // Gentle fade
    }

    return {
      name: 'professional',
      keySound: keyBuffer,
      clickSound: clickBuffer,
      backspaceSound: backspaceBuffer,
      completionSound: completionBuffer,
      characteristics: { bass: 0.7, mid: 0.25, high: 0.05, resonance: 0.15 }
    };
  }

  private async createCreativeProfile(sampleRate: number): Promise<SoundProfile> {
    const duration = 0.05;
    const keyBuffer = this.audioContext!.createBuffer(1, duration * sampleRate, sampleRate);
    const keyData = keyBuffer.getChannelData(0);

    // Creative: 528 Hz "Love Frequency" for emotional balance
    for (let i = 0; i < keyData.length; i++) {
      const t = i / sampleRate;
      keyData[i] = Math.sin(2 * Math.PI * 264 * t) * 0.06 * Math.exp(-90 * t) +  // 528/2 - subharmonic
                  Math.sin(2 * Math.PI * 528 * t) * 0.03 * Math.exp(-110 * t) +  // 528 Hz - love frequency
                  Math.sin(2 * Math.PI * 792 * t) * 0.01 * Math.exp(-130 * t); // 528*1.5 - harmonic
    }

    const clickBuffer = this.audioContext!.createBuffer(1, 0.012 * sampleRate, sampleRate);
    const clickData = clickBuffer.getChannelData(0);
    for (let i = 0; i < clickData.length; i++) {
      const t = i / sampleRate;
      clickData[i] = Math.sin(2 * Math.PI * 639 * t) * 0.05 * Math.exp(-500 * t); // 639 Hz - connection/harmony
    }

    const backspaceBuffer = this.audioContext!.createBuffer(1, 0.03 * sampleRate, sampleRate);
    const backspaceData = backspaceBuffer.getChannelData(0);
    for (let i = 0; i < backspaceData.length; i++) {
      const t = i / sampleRate;
      backspaceData[i] = Math.sin(2 * Math.PI * 216 * t) * 0.08 * Math.exp(-70 * t) +  // 432/2 - grounding
                        Math.sin(2 * Math.PI * 432 * t) * 0.03 * Math.exp(-90 * t);  // 432 Hz - calming
    }

    const completionBuffer = this.audioContext!.createBuffer(1, 0.1 * sampleRate, sampleRate);
    const completionData = completionBuffer.getChannelData(0);
    for (let i = 0; i < completionData.length; i++) {
      const t = i / sampleRate;
      completionData[i] = (Math.sin(2 * Math.PI * 528 * t) * 0.1 +    // 528 Hz - emotional balance
                           Math.sin(2 * Math.PI * 639 * t) * 0.06 +   // 639 Hz - harmony
                           Math.sin(2 * Math.PI * 741 * t) * 0.03) *  // 528+213 - gentle lift
                          Math.exp(-5 * t); // Slow fade
    }

    return {
      name: 'creative',
      keySound: keyBuffer,
      clickSound: clickBuffer,
      backspaceSound: backspaceBuffer,
      completionSound: completionBuffer,
      characteristics: { bass: 0.8, mid: 0.15, high: 0.05, resonance: 0.1 }
    };
  }

  private async createGamingProfile(sampleRate: number): Promise<SoundProfile> {
    const duration = 0.04;
    const keyBuffer = this.audioContext!.createBuffer(1, duration * sampleRate, sampleRate);
    const keyData = keyBuffer.getChannelData(0);

    // Gaming: Alpha waves (8-12 Hz) for relaxed alertness - scaled up to audible range
    for (let i = 0; i < keyData.length; i++) {
      const t = i / sampleRate;
      keyData[i] = Math.sin(2 * Math.PI * 216 * t) * 0.05 * Math.exp(-100 * t) +  // 432/2 - grounding
                  Math.sin(2 * Math.PI * 432 * t) * 0.025 * Math.exp(-120 * t) + // 432 Hz - calming
                  Math.sin(2 * Math.PI * 648 * t) * 0.01 * Math.exp(-140 * t); // 432*1.5 - harmonic
    }

    const clickBuffer = this.audioContext!.createBuffer(1, 0.01 * sampleRate, sampleRate);
    const clickData = clickBuffer.getChannelData(0);
    for (let i = 0; i < clickData.length; i++) {
      const t = i / sampleRate;
      clickData[i] = Math.sin(2 * Math.PI * 528 * t) * 0.04 * Math.exp(-600 * t); // 528 Hz - love frequency
    }

    const backspaceBuffer = this.audioContext!.createBuffer(1, 0.025 * sampleRate, sampleRate);
    const backspaceData = backspaceBuffer.getChannelData(0);
    for (let i = 0; i < backspaceData.length; i++) {
      const t = i / sampleRate;
      backspaceData[i] = Math.sin(2 * Math.PI * 174 * t) * 0.06 * Math.exp(-80 * t) +  // 174 Hz - physical relaxation
                        Math.sin(2 * Math.PI * 348 * t) * 0.02 * Math.exp(-100 * t);  // 174*2 - harmonic
    }

    const completionBuffer = this.audioContext!.createBuffer(1, 0.08 * sampleRate, sampleRate);
    const completionData = completionBuffer.getChannelData(0);
    for (let i = 0; i < completionData.length; i++) {
      const t = i / sampleRate;
      completionData[i] = (Math.sin(2 * Math.PI * 432 * t) * 0.08 +   // 432 Hz - grounding
                           Math.sin(2 * Math.PI * 528 * t) * 0.05 +   // 528 Hz - emotional balance
                           Math.sin(2 * Math.PI * 639 * t) * 0.02) *  // 639 Hz - harmony
                          Math.exp(-6 * t); // Very slow fade
    }

    return {
      name: 'gaming',
      keySound: keyBuffer,
      clickSound: clickBuffer,
      backspaceSound: backspaceBuffer,
      completionSound: completionBuffer,
      characteristics: { bass: 0.85, mid: 0.12, high: 0.03, resonance: 0.08 }
    };
  }

  private async createMinimalistProfile(sampleRate: number): Promise<SoundProfile> {
    const duration = 0.03;
    const keyBuffer = this.audioContext!.createBuffer(1, duration * sampleRate, sampleRate);
    const keyData = keyBuffer.getChannelData(0);

    // Minimalist: Theta waves (4-8 Hz) for deep relaxation - scaled to audible range
    for (let i = 0; i < keyData.length; i++) {
      const t = i / sampleRate;
      keyData[i] = Math.sin(2 * Math.PI * 174 * t) * 0.03 * Math.exp(-120 * t); // 174 Hz - physical relaxation
    }

    const clickBuffer = this.audioContext!.createBuffer(1, 0.006 * sampleRate, sampleRate);
    const clickData = clickBuffer.getChannelData(0);
    for (let i = 0; i < clickData.length; i++) {
      const t = i / sampleRate;
      clickData[i] = Math.sin(2 * Math.PI * 216 * t) * 0.02 * Math.exp(-800 * t); // 432/2 - ultra gentle
    }

    const backspaceBuffer = this.audioContext!.createBuffer(1, 0.015 * sampleRate, sampleRate);
    const backspaceData = backspaceBuffer.getChannelData(0);
    for (let i = 0; i < backspaceData.length; i++) {
      const t = i / sampleRate;
      backspaceData[i] = Math.sin(2 * Math.PI * 136 * t) * 0.04 * Math.exp(-100 * t); // 174*0.78 - ultra low
    }

    const completionBuffer = this.audioContext!.createBuffer(1, 0.06 * sampleRate, sampleRate);
    const completionData = completionBuffer.getChannelData(0);
    for (let i = 0; i < completionData.length; i++) {
      const t = i / sampleRate;
      completionData[i] = Math.sin(2 * Math.PI * 174 * t) * 0.05 * Math.exp(-8 * t); // 174 Hz - deep relaxation
    }

    return {
      name: 'minimalist',
      keySound: keyBuffer,
      clickSound: clickBuffer,
      backspaceSound: backspaceBuffer,
      completionSound: completionBuffer,
      characteristics: { bass: 0.95, mid: 0.05, high: 0, resonance: 0.03 }
    };
  }

  playSound(soundType: 'key' | 'click' | 'backspace' | 'completion', options: {
    velocity?: number;
    spatialPosition?: number;
    pitchVariation?: number;
  } = {}): void {
    if (!this.audioContext || !this.isInitialized) return;

    const velocity = options.velocity || 0.8;
    const spatialPosition = options.spatialPosition || 0;
    const pitchVariation = options.pitchVariation || 0;

    const profile = this.soundProfiles.get(this.config.soundProfile);
    if (!profile) return;

    let buffer: AudioBuffer | null = null;
    switch (soundType) {
      case 'key':
        buffer = profile.keySound;
        break;
      case 'click':
        buffer = profile.clickSound;
        break;
      case 'backspace':
        buffer = profile.backspaceSound;
        break;
      case 'completion':
        buffer = profile.completionSound;
        break;
    }

    if (!buffer) return;

    const source = this.audioContext.createBufferSource();
    source.buffer = buffer;

    // Apply velocity and pitch variation
    const playbackRate = 1 + (pitchVariation * (velocity - 0.5) * 0.2);
    source.playbackRate.value = playbackRate;

    // Create gain envelope for velocity
    const gainNode = this.audioContext.createGain();
    gainNode.gain.value = velocity * this.config.volume;

    // Apply spatial positioning
    if (this.config.spatialAudio && this.pannerNode) {
      this.pannerNode.pan.value = spatialPosition;
      source.connect(this.pannerNode);
    } else {
      source.connect(gainNode);
      gainNode.connect(this.audioContext.destination);
    }

    source.start(0);
  }

  updateConfig(newConfig: Partial<AudioConfig>): void {
    this.config = { ...this.config, ...newConfig };

    if (this.gainNode) {
      this.gainNode.gain.value = this.config.volume;
    }
  }

  getAvailableProfiles(): string[] {
    return Array.from(this.soundProfiles.keys());
  }

  getCurrentProfile(): SoundProfile | undefined {
    return this.soundProfiles.get(this.config.soundProfile);
  }

  cleanup(): void {
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }

    this.soundProfiles.clear();
    this.bufferPool = [];
    this.isInitialized = false;
  }
}
