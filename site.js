/* Public gallery reads files from git. A new picture is a git push, not a full site rebuild.
   Pictures and text: raw.githubusercontent.com (correct image types).
   Video: jsDelivr (video/mp4, 20 MB cap). Larger files fall back to a blob from raw. */
(function () {
  const host = (location.hostname || "").toLowerCase();
  const onGitHub = host.endsWith("github.io") || host.endsWith("github.com");
  const RAW = "https://raw.githubusercontent.com/Mrak0be5/tigress-thread-gallery/master/";
  const CDN = "https://cdn.jsdelivr.net/gh/Mrak0be5/tigress-thread-gallery@master/";

  function url(path) {
    const p = String(path || "").trim();
    if (!p || /^(https?:|blob:|data:)/i.test(p)) return p;
    if (!onGitHub || /\.html(\?|#|$)/i.test(p)) return p;
    const rel = p.replace(/^\.\//, "").replace(/^\//, "");
    if (/\.mp4(\?|#|$)/i.test(rel)) return CDN + rel;
    return RAW + rel;
  }

  function manifestUrl() {
    if (!onGitHub) return "manifest.json";
    return RAW + "manifest-public.json?ts=" + Date.now();
  }

  function rewriteItem(it) {
    if (!it || typeof it !== "object") return it;
    ["file", "pose", "poster", "stream", "prompt_file"].forEach((key) => {
      if (typeof it[key] === "string") it[key] = url(it[key]);
    });
    if (Array.isArray(it.refs)) {
      it.refs.forEach((ref) => {
        if (ref && typeof ref.file === "string") ref.file = url(ref.file);
      });
    }
    return it;
  }

  function rewriteData(data) {
    (data.items || []).forEach(rewriteItem);
    return data;
  }

  function rawFromCdn(src) {
    const match = String(src || "").match(/cdn\.jsdelivr\.net\/gh\/Mrak0be5\/tigress-thread-gallery@[^/]+\/(.+?)(?:\?|#|$)/);
    return match ? RAW + match[1] : "";
  }

  function toRaw(src) {
    const fromCdn = rawFromCdn(src);
    if (fromCdn) return fromCdn;
    const p = String(src || "").trim();
    if (!p) return "";
    if (!onGitHub || /^(https?:|blob:|data:)/i.test(p)) return p;
    return RAW + p.replace(/^\.\//, "").replace(/^\//, "");
  }

  async function fetchPacked(url, onProgress) {
    const raw = toRaw(url);
    const res = await fetch(raw);
    if (!res.ok) throw new Error("video HTTP " + res.status);
    const total = Number(res.headers.get("content-length")) || 0;
    const reader = res.body && res.body.getReader ? res.body.getReader() : null;
    let buf;
    if (!reader) {
      buf = new Uint8Array(await res.arrayBuffer());
      if (onProgress) onProgress({ phase: "download", ratio: 1, got: buf.length, total: buf.length });
    } else {
      const chunks = [];
      let got = 0;
      while (true) {
        const step = await reader.read();
        if (step.done) break;
        chunks.push(step.value);
        got += step.value.byteLength;
        if (onProgress) onProgress({ phase: "download", ratio: total ? got / total : 0, got, total });
      }
      buf = new Uint8Array(got);
      let off = 0;
      for (const chunk of chunks) {
        buf.set(chunk, off);
        off += chunk.byteLength;
      }
    }
    if (buf.length >= 2 && buf[0] === 0x1f && buf[1] === 0x8b && typeof DecompressionStream === "function") {
      if (onProgress) onProgress({ phase: "unpack", ratio: 1, got: buf.length, total });
      const ds = new DecompressionStream("gzip");
      const unpacked = await new Response(new Blob([buf]).stream().pipeThrough(ds)).arrayBuffer();
      buf = new Uint8Array(unpacked);
    } else if (onProgress) {
      onProgress({ phase: "unpack", ratio: 1, got: buf.length, total });
    }
    return URL.createObjectURL(new Blob([buf], { type: "video/mp4" }));
  }

  window.GALLERY = { onGitHub, url, manifestUrl, rewriteData, rawFromCdn, toRaw, fetchPacked, RAW, CDN };
})();
