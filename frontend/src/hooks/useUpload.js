import { useState, useCallback } from "react"
import { uploadDocument } from "../services/api"

export function useUpload() {
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const upload = useCallback(async (file) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are allowed")
      return
    }
    if (file.size > 25 * 1024 * 1024) {
      setError("File exceeds 25 MB limit")
      return
    }
    setUploading(true)
    setProcessing(false)
    setProgress(0)
    setError(null)
    setResult(null)
    try {
      const data = await uploadDocument(file, (pct) => {
        setProgress(pct)
        if (pct === 100) setProcessing(true)
      })
      setResult(data)
      return data
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
      setProcessing(false)
    }
  }, [])

  const reset = useCallback(() => {
    setUploading(false)
    setProcessing(false)
    setProgress(0)
    setResult(null)
    setError(null)
  }, [])

  return { uploading, processing, progress, result, error, upload, reset }
}
