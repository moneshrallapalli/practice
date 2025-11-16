/**
 * Summary statistics component
 */
import React from 'react';
import { SummaryStats as Stats } from '../types';

interface SummaryStatsProps {
  stats: Stats | null;
}

const SummaryStats: React.FC<SummaryStatsProps> = ({ stats }) => {
  if (!stats) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold">Daily Summary</h2>
        </div>
        <div className="card-body">
          <div className="text-center text-gray-500 py-8">
            <div className="animate-pulse">Loading statistics...</div>
          </div>
        </div>
      </div>
    );
  }

  const statItems = [
    {
      label: 'Total Events',
      value: stats.total_events,
      icon: '📊',
      color: 'text-blue-400'
    },
    {
      label: 'Critical Alerts',
      value: stats.critical_alerts,
      icon: '🚨',
      color: 'text-red-400'
    },
    {
      label: 'Warning Alerts',
      value: stats.warning_alerts,
      icon: '⚠️',
      color: 'text-orange-400'
    },
    {
      label: 'Info Alerts',
      value: stats.info_alerts,
      icon: 'ℹ️',
      color: 'text-blue-300'
    },
    {
      label: 'Avg Response Time',
      value: `${stats.avg_response_time_seconds}s`,
      icon: '⏱️',
      color: 'text-green-400'
    },
    {
      label: 'Active Cameras',
      value: stats.active_cameras,
      icon: '📹',
      color: 'text-cyan-400'
    }
  ];

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-lg font-semibold">Daily Summary</h2>
        <p className="text-sm text-gray-400">Last {stats.period_hours} hours</p>
      </div>
      <div className="card-body">
        <div className="grid grid-cols-2 gap-4">
          {statItems.map((item, index) => (
            <div
              key={index}
              className="bg-dark-900/50 rounded-lg p-4 border border-dark-700 hover:border-dark-600 transition-colors"
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">{item.icon}</span>
                <span className="text-xs text-gray-400">{item.label}</span>
              </div>
              <div className={`text-2xl font-bold ${item.color}`}>
                {item.value}
              </div>
            </div>
          ))}
        </div>

        {stats.context_stats && (
          <div className="mt-4 pt-4 border-t border-dark-700">
            <h3 className="text-sm font-semibold text-gray-300 mb-2">Context Database</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Stored Scenes:</span>
                <span className="text-gray-200 font-semibold">{stats.context_stats.total_scenes}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Patterns:</span>
                <span className="text-gray-200 font-semibold">{stats.context_stats.total_patterns}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SummaryStats;
