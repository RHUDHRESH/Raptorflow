import { useLordSocket } from './useLordSocket';

export const useCognitionSocket = () => {
  return useLordSocket('cognition');
};

export default useCognitionSocket;
