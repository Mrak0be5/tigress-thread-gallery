import pathlib, shutil

base = pathlib.Path(r'C:\Users\hebp\galleries\tigress-thread-gallery')
img_dir = base / 'images'
stream_dir = img_dir / 'stream'

count = 0
if stream_dir.exists() and stream_dir.is_dir():
    for src in stream_dir.glob('*.mp4'):
        dest = img_dir / src.name
        # Copy the compressed file over the original
        shutil.copy2(src, dest)
        count += 1
    
    # Remove the stream directory
    shutil.rmtree(stream_dir)

# Remove stream-index.js
idx = base / 'stream-index.js'
if idx.exists():
    idx.unlink()

print(f"Replaced {count} full videos with their compressed versions.")
