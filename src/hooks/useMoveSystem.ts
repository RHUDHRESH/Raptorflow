/**
 * React hooks for the Move System
 * Provides easy access to Move System data with loading/error states
 */

import { useState, useEffect } from 'react';
import { moveService } from '../lib/services/move-service';
import { techTreeService, CapabilityNode } from '../lib/services/tech-tree-service';
import { sprintService } from '../lib/services/sprint-service';
import { icpService } from '../lib/services/icp-service';

// Helper to get workspace ID (you'll need to implement this based on your auth)
const getWorkspaceId = (): string => {
  // TODO: Get from auth context or user metadata
  // For now, return a placeholder
  return 'YOUR_WORKSPACE_ID';
};

/**
 * Hook to fetch maneuver types
 */
export function useManeuverTypes() {
  const [maneuverTypes, setManeuverTypes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await moveService.getManeuverTypes();
        setManeuverTypes(data);
        setError(null);
      } catch (err) {
        setError(err as Error);
        console.error('Error fetching maneuver types:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return { maneuverTypes, loading, error };
}

/**
 * Hook to fetch capability nodes
 */
export function useCapabilityNodes() {
  const [capabilityNodes, setCapabilityNodes] = useState<CapabilityNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const workspaceId = getWorkspaceId();
        const data = await techTreeService.getCapabilityNodes(workspaceId);
        setCapabilityNodes(data);
        setError(null);
      } catch (err) {
        setError(err as Error);
        console.error('Error fetching capability nodes:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const unlockNode = async (nodeId: string) => {
    try {
      const updated = await techTreeService.unlockNode(nodeId);
      setCapabilityNodes(prev => 
        prev.map(node => node.id === nodeId ? updated : node)
      );
      return updated;
    } catch (err) {
      console.error('Error unlocking node:', err);
      throw err;
    }
  };

  return { capabilityNodes, loading, error, unlockNode };
}

/**
 * Hook to fetch moves
 */
export function useMoves() {
  const [moves, setMoves] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const workspaceId = getWorkspaceId();
        const data = await moveService.getMoves(workspaceId);
        setMoves(data);
        setError(null);
      } catch (err) {
        setError(err as Error);
        console.error('Error fetching moves:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const createMove = async (moveData: any) => {
    try {
      const workspaceId = getWorkspaceId();
      const newMove = await moveService.createMove({
        ...moveData,
        workspace_id: workspaceId,
      });
      setMoves(prev => [newMove, ...prev]);
      return newMove;
    } catch (err) {
      console.error('Error creating move:', err);
      throw err;
    }
  };

  const updateMove = async (moveId: string, updates: any) => {
    try {
      const updated = await moveService.updateMove(moveId, updates);
      setMoves(prev => 
        prev.map(move => move.id === moveId ? updated : move)
      );
      return updated;
    } catch (err) {
      console.error('Error updating move:', err);
      throw err;
    }
  };

  const deleteMove = async (moveId: string) => {
    try {
      await moveService.deleteMove(moveId);
      setMoves(prev => prev.filter(move => move.id !== moveId));
    } catch (err) {
      console.error('Error deleting move:', err);
      throw err;
    }
  };

  return { moves, loading, error, createMove, updateMove, deleteMove };
}

/**
 * Hook to fetch sprints
 */
export function useSprints() {
  const [sprints, setSprints] = useState<any[]>([]);
  const [activeSprint, setActiveSprint] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [allSprints, active] = await Promise.all([
          sprintService.getAll(),
          sprintService.getActive(),
        ]);
        setSprints(allSprints);
        setActiveSprint(active);
        setError(null);
      } catch (err) {
        setError(err as Error);
        console.error('Error fetching sprints:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const createSprint = async (sprintData: any) => {
    try {
      const workspaceId = getWorkspaceId();
      const newSprint = await sprintService.create({
        ...sprintData,
        workspace_id: workspaceId,
      });
      setSprints(prev => [newSprint, ...prev]);
      return newSprint;
    } catch (err) {
      console.error('Error creating sprint:', err);
      throw err;
    }
  };

  return { sprints, activeSprint, loading, error, createSprint };
}

/**
 * Hook to fetch ICPs/Cohorts
 */
export function useICPs() {
  const [icps, setIcps] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await icpService.getAll();
        setIcps(data);
        setError(null);
      } catch (err) {
        setError(err as Error);
        console.error('Error fetching ICPs:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const createICP = async (icpData: any) => {
    try {
      const workspaceId = getWorkspaceId();
      const newICP = await icpService.create({
        ...icpData,
        workspace_id: workspaceId,
      });
      setIcps(prev => [newICP, ...prev]);
      return newICP;
    } catch (err) {
      console.error('Error creating ICP:', err);
      throw err;
    }
  };

  return { icps, loading, error, createICP };
}

/**
 * Hook to check which maneuvers are unlocked
 */
export function useUnlockedManeuvers() {
  const { maneuverTypes, loading: maneuversLoading } = useManeuverTypes();
  const { capabilityNodes, loading: capabilitiesLoading } = useCapabilityNodes();
  const [unlockedManeuvers, setUnlockedManeuvers] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkUnlocked = async () => {
      if (maneuversLoading || capabilitiesLoading) {
        return;
      }

      try {
        setLoading(true);
        const workspaceId = getWorkspaceId();
        
        // Check each maneuver type
        const unlocked = await Promise.all(
          maneuverTypes.map(async (mt) => {
            const isUnlocked = await techTreeService.isManeuverUnlocked(mt.id, workspaceId);
            return isUnlocked ? mt.id : null;
          })
        );

        setUnlockedManeuvers(unlocked.filter(Boolean) as string[]);
      } catch (err) {
        console.error('Error checking unlocked maneuvers:', err);
      } finally {
        setLoading(false);
      }
    };

    checkUnlocked();
  }, [maneuverTypes, capabilityNodes, maneuversLoading, capabilitiesLoading]);

  return { unlockedManeuvers, loading };
}





