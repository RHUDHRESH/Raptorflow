import { useLordSocket } from './useLordSocket';

export const useArchitectSocket = () => {
  return useLordSocket('architect');
};

export default useArchitectSocket;
