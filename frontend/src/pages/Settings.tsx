import { useState, useEffect } from 'react';
import {
  getGlobalEmailPreferences,
  createOrUpdateGlobalEmailPreferences,
  type GlobalEmailPreferencesCreate,
} from '../services/api';

interface EmailPreferences {
  email: string;
  notify_on_match: boolean;
  notify_on_start: boolean;
  include_in_digest: boolean;
  digest_time: string;
  digest_timezone: string;
}

export default function Settings() {
  const [preferences, setPreferences] = useState<EmailPreferences>({
    email: '',
    notify_on_match: true,
    notify_on_start: false,
    include_in_digest: true,
    digest_time: '09:00',
    digest_timezone: 'UTC',
  });
  const [, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Load preferences when email changes
  useEffect(() => {
    if (preferences.email && preferences.email.includes('@')) {
      loadPreferences(preferences.email);
    }
  }, [preferences.email]);

  const loadPreferences = async (email: string) => {
    try {
      setLoading(true);
      const data = await getGlobalEmailPreferences(email);
      if (data) {
        setPreferences({
          email: data.email_address,
          notify_on_match: data.notify_on_match,
          notify_on_start: data.notify_on_start,
          include_in_digest: data.include_in_digest,
          digest_time: data.digest_time,
          digest_timezone: data.digest_timezone,
        });
      }
    } catch (err) {
      console.error('Failed to load preferences:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!preferences.email || !preferences.email.includes('@')) {
      setMessage({ type: 'error', text: 'Please enter a valid email address' });
      return;
    }

    try {
      setSaving(true);
      const data: GlobalEmailPreferencesCreate = {
        email_address: preferences.email,
        notify_on_match: preferences.notify_on_match,
        notify_on_start: preferences.notify_on_start,
        include_in_digest: preferences.include_in_digest,
        digest_time: preferences.digest_time,
        digest_timezone: preferences.digest_timezone,
      };

      await createOrUpdateGlobalEmailPreferences(data);
      setMessage({ type: 'success', text: 'Settings saved successfully!' });
      setTimeout(() => setMessage(null), 5000);
    } catch (err) {
      console.error('Save error:', err);
      setMessage({ type: 'error', text: 'Failed to save settings' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Settings</h1>
        <p className="text-gray-600">Manage your global notification preferences</p>
      </div>

      {/* Success/Error Message */}
      {message && (
        <div
          className={`mb-6 px-4 py-3 rounded animate-fade-in ${
            message.type === 'success'
              ? 'bg-green-100 border border-green-400 text-green-700'
              : 'bg-red-100 border border-red-400 text-red-700'
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Settings Form */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-6">Email Notifications</h2>

        {/* Email Input */}
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            Email Address *
          </label>
          <input
            type="email"
            value={preferences.email}
            onChange={(e) => setPreferences({ ...preferences, email: e.target.value })}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="your@email.com"
            required
          />
          <p className="text-gray-500 text-xs mt-1">
            Enter your email to load or save preferences
          </p>
        </div>

        {/* Instant Notifications Toggle */}
        <div className="mb-6">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={preferences.notify_on_match}
              onChange={(e) =>
                setPreferences({ ...preferences, notify_on_match: e.target.checked })
              }
              className="form-checkbox h-5 w-5 text-blue-600"
            />
            <span className="ml-3">
              <span className="text-gray-700 font-medium">Instant Match Notifications</span>
              <p className="text-gray-500 text-sm">
                Get notified immediately when a new match is found
              </p>
            </span>
          </label>
        </div>

        {/* Search Start Notifications */}
        <div className="mb-6">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={preferences.notify_on_start}
              onChange={(e) =>
                setPreferences({ ...preferences, notify_on_start: e.target.checked })
              }
              className="form-checkbox h-5 w-5 text-blue-600"
            />
            <span className="ml-3">
              <span className="text-gray-700 font-medium">Search Start Notifications</span>
              <p className="text-gray-500 text-sm">
                Get notified when a new search begins
              </p>
            </span>
          </label>
        </div>

        {/* Daily Digest Toggle */}
        <div className="mb-6">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={preferences.include_in_digest}
              onChange={(e) =>
                setPreferences({ ...preferences, include_in_digest: e.target.checked })
              }
              className="form-checkbox h-5 w-5 text-blue-600"
            />
            <span className="ml-3">
              <span className="text-gray-700 font-medium">Daily Digest</span>
              <p className="text-gray-500 text-sm">Receive a daily summary of all matches</p>
            </span>
          </label>
        </div>

        {/* Digest Time */}
        {preferences.include_in_digest && (
          <div className="mb-6 ml-8 animate-fade-in">
            <label className="block text-gray-700 text-sm font-bold mb-2">Digest Time</label>
            <input
              type="time"
              value={preferences.digest_time}
              onChange={(e) =>
                setPreferences({ ...preferences, digest_time: e.target.value })
              }
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
            disabled={saving || !preferences.email}
            className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline ${
              saving || !preferences.email ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  );
}