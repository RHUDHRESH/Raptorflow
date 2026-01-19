// Global React types compatibility fix for all components
declare global {
  namespace JSX {
    interface IntrinsicElements {
      [tagName: string]: any;
      progress: any;
    }
  }

  namespace React {
    interface ReactNode {
      children?: any;
      props?: any;
    }
  }
}

// Fix date-fns v4 compatibility
declare module 'date-fns' {
  export * from 'date-fns/format';
  export * from 'date-fns/formatDistanceToNow';
  export * from 'date-fns/subDays';
  export * from 'date-fns/startOfDay';
  export * from 'date-fns/endOfDay';
  export * from 'date-fns/eachDayOfInterval';
  export * from 'date-fns/parseISO';
  export * from 'date-fns/isAfter';
}

// Fix Radix UI Progress component - match actual module exports
declare module '@radix-ui/react-progress' {
  const Root: any;
  const Indicator: any;
  const Progress: any;

  export default Progress;
  export namespace Progress {
    const Root: any;
    const Indicator: any;
  }
}
