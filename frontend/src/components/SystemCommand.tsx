/**
 * System command interface
 */
import React, { useState } from 'react';

interface SystemCommandProps {
  onCommand: (command: string) => void;
}

const SystemCommand: React.FC<SystemCommandProps> = ({ onCommand }) => {
  const [command, setCommand] = useState('');
  const [history, setHistory] = useState<string[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (command.trim()) {
      setHistory([...history, command]);
      onCommand(command);
      setCommand('');
    }
  };

  const quickCommands = [
    { label: 'Test Alert', command: 'test_alert' },
    { label: 'Get Stats', command: 'get_stats' },
    { label: 'Refresh All', command: 'refresh_all' }
  ];

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-lg font-semibold">System Commands</h2>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit} className="mb-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              placeholder="Enter command..."
              className="flex-1 px-3 py-2 bg-dark-900 border border-dark-700 rounded-md text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md transition-colors"
            >
              Send
            </button>
          </div>
        </form>

        <div className="flex gap-2 flex-wrap mb-3">
          {quickCommands.map((cmd) => (
            <button
              key={cmd.command}
              onClick={() => onCommand(cmd.command)}
              className="px-3 py-1 text-xs bg-dark-700 hover:bg-dark-600 text-gray-300 rounded transition-colors"
            >
              {cmd.label}
            </button>
          ))}
        </div>

        {history.length > 0 && (
          <div className="mt-4 pt-4 border-t border-dark-700">
            <h3 className="text-xs font-semibold text-gray-400 mb-2">Command History</h3>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {history.slice(-5).reverse().map((cmd, index) => (
                <div key={index} className="text-xs text-gray-500 font-mono">
                  {'>'} {cmd}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemCommand;
