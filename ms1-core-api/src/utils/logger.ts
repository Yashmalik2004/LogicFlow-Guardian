const isProduction = process.env.NODE_ENV === 'production';

type LogLevel = 'info' | 'warn' | 'error';

function log(level: LogLevel, message: string, meta?: unknown): void {
  const timestamp = new Date().toISOString();
  const prefix = `[${timestamp}] [${level.toUpperCase()}]`;

  if (meta !== undefined) {
    // eslint-disable-next-line no-console
    console[level](`${prefix} ${message}`, meta);
  } else {
    // eslint-disable-next-line no-console
    console[level](`${prefix} ${message}`);
  }
}

export const logger = {
  info: (message: string, meta?: unknown) => {
    if (!isProduction) {
      log('info', message, meta);
    }
  },
  warn: (message: string, meta?: unknown) => log('warn', message, meta),
  error: (message: string, meta?: unknown) => log('error', message, meta),
};
