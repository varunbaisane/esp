import { useEffect, useState } from 'react';
import { notificationPreferenceService } from '../../services/notificationPreferenceService';
import type { NotificationPreference } from '../../types/notificationPreference';
import { PageLoader } from '../../components/common/PageLoader';

export const NotificationPreferencesPage = () => {
  const [preferences, setPreferences] = useState<NotificationPreference[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      setIsLoading(true);
      const data = await notificationPreferenceService.getPreferences();
      setPreferences(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load preferences.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = async (prefId: number, currentEnabled: boolean) => {
    // Optimistic UI update
    setPreferences(prev => 
      prev.map(p => p.id === prefId ? { ...p, enabled: !currentEnabled } : p)
    );

    try {
      await notificationPreferenceService.updatePreference(prefId, { enabled: !currentEnabled });
    } catch (err: any) {
      // Revert on failure
      setPreferences(prev => 
        prev.map(p => p.id === prefId ? { ...p, enabled: currentEnabled } : p)
      );
      setError(err.response?.data?.detail || 'Failed to update preference.');
    }
  };

  if (isLoading) {
    return <PageLoader />;
  }

  // Group by category (Tickets vs Roles) and then by type
  const groupedByCategory = preferences.reduce((acc, pref) => {
    const category = pref.notification_type.startsWith('TICKET') ? 'Tickets' : 'Roles';
    if (!acc[category]) {
      acc[category] = {};
    }
    if (!acc[category][pref.notification_type]) {
      acc[category][pref.notification_type] = [];
    }
    acc[category][pref.notification_type].push(pref);
    return acc;
  }, {} as Record<string, Record<string, NotificationPreference[]>>);

  const formatType = (type: string) => {
    return type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' ');
  };

  const formatChannel = (channel: string) => {
    if (channel === 'IN_APP') return 'In-App';
    return channel.charAt(0).toUpperCase() + channel.slice(1).toLowerCase();
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Notification Preferences</h1>
        <p className="mt-2 text-sm text-gray-600">
          Manage how you receive ongoing operational notifications.
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border-l-4 border-red-400 p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="space-y-6">
        {Object.entries(groupedByCategory).map(([category, types]) => (
          <details key={category} className="bg-white shadow sm:rounded-lg overflow-hidden group" open>
            <summary className="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200 cursor-pointer flex justify-between items-center hover:bg-gray-100 list-none [&::-webkit-details-marker]:hidden">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                {category}
              </h3>
              <svg className="h-5 w-5 text-gray-500 transform transition-transform group-open:rotate-180" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </summary>
            
            <div className="px-4 py-5 sm:p-6 divide-y divide-gray-200">
              {Object.entries(types).map(([type, prefs]) => (
                <div key={type} className="py-4 flex items-center justify-between first:pt-0 last:pb-0">
                  <div className="text-sm font-medium text-gray-900">
                    {formatType(type)}
                  </div>
                  <div className="flex space-x-6 items-center">
                    {(prefs as NotificationPreference[]).map(pref => (
                      <div key={pref.id} className="flex items-center space-x-3">
                        <span className="text-sm text-gray-600">
                          {formatChannel(pref.channel)}
                        </span>
                        <button
                          type="button"
                          className={`
                            relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500
                            ${pref.enabled ? 'bg-cyan-600' : 'bg-gray-200'}
                          `}
                          role="switch"
                          aria-checked={pref.enabled}
                          onClick={() => handleToggle(pref.id, pref.enabled)}
                        >
                          <span className="sr-only">Toggle {pref.channel}</span>
                          <span
                            aria-hidden="true"
                            className={`
                              pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200
                              ${pref.enabled ? 'translate-x-5' : 'translate-x-0'}
                            `}
                          />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </details>
        ))}
      </div>
    </div>
  );
};
