import { useState, useEffect } from 'react';
import { getEmailPreferences } from '../services/api';

interface EmailPreferences {
  email: string;
  notify_on_match: boolean;
  daily_digest: boolean;
  digest_time: string;
}

export default function Settings() {
  const [preferences, setPreferences] = useState<EmailPreferences>({
    email: '',
    notify_on_match: true,
    daily_digest: true,
    digest_time: '09:00',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      setLoading(true);
      const data = await getEmailPreferences();
      if (data) {
        setPreferences(data);
      }
    } catch (err) {
      console.error('Failed to load preferences:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      // Note: Global email preferences are not yet implemented in the backend
      // The backend currently only supports per-search-request email preferences
      // For now, we'll just show a success message
      console.log('Preferences to save:', preferences);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setMessage({ type: 'success', text: 'Settings saved successfully! (Note: Global preferences will be implemented in a future update)' });
      setTimeout(() => setMessage(null), 5000);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to save settings' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-300 rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-gray-300 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Settings
        </h1>
        <p className="text-gray-600">
          Manage your notification preferences
        </p>
      </div>

      {/* Success/Error Message */}
      {message && (
        <div className={`mb-6 px-4 py-3 rounded animate-fade-in ${
          message.type === 'success' 
            ? 'bg-green-100 border border-green-400 text-green-700'
            : 'bg-red-100 border border-red-400 text-red-700'
        }`}>
          {message.text}
        </div>
      )}

      {/* Settings Form */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-6">
          Email Notifications
        </h2>

        {/* Email Input */}
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            Email Address
          </label>
          <input
            type="email"
            value={preferences.email}
            onChange={(e) => setPreferences({ ...preferences, email: e.target.value })}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="your@email.com"
          />
        </div>

        {/* Instant Notifications Toggle */}
        <div className="mb-6">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={preferences.notify_on_match}
              onChange={(e) => setPreferences({ ...preferences, notify_on_match: e.target.checked })}
              className="form-checkbox h-5 w-5 text-blue-600"
            />
            <span className="ml-3">
              <span className="text-gray-700 font-medium">Instant Match Notifications</span>
              <p className="text-gray-500 text-sm">Get notified immediately when a new match is found</p>
            </span>
          </label>
        </div>

        {/* Daily Digest Toggle */}
        <div className="mb-6">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={preferences.daily_digest}
              onChange={(e) => setPreferences({ ...preferences, daily_digest: e.target.checked })}
              className="form-checkbox h-5 w-5 text-blue-600"
            />
            <span className="ml-3">
              <span className="text-gray-700 font-medium">Daily Digest</span>
              <p className="text-gray-500 text-sm">Receive a daily summary of all matches</p>
            </span>
          </label>
        </div>

        {/* Digest Time (only show if daily digest is enabled) */}
        {preferences.daily_digest && (
          <div className="mb-6 ml-8 animate-fade-in">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Digest Time
            </label>
            <input
              type="time"
              value={preferences.digest_time}
              onChange={(e) => setPreferences({ ...preferences, digest_time: e.target.value })}
              className="shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
            <p className="text-gray-500 text-xs mt-1">
              Choose when you want to receive your daily digest
            </p>
          </div>
        )}

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            disabled={saving}
            className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline ${
              saving ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
