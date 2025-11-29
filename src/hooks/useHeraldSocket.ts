import { useLordSocket } from './useLordSocket';

export const useHeraldSocket = () => {
  return useLordSocket('herald');
};

export default useHeraldSocket;
