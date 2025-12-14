declare module 'lenis' {
  interface LenisOptions {
    wrapper?: Window | HTMLElement;
    content?: HTMLElement;
    wheelEventsTarget?: Window | HTMLElement;
    smoothWheel?: boolean;
    smoothTouch?: boolean;
    syncTouch?: boolean;
    syncTouchLerp?: number;
    touchInertiaMultiplier?: number;
    duration?: number;
    smooth?: boolean;
    easing?: (t: number) => number;
    lerp?: number;
    infinite?: boolean;
    gestureOrientation?: 'vertical' | 'horizontal' | 'both';
    orientation?: 'vertical' | 'horizontal';
    touchMultiplier?: number;
    wheelMultiplier?: number;
    normalizeWheel?: boolean;
    autoResize?: boolean;
  }

  class Lenis {
    constructor(options?: LenisOptions);
    raf(time: number): void;
    destroy(): void;
    on(event: string, callback: (e: any) => void): void;
    off(event: string, callback: (e: any) => void): void;
    scrollTo(target: number | string | HTMLElement, options?: { offset?: number; immediate?: boolean; duration?: number; easing?: (t: number) => number }): void;
    start(): void;
    stop(): void;
    reset(): void;
    isScrolling: boolean;
    isStopped: boolean;
    velocity: number;
    direction: number;
    animatedScroll: number;
    rootElement: HTMLElement;
    options: LenisOptions;
  }

  export default Lenis;
}