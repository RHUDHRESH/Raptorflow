import { useState, useCallback } from 'react';
import { ProofItem } from '@/lib/foundation';

export function useProofVault(initialItems: ProofItem[] = []) {
  const [items, setItems] = useState<ProofItem[]>(initialItems);

  const addItem = useCallback((newItem: Omit<ProofItem, 'id'>) => {
    const item: ProofItem = {
      ...newItem,
      id: `proof_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    };
    setItems((prev) => [...prev, item]);
    return item;
  }, []);

  const updateItem = useCallback((id: string, updates: Partial<ProofItem>) => {
    setItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, ...updates } : item))
    );
  }, []);

  const deleteItem = useCallback((id: string) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  }, []);

  const getItemsByType = useCallback(
    (type: ProofItem['type']) => {
      return items.filter((item) => item.type === type);
    },
    [items]
  );

  const getItemsByPhase = useCallback(
    (phase: number) => {
      return items.filter((item) => item.linkedPhases?.includes(phase));
    },
    [items]
  );

  const getVerifiedItems = useCallback(() => {
    return items.filter((item) => item.verified);
  }, [items]);

  const getTopRatedItems = useCallback(
    (minRating: number = 4) => {
      return items.filter((item) => item.rating && item.rating >= minRating);
    },
    [items]
  );

  const searchItems = useCallback(
    (query: string) => {
      const lowercaseQuery = query.toLowerCase();
      return items.filter(
        (item) =>
          item.title.toLowerCase().includes(lowercaseQuery) ||
          item.content.toLowerCase().includes(lowercaseQuery) ||
          item.tags.some((tag) => tag.toLowerCase().includes(lowercaseQuery)) ||
          item.source?.toLowerCase().includes(lowercaseQuery)
      );
    },
    [items]
  );

  return {
    items,
    addItem,
    updateItem,
    deleteItem,
    getItemsByType,
    getItemsByPhase,
    getVerifiedItems,
    getTopRatedItems,
    searchItems,
  };
}
