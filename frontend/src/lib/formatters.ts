import { format, parseISO, isValid } from 'date-fns';

export function formatDate(date: string | Date | null | undefined, formatStr = 'MMM dd, yyyy'): string {
  if (!date) return '-';
  
  const parsedDate = typeof date === 'string' ? parseISO(date) : date;
  if (!isValid(parsedDate)) return '-';
  
  return format(parsedDate, formatStr);
}

export function formatDateTime(date: string | Date | null | undefined): string {
  return formatDate(date, 'MMM dd, yyyy HH:mm');
}

export function formatNumber(num: number | null | undefined, decimals = 0): string {
  if (num === null || num === undefined) return '-';
  return num.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

export function formatCurrency(amount: number | null | undefined): string {
  if (amount === null || amount === undefined) return '-';
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
  }).format(amount);
}

export function formatCoordinates(lat: number, lng: number): string {
  return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
}

export function truncateText(text: string, maxLength: number): string {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

export function capitalizeFirst(str: string): string {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export function snakeToTitleCase(str: string): string {
  if (!str) return str;
  return str
    .split('_')
    .map(word => capitalizeFirst(word.toLowerCase()))
    .join(' ');
}
