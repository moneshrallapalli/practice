/**
 * Daily Summary Component - Interactive Statistics Dashboard
 */
import React from 'react';
import { SummaryStats } from '../types';

interface DailySummaryProps {
  stats: SummaryStats | null;
}

const DailySummary: React.FC<DailySummaryProps> = ({ stats }) => {
  // Use real stats if available, otherwise show dummy/default data
  const totalEvents = stats?.total_events || 0;
  const criticalAlerts = stats?.critical_alerts || 0;
  const warningAlerts = stats?.warning_alerts || 0;
  const infoAlerts = stats?.info_alerts || 0;
  const avgResponseTime = stats?.avg_response_time_seconds || 0;
  const activeCameras = stats?.active_cameras || 1;
  const storedScenes = stats?.context_stats?.total_scenes || 0; // From context database
  const patterns = stats?.context_stats?.total_patterns || 0; // From pattern recognition

  const formatResponseTime = (seconds: number): string => {
    if (seconds === 0) return '0s';
    if (seconds < 60) return `${Math.round(seconds)}s`;
    return `${Math.round(seconds / 60)}m`;
  };

  const statCards = [
    {
      id: 'events',
      icon: '📊',
      label: 'Total Events',
      value: totalEvents,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/20',
      hoverColor: 'hover:bg-blue-500/20'
    },
    {
      id: 'critical',
      icon: '🚨',
      label: 'Critical Alerts',
      value: criticalAlerts,
      color: 'from-red-500 to-red-600',
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/20',
      hoverColor: 'hover:bg-red-500/20'
    },
    {
      id: 'warning',
      icon: '⚠️',
      label: 'Warning Alerts',
      value: warningAlerts,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-500/10',
      borderColor: 'border-orange-500/20',
      hoverColor: 'hover:bg-orange-500/20'
    },
    {
      id: 'info',
      icon: 'ℹ️',
      label: 'Info Alerts',
      value: infoAlerts,
      color: 'from-cyan-500 to-cyan-600',
      bgColor: 'bg-cyan-500/10',
      borderColor: 'border-cyan-500/20',
      hoverColor: 'hover:bg-cyan-500/20'
    },
    {
      id: 'response',
      icon: '⏱️',
      label: 'Avg Response Time',
      value: formatResponseTime(avgResponseTime),
      valueColor: avgResponseTime === 0 ? 'text-green-400' : avgResponseTime < 30 ? 'text-green-400' : 'text-yellow-400',
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/20',
      hoverColor: 'hover:bg-green-500/20'
    },
    {
      id: 'cameras',
      icon: '📹',
      label: 'Active Cameras',
      value: activeCameras,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/20',
      hoverColor: 'hover:bg-purple-500/20'
    }
  ];

  return (
    <div className="card">
      <div className="card-header flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-100">Daily Summary</h2>
          <p className="text-sm text-gray-400 mt-1">Last 24 hours</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-xs text-gray-400">Live</span>
        </div>
      </div>

      <div className="card-body">
        <div className="grid grid-cols-2 gap-4">
          {statCards.map((card) => (
            <div
              key={card.id}
              className={`
                group relative overflow-hidden rounded-lg border ${card.borderColor} ${card.bgColor}
                transition-all duration-300 cursor-pointer ${card.hoverColor}
                transform hover:scale-105 hover:shadow-lg
              `}
            >
              {/* Gradient background on hover */}
              <div className={`
                absolute inset-0 opacity-0 group-hover:opacity-10
                bg-gradient-to-br ${card.color} transition-opacity duration-300
              `}></div>

              <div className="relative p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="text-2xl">{card.icon}</div>
                  {card.id === 'events' && totalEvents > 0 && (
                    <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-xs rounded-full">
                      +{totalEvents}
                    </span>
                  )}
                  {card.id === 'critical' && criticalAlerts > 0 && (
                    <span className="px-2 py-0.5 bg-red-500/20 text-red-400 text-xs rounded-full animate-pulse">
                      New
                    </span>
                  )}
                </div>

                <div className="text-xs text-gray-400 mb-1">{card.label}</div>
                <div className={`text-2xl font-bold ${card.valueColor || 'text-gray-100'}`}>
                  {card.value}
                </div>

                {/* Trend indicator (can be made dynamic) */}
                {card.id === 'events' && totalEvents > 0 && (
                  <div className="mt-2 flex items-center gap-1 text-xs text-green-400">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                    <span>Active</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Context Database Section */}
        <div className="mt-6 pt-6 border-t border-dark-700">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Context Database</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center justify-between p-3 bg-dark-800/50 rounded-lg border border-dark-700 hover:border-dark-600 transition-colors">
              <span className="text-sm text-gray-400">Stored Scenes:</span>
              <span className="text-lg font-semibold text-gray-100">{storedScenes}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-dark-800/50 rounded-lg border border-dark-700 hover:border-dark-600 transition-colors">
              <span className="text-sm text-gray-400">Patterns:</span>
              <span className="text-lg font-semibold text-gray-100">{patterns}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DailySummary;
