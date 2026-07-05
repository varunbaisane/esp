export const getNotificationLink = (entityType: string | null, entityId: number | null, isAdmin: boolean = false): string | null => {
  if (!entityType || !entityId) {
    return null;
  }

  const type = entityType.toLowerCase();

  switch (type) {
    case 'ticket':
      return `/tickets/${entityId}`;
    case 'user':
      if (isAdmin) {
        return `/admin/users/${entityId}`;
      }
      return '/workspace';
    default:
      // Gracefully handle unknown entity types
      return '/notifications';
  }
};
