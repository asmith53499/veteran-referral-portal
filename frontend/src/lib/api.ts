import axios from 'axios';
import {
  AuthResponse,
  User,
  Referral,
  ReferralListResponse,
  ReferralStats,
  Outcome,
  OutcomeListResponse,
  OutcomeStats,
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: `${API_URL}/v1`,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: async (username: string, password: string): Promise<AuthResponse> => {
    const form = new URLSearchParams();
    form.append('username', username);
    form.append('password', password);
    const { data } = await client.post<AuthResponse>('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return data;
  },

  getProfile: async (): Promise<User> => {
    const { data } = await client.get<User>('/auth/users/me');
    return data;
  },
};

export const referralsAPI = {
  list: async (): Promise<ReferralListResponse> => {
    const { data } = await client.get<ReferralListResponse>('/referrals');
    return data;
  },

  get: async (referralToken: string): Promise<Referral> => {
    const { data } = await client.get<Referral>(`/referrals/${referralToken}`);
    return data;
  },

  getStats: async (): Promise<ReferralStats> => {
    const { data } = await client.get<ReferralStats>('/referrals/summary/stats');
    return data;
  },
};

export const outcomesAPI = {
  list: async (): Promise<OutcomeListResponse> => {
    const { data } = await client.get<OutcomeListResponse>('/outcomes');
    return data;
  },

  getStats: async (): Promise<OutcomeStats> => {
    const { data } = await client.get<OutcomeStats>('/outcomes/summary/stats');
    return data;
  },

  create: async (outcome: Partial<Outcome>): Promise<Outcome> => {
    const { data } = await client.post<Outcome>('/outcomes', outcome);
    return data;
  },

  update: async (id: string, outcome: Partial<Outcome>): Promise<Outcome> => {
    const { data } = await client.put<Outcome>(`/outcomes/${id}`, outcome);
    return data;
  },
};
