declare module 'express' {
  export interface Request {
    headers: Record<string, any>;
    params: Record<string, any>;
    query: Record<string, any>;
    body: any;
  }

  export interface Response {
    status(code: number): Response;
    json(body: any): any;
  }

  export function Router(): any;
}
