import { NextRequest, NextResponse } from 'next/server';

// Known scraper/bot user-agent patterns to block
const BLOCKED_UA_PATTERNS = [
  /python-requests/i,
  /scrapy/i,
  /wget/i,
  /curl/i,
  /httpx/i,
  /aiohttp/i,
  /go-http-client/i,
  /java\/\d/i,
  /libwww-perl/i,
  /lwp-/i,
  /axios/i,
  /node-fetch/i,
  /okhttp/i,
  /php\//i,
  /mechanize/i,
  /selenium/i,
  /playwright/i,
  /puppeteer/i,
  /headlesschrome/i,
  /phantomjs/i,
  /crawler/i,
  /spider/i,
  /scraper/i,
  /bot(?!.*google|.*bing|.*baidu|.*yandex)/i, // block bots except major search engines
];

export function middleware(request: NextRequest) {
  const ua = request.headers.get('user-agent') || '';

  // Block scrapers by user-agent
  const isBlocked = BLOCKED_UA_PATTERNS.some((pattern) => pattern.test(ua));
  if (isBlocked) {
    return new NextResponse('Access denied', { status: 403 });
  }

  // Image hotlinking protection: block /models/ and /videos/ requests from external sites
  const { pathname } = request.nextUrl;
  if (pathname.startsWith('/models/') || pathname.startsWith('/videos/')) {
    const referer = request.headers.get('referer') || '';
    const host = request.headers.get('host') || '';
    // Allow: no referer (direct access), same host, or localhost
    const isAllowed =
      !referer ||
      referer.includes(host) ||
      referer.includes('localhost') ||
      referer.includes('vercel.app');
    if (!isAllowed) {
      return new NextResponse('Hotlinking not allowed', { status: 403 });
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
