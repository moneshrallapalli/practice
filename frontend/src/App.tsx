/**
 * Main Application Component
 */
import React, { useState, useEffect } from 'react';
import { Camera, Alert, SummaryStats } from './types';
import { cameraApi, alertApi, statsApi } from './services/api';
import wsService from './services/websocket';
import LiveFeedGrid from './components/LiveFeedGrid';
import AlertPanel from './components/AlertPanel';
import SceneNarration from './components/SceneNarration';
import SummaryStatsComponent from './components/SummaryStats';
import SystemCommand from './components/SystemCommand';

interface NarrationEntry {
  id: string;
  timestamp: string;
  cameraId: number;
  description: string;
  significance: number;
  detections: number;
  context?: string;
}

function App() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<SummaryStats | null>(null);
  const [liveFeedData, setLiveFeedData] = useState<Map<number, { frame: string; timestamp: string }>>(new Map());
  const [narrations, setNarrations] = useState<NarrationEntry[]>([]);
  const [activeTab, setActiveTab] = useState('dashboard');

  // Load initial data
  useEffect(() => {
    loadCameras();
    loadAlerts();
    loadStats();

    // Refresh stats every 30 seconds
    const statsInterval = setInterval(loadStats, 30000);

    return () => clearInterval(statsInterval);
  }, []);

  // Setup WebSocket connections
  useEffect(() => {
    // Connect to live feed
    wsService.connectLiveFeed((update) => {
      setLiveFeedData((prev) => {
        const newMap = new Map(prev);
        newMap.set(update.camera_id, {
          frame: update.frame,
          timestamp: update.timestamp
        });
        return newMap;
      });
    });

    // Connect to alerts
    wsService.connectAlerts((alert) => {
      setAlerts((prev) => [alert, ...prev].slice(0, 50)); // Keep last 50 alerts

      // Play alert sound for critical alerts
      if (alert.severity === 'CRITICAL') {
        playAlertSound();
      }
    });

    // Connect to analysis
    wsService.connectAnalysis((update) => {
      const narration: NarrationEntry = {
        id: `${update.analysis.camera_id}-${Date.now()}`,
        timestamp: update.timestamp,
        cameraId: update.analysis.camera_id,
        description: update.analysis.scene_description,
        significance: update.analysis.significance,
        detections: update.analysis.detections,
        context: update.analysis.context
      };

      setNarrations((prev) => [...prev, narration].slice(-100)); // Keep last 100 narrations
    });

    // Connect to system
    wsService.connectSystem((message) => {
      console.log('System message:', message);
    });

    return () => {
      wsService.disconnectAll();
    };
  }, []);

  const loadCameras = async () => {
    try {
      const data = await cameraApi.getAll();
      setCameras(data);
    } catch (error) {
      console.error('Error loading cameras:', error);
    }
  };

  const loadAlerts = async () => {
    try {
      const data = await alertApi.getAll({ limit: 50 });
      setAlerts(data);
    } catch (error) {
      console.error('Error loading alerts:', error);
    }
  };

  const loadStats = async () => {
    try {
      const data = await statsApi.getSummary(24);
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleCameraStart = async (cameraId: number) => {
    try {
      await cameraApi.start(cameraId);
      await loadCameras();
    } catch (error) {
      console.error('Error starting camera:', error);
    }
  };

  const handleCameraStop = async (cameraId: number) => {
    try {
      await cameraApi.stop(cameraId);
      setLiveFeedData((prev) => {
        const newMap = new Map(prev);
        newMap.delete(cameraId);
        return newMap;
      });
      await loadCameras();
    } catch (error) {
      console.error('Error stopping camera:', error);
    }
  };

  const handleAcknowledgeAlert = async (alertId: number) => {
    try {
      await alertApi.acknowledge(alertId);
      setAlerts((prev) =>
        prev.map((alert) =>
          alert.id === alertId ? { ...alert, is_read: true } : alert
        )
      );
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const handleSystemCommand = (command: string) => {
    wsService.send('/ws/system', { command, params: {} });
  };

  const playAlertSound = () => {
    // Simple beep sound (in production, use a proper alert sound)
    const context = new (window.AudioContext || (window as any).webkitAudioContext)();
    const oscillator = context.createOscillator();
    const gainNode = context.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(context.destination);

    oscillator.frequency.value = 800;
    oscillator.type = 'sine';

    gainNode.gain.setValueAtTime(0.3, context.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, context.currentTime + 0.5);

    oscillator.start(context.currentTime);
    oscillator.stop(context.currentTime + 0.5);
  };

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'live', label: 'Live Feeds', icon: '📹' },
    { id: 'alerts', label: 'Alerts', icon: '🚨' },
    { id: 'summary', label: 'Summary', icon: '📈' }
  ];

  return (
    <div className="min-h-screen bg-dark-950">
      {/* Header */}
      <header className="bg-dark-900 border-b border-dark-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="text-3xl">🛡️</div>
              <div>
                <h1 className="text-2xl font-bold text-gray-100">SENTINTINEL</h1>
                <p className="text-sm text-gray-400">AI-Powered Surveillance System</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-sm text-gray-400">
                {stats && (
                  <span className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${stats.active_cameras > 0 ? 'bg-green-400 animate-pulse' : 'bg-gray-600'}`}></span>
                    {stats.active_cameras} Camera{stats.active_cameras !== 1 ? 's' : ''} Active
                  </span>
                )}
              </div>
              <button className="p-2 hover:bg-dark-800 rounded-lg transition-colors">
                <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </button>
              <button className="p-2 hover:bg-dark-800 rounded-lg transition-colors">
                <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex gap-2 mt-4 border-b border-dark-800">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-primary-400 border-b-2 border-primary-400'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'dashboard' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Live Feeds */}
            <div className="lg:col-span-2 space-y-6">
              <LiveFeedGrid
                cameras={cameras}
                liveFeedData={liveFeedData}
                onCameraStart={handleCameraStart}
                onCameraStop={handleCameraStop}
              />
              <SceneNarration narrations={narrations} />
            </div>

            {/* Right Column - Alerts & Stats */}
            <div className="space-y-6">
              <AlertPanel alerts={alerts} onAcknowledge={handleAcknowledgeAlert} />
              <SummaryStatsComponent stats={stats} />
              <SystemCommand onCommand={handleSystemCommand} />
            </div>
          </div>
        )}

        {activeTab === 'live' && (
          <LiveFeedGrid
            cameras={cameras}
            liveFeedData={liveFeedData}
            onCameraStart={handleCameraStart}
            onCameraStop={handleCameraStop}
          />
        )}

        {activeTab === 'alerts' && (
          <div className="max-w-3xl mx-auto">
            <AlertPanel alerts={alerts} onAcknowledge={handleAcknowledgeAlert} />
          </div>
        )}

        {activeTab === 'summary' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SummaryStatsComponent stats={stats} />
            <SceneNarration narrations={narrations} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
