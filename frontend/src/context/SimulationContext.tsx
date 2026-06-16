/* eslint-disable */
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface SimulationContextType {
  isSimulating: boolean;
  activeSimId: string | null;
  startSimulation: (id: string) => void;
  stopSimulation: () => void;
}

const SimulationContext = createContext<SimulationContextType | undefined>(undefined);

export const SimulationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isSimulating, setIsSimulating] = useState(false);
  const [activeSimId, setActiveSimId] = useState<string | null>(null);

  const startSimulation = (id: string) => {
    setIsSimulating(true);
    setActiveSimId(id);
  };

  const stopSimulation = () => {
    setIsSimulating(false);
    setActiveSimId(null);
  };

  return (
    <SimulationContext.Provider value={{ isSimulating, activeSimId, startSimulation, stopSimulation }}>
      {children}
    </SimulationContext.Provider>
  );
};

export const useSimulation = () => {
  const context = useContext(SimulationContext);
  if (context === undefined) {
    throw new Error('useSimulation must be used within a SimulationProvider');
  }
  return context;
};
