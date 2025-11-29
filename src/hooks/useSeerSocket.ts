import { useLordSocket } from './useLordSocket';

export const useSeerSocket = () => {
  return useLordSocket('seer');
};

export default useSeerSocket;
