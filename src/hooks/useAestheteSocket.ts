import { useLordSocket } from './useLordSocket';

export const useAestheteSocket = () => {
  return useLordSocket('aesthete');
};

export default useAestheteSocket;
