export interface RaptorResponse<T = any> {
  success: boolean;
  data: T | null;
  error: {
    code: string;
    message: string;
    details?: any;
  } | null;
  meta: {
    timestamp: string;
    requestId?: string;
    [key: string]: any;
  };
}
