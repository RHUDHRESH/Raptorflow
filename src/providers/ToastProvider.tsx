import React from 'react';
// Re-export sonner's toast for convenience if needed, but here we provide a context hook as requested by usage
import { toast as sonnerToast } from 'sonner';

const Context = React.createContext({
    toast: (args: any) => { sonnerToast(args.title, { description: args.description }) }
});

export const useToast = () => React.useContext(Context);

export const ToastProvider = ({ children }: { children: React.ReactNode }) => {
    return (
        <Context.Provider value={{ toast: (args: any) => sonnerToast(args.title, { description: args.description }) }}>
            {children}
        </Context.Provider>
    );
};
