// Type definitions for the Veteran Referral Outcomes Portal

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: 'VA_ADMIN' | 'VSA_ADMIN' | 'VSA_USER';
  vsa_id?: string;
  is_active: boolean;
  is_verified: boolean;
  phone?: string;
  position?: string;
  department?: string;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface Referral {
  referral_token: string;
  issued_at: string;
  vsa_id: string;
  program_code: string;
  episode_id?: string;
  referral_type: string;
  priority_level: string;
  crisis_type?: string;
  urgency_indicator?: string;
  expected_contact_date?: string;
  va_facility_code?: string;
  created_at: string;
  updated_at: string;
}

export interface Outcome {
  id: string;
  referral_token: string;
  vsa_id: string;
  status: 'RECEIVED' | 'ENGAGED' | 'WAITLIST' | 'COMPLETED' | 'UNREACHABLE' | 'DECLINED' | 'TRANSFERRED' | 'OTHER';
  reason_code?: 'NO_SHOW' | 'CONTACT_FAILED' | 'CAPACITY' | 'INELIGIBLE' | 'WITHDREW' | 'OTHER_NONPII';
  first_contact_at?: string;
  closed_at?: string;
  notes?: string;
  updated_by: string;
  updated_at: string;
}

export interface ReferralListResponse {
  referrals: Referral[];
  total: number;
  page: number;
  size: number;
}

export interface OutcomeListResponse {
  outcomes: Outcome[];
  total: number;
  page: number;
  size: number;
}

export interface ReferralStats {
  total_referrals: number;
  by_program: Record<string, number>;
  by_priority: Record<string, number>;
  by_status: Record<string, number>;
  avg_time_to_outcome?: number;
  vsa_id?: string;
}

export interface OutcomeStats {
  total_outcomes: number;
  by_status: Record<string, number>;
  by_reason: Record<string, number>;
  avg_time_to_contact?: number;
  avg_time_to_close?: number;
  vsa_id?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  username: string;
  role: string;
  vsa_id?: string;
}

export interface LoginForm {
  username: string;
  password: string;
}

export interface OutcomeForm {
  referral_token: string;
  vsa_id: string;
  status: Outcome['status'];
  reason_code?: Outcome['reason_code'];
  first_contact_at?: string;
  closed_at?: string;
  notes?: string;
}

export interface OutcomeUpdateForm {
  status?: Outcome['status'];
  reason_code?: Outcome['reason_code'];
  first_contact_at?: string;
  closed_at?: string;
  notes?: string;
}

export interface BulkOutcomeForm {
  outcomes: OutcomeForm[];
}

export interface ApiError {
  detail: string;
  error?: string;
  event?: string;
  logger?: string;
  level?: string;
  timestamp?: string;
}
