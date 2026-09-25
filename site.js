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

  async function playBlob(video, rawUrl) {
    const res = await fetch(rawUrl);
    if (!res.ok) throw new Error("video HTTP " + res.status);
    const blob = new Blob([await res.arrayBuffer()], { type: "video/mp4" });
    video.src = URL.createObjectURL(blob);
  }

  window.GALLERY = { onGitHub, url, manifestUrl, rewriteData, rawFromCdn, playBlob, RAW, CDN };
})();
