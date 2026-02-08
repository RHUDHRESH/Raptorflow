import { toast } from "sonner";

type NotifyFn = (message: string, description?: string) => void;

export const notify = {
  success: ((message: string, description?: string) =>
    description ? toast.success(message, { description }) : toast.success(message)) as NotifyFn,
  error: ((message: string, description?: string) =>
    description ? toast.error(message, { description }) : toast.error(message)) as NotifyFn,
  info: ((message: string, description?: string) =>
    description ? toast(message, { description }) : toast(message)) as NotifyFn,
};
