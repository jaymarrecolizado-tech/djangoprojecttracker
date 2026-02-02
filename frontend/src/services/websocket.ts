import type { WebSocketMessage, Notification, ImportProgress } from '@/types/api';

type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';
type MessageHandler = (message: WebSocketMessage) => void;
type StatusHandler = (status: WebSocketStatus) => void;

interface WebSocketCallbacks {
  onMessage?: MessageHandler;
  onStatusChange?: StatusHandler;
  onNotification?: (notification: Notification) => void;
  onImportProgress?: (progress: ImportProgress) => void;
  onError?: (error: Event) => void;
}

/**
 * WebSocket Service
 *
 * Manages WebSocket connections for real-time updates.
 * Handles notifications, import progress updates, and project updates.
 *
 * Connection URL: ws://localhost:8000/ws/notifications/
 */
class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000;
  private reconnectTimeoutId: number | null = null;
  private callbacks: WebSocketCallbacks = {};
  private status: WebSocketStatus = 'disconnected';
  private messageQueue: string[] = [];

  constructor(url?: string) {
    // @ts-ignore - Vite env types
    this.url = url || (import.meta.env?.VITE_WS_URL as string) || 'ws://localhost:8000/ws/';
    // Append notifications endpoint
    if (!this.url.endsWith('/')) {
      this.url += '/';
    }
    this.url += 'notifications/';
  }

  /**
   * Get current connection status
   */
  getStatus(): WebSocketStatus {
    return this.status;
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Connect to WebSocket server
   */
  connect(callbacks?: WebSocketCallbacks): void {
    if (callbacks) {
      this.callbacks = { ...this.callbacks, ...callbacks };
    }

    if (this.isConnected()) {
      console.log('WebSocket already connected');
      return;
    }

    // Check if WebSocket is enabled
    // @ts-ignore - Vite env types
    if (import.meta.env?.VITE_ENABLE_WEBSOCKET === 'false') {
      console.log('WebSocket is disabled');
      return;
    }

    this.updateStatus('connecting');

    try {
      this.ws = new WebSocket(this.url);
      this.setupEventHandlers();
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.updateStatus('error');
      this.attemptReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.clearReconnectTimeout();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnected');
      this.ws = null;
    }

    this.reconnectAttempts = 0;
    this.messageQueue = [];
    this.updateStatus('disconnected');
  }

  /**
   * Send message to server
   */
  send(message: unknown): boolean {
    const messageStr = typeof message === 'string' ? message : JSON.stringify(message);

    if (this.isConnected()) {
      this.ws!.send(messageStr);
      return true;
    } else {
      // Queue message for when connection is restored
      this.messageQueue.push(messageStr);
      console.warn('WebSocket not connected, message queued');
      return false;
    }
  }

  /**
   * Subscribe to specific notification types
   */
  subscribe(channel: string): void {
    this.send({
      type: 'subscribe',
      channel,
    });
  }

  /**
   * Unsubscribe from notification types
   */
  unsubscribe(channel: string): void {
    this.send({
      type: 'unsubscribe',
      channel,
    });
  }

  /**
   * Send ping to keep connection alive
   */
  ping(): void {
    this.send({ type: 'ping' });
  }

  /**
   * Update callbacks
   */
  setCallbacks(callbacks: WebSocketCallbacks): void {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }

  /**
   * Setup WebSocket event handlers
   */
  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.updateStatus('connected');
      this.flushMessageQueue();
    };

    this.ws.onmessage = (event) => {
      this.handleMessage(event.data);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.updateStatus('error');
      if (this.callbacks.onError) {
        this.callbacks.onError(error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      this.updateStatus('disconnected');

      // Attempt reconnect if not intentionally closed
      if (event.code !== 1000 && event.code !== 1001) {
        this.attemptReconnect();
      }
    };
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(data: string): void {
    try {
      const message: WebSocketMessage = JSON.parse(data);

      // Call generic message handler
      if (this.callbacks.onMessage) {
        this.callbacks.onMessage(message);
      }

      // Route to specific handlers based on message type
      const messageType = message.type as string;
      switch (messageType) {
        case 'notification':
          if (this.callbacks.onNotification && message.data) {
            this.callbacks.onNotification(message.data as Notification);
          }
          break;

        case 'import_progress':
          if (this.callbacks.onImportProgress && message.data) {
            this.callbacks.onImportProgress(message.data as ImportProgress);
          }
          break;

        case 'project_update':
          // Handle project update
          console.log('Project update received:', message.data);
          break;

        case 'ping':
          // Respond with pong
          this.send({ type: 'pong' });
          break;

        case 'pong':
          // Keepalive response received
          break;

        default:
          console.log('Unknown message type:', message.type);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  /**
   * Update connection status and notify listeners
   */
  private updateStatus(status: WebSocketStatus): void {
    this.status = status;
    if (this.callbacks.onStatusChange) {
      this.callbacks.onStatusChange(status);
    }
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);

    this.reconnectTimeoutId = window.setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Clear reconnect timeout
   */
  private clearReconnectTimeout(): void {
    if (this.reconnectTimeoutId !== null) {
      window.clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }
  }

  /**
   * Send queued messages
   */
  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) {
        this.ws?.send(message);
      }
    }
  }
}

// Singleton instance
let websocketInstance: WebSocketService | null = null;

/**
 * Get WebSocket service instance (singleton)
 */
export function getWebSocketService(url?: string): WebSocketService {
  if (!websocketInstance) {
    websocketInstance = new WebSocketService(url);
  }
  return websocketInstance;
}

/**
 * Reset WebSocket service instance
 */
export function resetWebSocketService(): void {
  if (websocketInstance) {
    websocketInstance.disconnect();
    websocketInstance = null;
  }
}

// Export class for custom instances
export { WebSocketService };
export type { WebSocketCallbacks, WebSocketStatus };
export default getWebSocketService;
