const BASE_URL = "http://localhost:8000"

const UPLOAD_TIMEOUT_MS = 5 * 60 * 1000

export async function uploadDocument(file, onProgress) {
  const form = new FormData()
  form.append("file", file)

  const xhr = new XMLHttpRequest()
  xhr.open("POST", `${BASE_URL}/upload`)
  xhr.timeout = UPLOAD_TIMEOUT_MS

  const result = await new Promise((resolve, reject) => {
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    }
    xhr.upload.onload = () => {
      if (onProgress) onProgress(100)
    }
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText))
      } else {
        try {
          reject(new Error(JSON.parse(xhr.responseText).detail || "Upload failed"))
        } catch {
          reject(new Error("Upload failed"))
        }
      }
    }
    xhr.ontimeout = () => reject(new Error("Upload timed out after 5 minutes"))
    xhr.onerror = () => reject(new Error("Network error"))
    xhr.send(form)
  })
  return result
}

export async function askQuestion(question) {
  const res = await fetch(`${BASE_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || "Query failed")
  }
  return res.json()
}

export async function healthCheck() {
  const res = await fetch(`${BASE_URL}/health`)
  return res.json()
}
