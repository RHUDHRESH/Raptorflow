import { useLordSocket } from './useLordSocket';

export const useArbiterSocket = () => {
  return useLordSocket('arbiter');
};

export default useArbiterSocket;
