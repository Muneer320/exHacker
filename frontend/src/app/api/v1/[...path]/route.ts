/** Same-origin proxy; backend address and credentials never enter the bundle. */
import { NextRequest } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

class RequestTooLarge extends Error {}

async function readBody(request: NextRequest) {
  const reader = request.body?.getReader();
  if (!reader) return undefined;
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > 200000) {
        await reader.cancel();
        throw new RequestTooLarge();
      }
      chunks.push(value);
    }
  } finally {
    reader.releaseLock();
  }
  const body = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) {
    body.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return new TextDecoder().decode(body);
}

async function proxy(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const { path } = await params;
  if (
    path.some(
      (segment) => !/^[a-zA-Z0-9_.-]+$/.test(segment) || segment === "..",
    )
  )
    return new Response(null, { status: 400 });
  const base = process.env.BACKEND_URL || "http://127.0.0.1:8000";
  try {
    const body = ["GET", "HEAD"].includes(request.method)
      ? undefined
      : await readBody(request);
    const response = await fetch(
      `${base.replace(/\/$/, "")}/api/v1/${path.map(encodeURIComponent).join("/")}${request.nextUrl.search}`,
      {
        method: request.method,
        body,
        headers: {
          "Content-Type": "application/json",
          Authorization: request.headers.get("authorization") || "",
          "X-AI-Lease": request.headers.get("x-ai-lease") || "",
        },
        cache: "no-store",
        signal: AbortSignal.timeout(18000),
      },
    );
    const headers = new Headers({
      "Cache-Control": "private, no-store",
      "X-Content-Type-Options": "nosniff",
    });
    for (const key of ["Content-Type", "Content-Disposition", "ETag"]) {
      const value = response.headers.get(key);
      if (value) headers.set(key, value);
    }
    return new Response(response.body, { status: response.status, headers });
  } catch (error) {
    if (error instanceof RequestTooLarge)
      return Response.json(
        { success: false, error: { message: "Request is too large." } },
        { status: 413, headers: { "Cache-Control": "private, no-store" } },
      );
    return Response.json(
      {
        success: false,
        error: {
          message:
            "The project service is unavailable. Please retry in a moment.",
        },
      },
      { status: 503 },
    );
  }
}

export {
  proxy as GET,
  proxy as POST,
  proxy as PATCH,
  proxy as PUT,
  proxy as DELETE,
};
