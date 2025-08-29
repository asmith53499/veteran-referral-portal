'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { referralsAPI, outcomesAPI } from '@/lib/api';
import { ReferralStats, OutcomeStats } from '@/types';
import DashboardLayout from '@/components/DashboardLayout';
import {
  ChartBarIcon,
  DocumentTextIcon,
  ClipboardDocumentListIcon,
  ClockIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [referralStats, setReferralStats] = useState<ReferralStats | null>(null);
  const [outcomeStats, setOutcomeStats] = useState<OutcomeStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [refStats, outStats] = await Promise.all([
          referralsAPI.getStats(),
          outcomesAPI.getStats(),
        ]);
        setReferralStats(refStats);
        setOutcomeStats(outStats);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
        // Don't show error for 401/403 - user just needs to login
        if (error && typeof error === 'object' && 'response' in error) {
          const axiosError = error as { response: { status: number } };
          if (axiosError.response?.status === 401 || axiosError.response?.status === 403) {
            // User needs to login, redirect to login
            router.push('/login');
            return;
          }
        }
      } finally {
        setLoading(false);
      }
    };

    // Only fetch stats if user is authenticated
    if (user) {
      fetchStats();
    } else {
      setLoading(false);
    }
  }, [user, router]);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  const stats = [
    {
      name: 'Total Referrals',
      value: referralStats?.total_referrals || 0,
      icon: DocumentTextIcon,
      color: 'bg-blue-500',
    },
    {
      name: 'Total Outcomes',
      value: outcomeStats?.total_outcomes || 0,
      icon: ClipboardDocumentListIcon,
      color: 'bg-green-500',
    },
    {
      name: 'Avg Time to Contact',
      value: outcomeStats?.avg_time_to_contact 
        ? `${Math.round(outcomeStats.avg_time_to_contact)}h`
        : 'N/A',
      icon: ClockIcon,
      color: 'bg-yellow-500',
    },
    {
      name: 'Completion Rate',
      value: referralStats && outcomeStats
        ? `${Math.round((outcomeStats.total_outcomes / referralStats.total_referrals) * 100)}%`
        : 'N/A',
      icon: CheckCircleIcon,
      color: 'bg-purple-500',
    },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                      <p className="text-gray-600">
              Welcome to the Veteran Referral Outcomes Portal. Here&apos;s an overview of your data.
            </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((item) => (
            <div
              key={item.name}
              className="relative overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:px-6"
            >
              <dt>
                <div className={`absolute rounded-md p-3 ${item.color}`}>
                  <item.icon className="h-6 w-6 text-white" />
                </div>
                <p className="ml-16 truncate text-sm font-medium text-gray-500">
                  {item.name}
                </p>
              </dt>
              <dd className="ml-16 flex items-baseline">
                <p className="text-2xl font-semibold text-gray-900">{item.value}</p>
              </dd>
            </div>
          ))}
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Referrals by Program */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Referrals by Program</h3>
            {referralStats?.by_program ? (
              <div className="space-y-3">
                {Object.entries(referralStats.by_program).map(([program, count]) => (
                  <div key={program} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">{program}</span>
                    <span className="text-sm font-medium text-gray-900">{count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No referral data available</p>
            )}
          </div>

          {/* Outcomes by Status */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Outcomes by Status</h3>
            {outcomeStats?.by_status ? (
              <div className="space-y-3">
                {Object.entries(outcomeStats.by_status).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">{status}</span>
                    <span className="text-sm font-medium text-gray-900">{count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No outcome data available</p>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <a
              href="/referrals"
              className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
            >
              <DocumentTextIcon className="h-6 w-6 text-blue-600" />
              <div className="flex-1 min-w-0">
                <span className="absolute inset-0" aria-hidden="true" />
                <p className="text-sm font-medium text-gray-900">View Referrals</p>
                <p className="text-sm text-gray-500">Browse all referrals</p>
              </div>
            </a>

            <a
              href="/outcomes"
              className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
            >
              <ClipboardDocumentListIcon className="h-6 w-6 text-green-600" />
              <div className="flex-1 min-w-0">
                <span className="absolute inset-0" aria-hidden="true" />
                <p className="text-sm font-medium text-gray-900">Manage Outcomes</p>
                <p className="text-sm text-gray-500">Track referral outcomes</p>
              </div>
            </a>

            <a
              href="/outcomes?action=create"
              className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
            >
              <CheckCircleIcon className="h-6 w-6 text-purple-600" />
              <div className="flex-1 min-w-0">
                <span className="absolute inset-0" aria-hidden="true" />
                <p className="text-sm font-medium text-gray-900">Add Outcome</p>
                <p className="text-sm text-gray-500">Create new outcome</p>
              </div>
            </a>

            <a
              href="/referrals?action=import"
              className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
            >
              <ChartBarIcon className="h-6 w-6 text-orange-600" />
              <div className="flex-1 min-w-0">
                <span className="absolute inset-0" aria-hidden="true" />
                <p className="text-sm font-medium text-gray-900">Import Data</p>
                <p className="text-sm text-gray-500">Upload CSV file</p>
              </div>
            </a>
          </div>
        </div>

        {/* User Info */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Account Information</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <p className="text-sm text-gray-500">Name</p>
              <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Role</p>
              <p className="text-sm font-medium text-gray-900">{user?.role}</p>
            </div>
            {user?.vsa_id && (
              <div>
                <p className="text-sm text-gray-500">VSA ID</p>
                <p className="text-sm font-medium text-gray-900">{user.vsa_id}</p>
              </div>
            )}
            <div>
              <p className="text-sm text-gray-500">Email</p>
              <p className="text-sm font-medium text-gray-900">{user?.email}</p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
