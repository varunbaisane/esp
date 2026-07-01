const TIME_OPTIONS: Intl.DateTimeFormatOptions = {
  hour: "2-digit",
  minute: "2-digit",
  hour12: true,
};

const DATE_OPTIONS: Intl.DateTimeFormatOptions = {
  day: "2-digit",
  month: "short",
  year: "numeric",
};

export function formatRelativeDateTime(dateString: string | Date): string {
  const date = new Date(dateString);
  const now = new Date();

  const dateStr = date.toDateString();
  const todayStr = now.toDateString();

  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayStr = yesterday.toDateString();

  const timeStr = date.toLocaleTimeString(undefined, TIME_OPTIONS);

  if (dateStr === todayStr) {
    return `Today, ${timeStr}`;
  } else if (dateStr === yesterdayStr) {
    return `Yesterday, ${timeStr}`;
  } else {
    const formattedDate = date.toLocaleDateString(undefined, DATE_OPTIONS);
    return `${formattedDate}, ${timeStr}`;
  }
}
