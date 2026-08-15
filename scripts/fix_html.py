import pathlib, re

def process_file(p):
    text = p.read_text('utf-8')
    
    # Remove <script src="stream-index.js"></script>
    text = text.replace('<script src="stream-index.js"></script>\n', '')
    text = text.replace('<script src="stream-index.js"></script>', '')
    
    # In watch.html: simplify playUrl
    old_playurl_watch = '''      function playUrl(id, item) {
        if (item && item.stream) return item.stream;
        if (window.STREAM_IDS && window.STREAM_IDS[id]) {
          return "images/stream/" + encodeURIComponent(id) + ".mp4";
        }
        if (item && item.file) return item.file;
        return "images/" + encodeURIComponent(id) + ".mp4";
      }'''
    new_playurl_watch = '''      function playUrl(id, item) {
        if (item && item.file) return item.file;
        return "images/" + encodeURIComponent(id) + ".mp4";
      }'''
    text = text.replace(old_playurl_watch, new_playurl_watch)
    
    # In index.html: simplify playUrl
    old_playurl_idx = '''      function playUrl(id) {
        if (window.STREAM_IDS && window.STREAM_IDS[id]) {
          return "images/stream/" + encodeURIComponent(id) + ".mp4";
        }
        return "images/" + encodeURIComponent(id) + ".mp4";
      }'''
    new_playurl_idx = '''      function playUrl(id) {
        return "images/" + encodeURIComponent(id) + ".mp4";
      }'''
    text = text.replace(old_playurl_idx, new_playurl_idx)
    
    # In watch.html: simplify preload script
    old_preload = '''      var q = new URLSearchParams(location.search).get("id");
      if (!q) return;
      var id = q.trim();
      var src = (window.STREAM_IDS && window.STREAM_IDS[id])
        ? ("images/stream/" + encodeURIComponent(id) + ".mp4")
        : ("images/" + encodeURIComponent(id) + ".mp4");
      window.__VIDEO_SRC = src;
      var v = document.createElement("link");
      v.rel = "preload";'''
      
    new_preload = '''      var q = new URLSearchParams(location.search).get("id");
      if (!q) return;
      var id = q.trim();
      var src = "images/" + encodeURIComponent(id) + ".mp4";
      window.__VIDEO_SRC = src;
      var v = document.createElement("link");
      v.rel = "preload";'''
    text = text.replace(old_preload, new_preload)
    
    p.write_text(text, 'utf-8')

base = pathlib.Path(r'C:\Users\hebp\galleries\tigress-thread-gallery')
process_file(base / 'watch.html')
process_file(base / 'index.html')

# In manifest.json, remove "stream" field from items
import json
mani = base / 'manifest.json'
if mani.exists():
    data = json.loads(mani.read_text('utf-8'))
    for it in data.get("items", []):
        it.pop("stream", None)
    mani.write_text(json.dumps(data, indent=2, ensure_ascii=False), 'utf-8')

pub_mani = base / 'manifest-public.json'
if pub_mani.exists():
    data = json.loads(pub_mani.read_text('utf-8'))
    for it in data.get("items", []):
        it.pop("stream", None)
    pub_mani.write_text(json.dumps(data, indent=2, ensure_ascii=False), 'utf-8')

