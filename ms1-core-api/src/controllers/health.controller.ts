import { Request, Response } from 'express';

export function healthCheck(req: Request, res: Response): void {
  res.status(200).json({
    status: 'OK',
    service: 'ms1-core-api',
  });
}
