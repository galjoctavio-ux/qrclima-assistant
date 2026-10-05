import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
export function GET() {
  const api = process.env.NEXT_PUBLIC_QRCLIMA_ASSISTANT_API_URL;
  const enabled = process.env.NEXT_PUBLIC_QRCLIMA_ASSISTANT_ENABLED === 'true' && !!api;
  return NextResponse.json({ enabled, ...(enabled ? { api } : {}), version: '0.4.0' }, {
    headers: { 'Cache-Control': 'no-store' },
  });
}
