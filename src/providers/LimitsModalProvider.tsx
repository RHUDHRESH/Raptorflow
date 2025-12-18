import React from 'react';

const Context = React.createContext({
    openLimitModal: (args: any) => { console.log('Open Limit Modal', args) }
});

export const useLimitsModal = () => React.useContext(Context);

export const LimitsModalProvider = ({ children }: { children: React.ReactNode }) => {
    return (
        <Context.Provider value={{ openLimitModal: (args) => console.log('Open Limit Modal', args) }}>
            {children}
        </Context.Provider>
    );
};
