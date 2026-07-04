export const getNotificationLink = (entityType: string | null, entityId: number | null): string | null => {
  if (!entityType || !entityId) {
    return null;
  }

  const type = entityType.toLowerCase();

  switch (type) {
    case 'ticket':
      return `/tickets/${entityId}`;
    case 'user':
      return `/admin/users/${entityId}`;
    default:
      // Gracefully handle unknown entity types
      return '/notifications';
  }
};
