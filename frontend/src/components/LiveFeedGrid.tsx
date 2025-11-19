/**
 * Live camera feed grid component
 */
import React from 'react';
import { Camera } from '../types';

interface LiveFeedGridProps {
  cameras: Camera[];
  liveFeedData: Map<number, { frame: string; timestamp: string }>;
  onCameraStart: (cameraId: number) => void;
  onCameraStop: (cameraId: number) => void;
}

const LiveFeedGrid: React.FC<LiveFeedGridProps> = ({
  cameras,
  liveFeedData,
  onCameraStart,
  onCameraStop
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {cameras.map((camera) => {
        const feedData = liveFeedData.get(camera.id);

        return (
          <div key={camera.id} className="card">
            <div className="card-header flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-gray-100">{camera.name}</h3>
                <p className="text-sm text-gray-400">{camera.location}</p>
              </div>
              <div className="flex items-center gap-2">
                {camera.is_active ? (
                  <>
                    <span className="flex items-center gap-1 text-xs text-green-400">
                      <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                      LIVE
                    </span>
                    <button
                      onClick={() => onCameraStop(camera.id)}
                      className="text-xs px-2 py-1 bg-red-600 hover:bg-red-700 text-white rounded"
                    >
                      Stop
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => onCameraStart(camera.id)}
                    className="text-xs px-2 py-1 bg-green-600 hover:bg-green-700 text-white rounded"
                  >
                    Start
                  </button>
                )}
              </div>
            </div>
            <div className="card-body p-0">
              <div className="relative aspect-video bg-dark-900">
                {feedData?.frame ? (
                  <>
                    <img
                      src={`data:image/jpeg;base64,${feedData.frame}`}
                      alt={`Feed from ${camera.name}`}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        console.error(`Failed to load image for camera ${camera.id}`);
                        console.log('Feed data:', feedData);
                      }}
                    />
                    <div className="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                      ● LIVE
                    </div>
                  </>
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-500">
                    {camera.is_active ? (
                      <div className="text-center">
                        <div className="animate-pulse mb-2">
                          <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <p className="mb-1">Waiting for video feed...</p>
                        <p className="text-xs text-gray-600">Camera is active, frames should appear shortly</p>
                      </div>
                    ) : (
                      <div className="text-center">
                        <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                        <p>Camera offline</p>
                        <p className="text-xs text-gray-600 mt-1">Click "Start" to begin streaming</p>
                      </div>
                    )}
                  </div>
                )}
                {feedData?.timestamp && (
                  <div className="absolute bottom-2 left-2 bg-dark-900/80 px-2 py-1 rounded text-xs text-gray-300">
                    {new Date(feedData.timestamp).toLocaleTimeString()}
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default LiveFeedGrid;
