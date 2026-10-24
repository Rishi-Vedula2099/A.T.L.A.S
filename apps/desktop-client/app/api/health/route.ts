import { NextResponse } from "next/server";

// Lightweight health-check endpoint used by the Docker HEALTHCHECK and Traefik.
export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json({ status: "ok" });
}
