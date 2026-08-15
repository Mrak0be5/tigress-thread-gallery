import pathlib, re
p = pathlib.Path(r'C:\Users\hebp\galleries\tigress-thread-gallery\scripts\publish-add.py')
text = p.read_text('utf-8')

# Remove stream logic
text = re.sub(r'def ensure_item_stream.*?def strip_secrets_item', 'def strip_secrets_item', text, flags=re.DOTALL)

# Remove encode_stream args handling
text = re.sub(r'    if args\.encode_stream:.*?return 0\n\n', '', text, flags=re.DOTALL)
text = text.replace('ap.add_argument("--encode-stream", action="store_true", help="encode lightweight playback mp4s")\n', '')
text = text.replace('ap.add_argument("--force-stream", action="store_true", help="rebuild stream mp4s even if files exist")\n', '')

# Change video processing to compress directly
new_vid_process = '''    if src.suffix.lower() == ".mp4":
        out_name = f"{iid}.mp4"
        out_path = IMG / out_name
        out_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Compressing video {src.name} to {out_name}...")
        process_video_file(src, out_path)
        size = (0, 0)'''
old_vid_process = '''    if src.suffix.lower() == ".mp4":
        out_name = f"{iid}.mp4"
        out_path = IMG / out_name
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out_path)
        size = (0, 0)'''
text = text.replace(old_vid_process, new_vid_process)

# Remove ensure_item_stream calls
text = text.replace('        ensure_item_stream(item)\n', '')
text = text.replace('    if src.suffix.lower() == ".mp4":\n        write_stream_index(data)\n', '')

p.write_text(text, 'utf-8')
