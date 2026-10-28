export async function onRequest(context) {
  const url = new URL(context.request.url);
  const forwarded = context.request.headers.get("x-forwarded-proto");
  if (url.protocol === "http:" || forwarded === "http") {
    url.protocol = "https:";
    return Response.redirect(url.toString(), 301);
  }
  return context.next();
}
