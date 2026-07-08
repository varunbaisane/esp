class NotificationSoundService {
  private audio: HTMLAudioElement | null = null;
  private isPlaying = false;

  constructor() {
    if (typeof window !== 'undefined') {
      this.audio = new Audio('/sounds/notification.mp3');
      this.audio.volume = 0.5; // professional, soft volume
    }
  }

  public play() {
    if (!this.audio || this.isPlaying) return;

    this.isPlaying = true;
    this.audio.play().catch((err) => {
      // Auto-play might be blocked by browser. This is fine.
      console.warn('Failed to play notification sound', err);
    }).finally(() => {
      this.isPlaying = false;
    });
  }
}

export const notificationSoundService = new NotificationSoundService();
