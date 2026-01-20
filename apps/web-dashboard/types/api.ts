export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_verified: boolean;
  roles: string[];
  created_at: string;
  updated_at: string;
  links?: Record<string, string>;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserRegister {
  email: string;
  username: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface UserUpdate {
  username?: string;
  email?: string;
}

export interface WorkflowResponse {
  thread_id: string;
  status: string;
  state?: Record<string, unknown>;
  created_at: string;
  type: string;
}

export interface StruggleInput {
  edit_frequency: number;
  error_logs: string[];
  history: string[];
}

export interface AuditInput {
  diff_content: string;
  violations: string[];
}

export interface AuditResponse {
  id: string;
  status: string;
  repo: string;
  message: string;
  created_at?: string;
  violations?: string[];
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
