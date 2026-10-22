import { NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import type { NextRequest } from "next/server";

export async function middleware(request: NextRequest) {
  const token = await getToken({ req: request });
  const { pathname } = request.nextUrl;

  if (pathname.startsWith("/officer") && pathname !== "/officer/login") {
    if (!token) {
      return NextResponse.redirect(new URL("/officer/login", request.url));
    }
  }

  if (pathname.startsWith("/admin") && pathname !== "/admin/login") {
    if (!token || token.role !== "admin") {
      return NextResponse.redirect(new URL("/admin/login", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/officer/:path*", "/admin/:path*"],
};
