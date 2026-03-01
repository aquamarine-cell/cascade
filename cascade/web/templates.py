"""Self-contained HTML template for the file uploader UI.

No external dependencies (no CDN, no npm). Inline CSS/JS with
Deep Stream styling matching the CLI theme.
"""

UPLOAD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CASCADE - File Upload</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Courier New', monospace;
    background: #0a0e27;
    color: #e0e0e0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
  }
  h1 {
    color: #00f2ff;
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }
  .subtitle {
    color: #7000ff;
    margin-bottom: 2rem;
    font-size: 0.9rem;
  }
  .drop-zone {
    width: 100%;
    max-width: 600px;
    min-height: 200px;
    border: 2px dashed #7000ff;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    transition: border-color 0.2s, background 0.2s;
    cursor: pointer;
  }
  .drop-zone.drag-over {
    border-color: #00f2ff;
    background: rgba(0, 242, 255, 0.05);
  }
  .drop-zone p { color: #888; margin-top: 0.5rem; }
  .drop-zone .icon { font-size: 3rem; color: #7000ff; }
  input[type="file"] { display: none; }
  .file-list {
    width: 100%;
    max-width: 600px;
    margin-top: 1.5rem;
  }
  .file-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 1rem;
    background: rgba(112, 0, 255, 0.1);
    border: 1px solid #7000ff;
    border-radius: 6px;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
  }
  .file-item .name { color: #00f2ff; }
  .file-item .status { font-size: 0.8rem; }
  .file-item .status.ok { color: #00ff88; }
  .file-item .status.err { color: #ff0055; }
  .file-item .status.pending { color: #888; }
  .context-info {
    width: 100%;
    max-width: 600px;
    margin-top: 2rem;
    padding: 1rem;
    border: 1px solid #333;
    border-radius: 8px;
    font-size: 0.8rem;
    color: #888;
  }
  .context-info h3 { color: #00f2ff; margin-bottom: 0.5rem; }
</style>
</head>
<body>
  <h1>CASCADE</h1>
  <p class="subtitle">Drag and drop files to add to conversation context</p>

  <div class="drop-zone" id="dropZone">
    <div class="icon">+</div>
    <p>Drop files here or click to browse</p>
  </div>
  <input type="file" id="fileInput" multiple>

  <div class="file-list" id="fileList"></div>
  <div class="context-info" id="contextInfo">
    <h3>Context</h3>
    <p>Loading...</p>
  </div>

<script>
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');

dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  handleFiles(e.dataTransfer.files);
});
fileInput.addEventListener('change', () => handleFiles(fileInput.files));

function handleFiles(files) {
  for (const file of files) {
    uploadFile(file);
  }
}

function addFileItem(name, status, cls) {
  const div = document.createElement('div');
  div.className = 'file-item';
  div.innerHTML = `<span class="name">${name}</span><span class="status ${cls}">${status}</span>`;
  fileList.prepend(div);
  return div;
}

async function uploadFile(file) {
  const item = addFileItem(file.name, 'uploading...', 'pending');
  const formData = new FormData();
  formData.append('file', file);
  try {
    const resp = await fetch('/upload', { method: 'POST', body: formData });
    const data = await resp.json();
    if (data.ok) {
      item.querySelector('.status').textContent = 'added';
      item.querySelector('.status').className = 'status ok';
    } else {
      item.querySelector('.status').textContent = data.error || 'error';
      item.querySelector('.status').className = 'status err';
    }
  } catch (err) {
    item.querySelector('.status').textContent = 'failed';
    item.querySelector('.status').className = 'status err';
  }
  refreshContext();
}

async function refreshContext() {
  try {
    const resp = await fetch('/context');
    const data = await resp.json();
    const info = document.getElementById('contextInfo');
    info.innerHTML = `<h3>Context (${data.source_count} sources, ~${data.token_estimate} tokens)</h3>`;
    for (const s of data.sources) {
      const p = document.createElement('p');
      p.textContent = `[${s.type}] ${s.label} (${s.size} chars)`;
      info.appendChild(p);
    }
  } catch (err) {
    // ignore
  }
}

refreshContext();
</script>
</body>
</html>
"""
