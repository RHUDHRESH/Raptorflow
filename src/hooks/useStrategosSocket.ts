import { useLordSocket } from './useLordSocket';

export const useStrategosSocket = () => {
  return useLordSocket('strategos');
};

export default useStrategosSocket;
