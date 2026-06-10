const corsHeaders = (origin, allowedOrigin) => {
  const allow =
    allowedOrigin === "*" || origin === allowedOrigin ? origin || allowedOrigin : allowedOrigin;
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
};

export default {
  async fetch(request, env) {
    const allowedOrigin = env.ALLOWED_ORIGIN || "*";
    const origin = request.headers.get("Origin") || "";

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders(origin, allowedOrigin) });
    }

    if (request.method !== "POST") {
      return new Response("Method not allowed", {
        status: 405,
        headers: corsHeaders(origin, allowedOrigin),
      });
    }

    if (!env.GITHUB_TOKEN) {
      return new Response("Worker not configured", {
        status: 500,
        headers: corsHeaders(origin, allowedOrigin),
      });
    }

    const owner = env.GITHUB_OWNER;
    const repo = env.GITHUB_REPO;
    const workflowFile = env.WORKFLOW_FILE || "refresh-promotions.yml";
    const url = `https://api.github.com/repos/${owner}/${repo}/actions/workflows/${workflowFile}/dispatches`;

    const githubRes = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.GITHUB_TOKEN}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ref: "main" }),
    });

    const headers = {
      ...corsHeaders(origin, allowedOrigin),
      "Content-Type": "application/json",
    };

    if (githubRes.status === 204) {
      return new Response(JSON.stringify({ ok: true }), { status: 200, headers });
    }

    const detail = await githubRes.text();
    return new Response(
      JSON.stringify({ ok: false, status: githubRes.status, detail: detail.slice(0, 500) }),
      { status: githubRes.status, headers },
    );
  },
};
