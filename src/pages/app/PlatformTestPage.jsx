import React from 'react'
import { supabase } from '@/lib/supabase'
import { Button } from '@/ui'

const API_BASE = import.meta.env.VITE_API_URL || import.meta.env.VITE_BACKEND_API_URL || '/api'

async function getAccessToken() {
  const {
    data: { session },
  } = await supabase.auth.getSession()
  return session?.access_token || null
}

async function readResponseTextSafe(res) {
  try {
    return await res.text()
  } catch {
    return ''
  }
}

const PlatformTestPage = () => {
  const [emailTo, setEmailTo] = React.useState('')
  const [emailSubject, setEmailSubject] = React.useState('Test email from Raptorflow')
  const [emailText, setEmailText] = React.useState('Hello from the platform test page.')
  const [emailStatus, setEmailStatus] = React.useState(null)

  const [selectedFile, setSelectedFile] = React.useState(null)
  const [uploadStatus, setUploadStatus] = React.useState(null)
  const [uploadedInfo, setUploadedInfo] = React.useState(null)

  const [busy, setBusy] = React.useState(false)

  const sendEmail = async () => {
    setEmailStatus(null)
    setBusy(true)

    try {
      const token = await getAccessToken()
      if (!token) {
        setEmailStatus({ ok: false, error: 'No Supabase access token found. Please sign in again.' })
        return
      }

      const res = await fetch(`${API_BASE}/email/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          to: emailTo,
          subject: emailSubject,
          text: emailText,
        }),
      })

      if (!res.ok) {
        const details = await readResponseTextSafe(res)
        setEmailStatus({ ok: false, error: `Email send failed (${res.status})`, details })
        return
      }

      const data = await res.json().catch(() => ({}))
      setEmailStatus({ ok: true, data })
    } catch (e) {
      setEmailStatus({ ok: false, error: e?.message || 'Email send failed' })
    } finally {
      setBusy(false)
    }
  }

  const uploadFile = async () => {
    setUploadStatus(null)
    setUploadedInfo(null)
    setBusy(true)

    try {
      if (!selectedFile) {
        setUploadStatus({ ok: false, error: 'Select a file first.' })
        return
      }

      const token = await getAccessToken()
      if (!token) {
        setUploadStatus({ ok: false, error: 'No Supabase access token found. Please sign in again.' })
        return
      }

      const contentType = selectedFile.type || 'application/octet-stream'

      const signedRes = await fetch(`${API_BASE}/storage/signed-upload`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          filename: selectedFile.name,
          contentType,
        }),
      })

      if (!signedRes.ok) {
        const details = await readResponseTextSafe(signedRes)
        setUploadStatus({ ok: false, error: `Signed URL request failed (${signedRes.status})`, details })
        return
      }

      const signed = await signedRes.json()

      const putRes = await fetch(signed.url, {
        method: 'PUT',
        headers: {
          ...(signed.headers || {}),
          'Content-Type': contentType,
        },
        body: selectedFile,
      })

      if (!putRes.ok) {
        const details = await readResponseTextSafe(putRes)
        setUploadStatus({ ok: false, error: `GCS upload failed (${putRes.status})`, details })
        return
      }

      setUploadStatus({ ok: true })
      setUploadedInfo({
        key: signed.key,
        bucket: signed.bucket,
        expiresAt: signed.expiresAt,
      })
    } catch (e) {
      setUploadStatus({ ok: false, error: e?.message || 'Upload failed' })
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="min-h-full bg-paper px-6 py-10">
      <div className="mx-auto w-full max-w-3xl">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-ink-900">Platform Test</h1>
          <p className="mt-2 text-sm text-ink-500">
            Use this page to validate Supabase auth, SendGrid email, and GCS signed uploads.
          </p>
        </div>

        <div className="space-y-8">
          <section className="rounded-card border border-border bg-card p-6">
            <h2 className="text-sm font-semibold text-ink-900">Subframe UI</h2>
            <p className="mt-2 text-sm text-ink-500">
              If you can see and click this button, the Subframe sync and aliasing are working.
            </p>
            <div className="mt-4">
              <Button onClick={() => console.log('Subframe Button clicked')}>Test Subframe Button</Button>
            </div>
          </section>

          <section className="rounded-card border border-border bg-card p-6">
            <h2 className="text-sm font-semibold text-ink-900">SendGrid Email</h2>

            <div className="mt-4 grid grid-cols-1 gap-4">
              <div>
                <label className="text-xs text-ink-600">To</label>
                <input
                  className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
                  placeholder="you@example.com"
                  value={emailTo}
                  onChange={(e) => setEmailTo(e.target.value)}
                  disabled={busy}
                />
              </div>

              <div>
                <label className="text-xs text-ink-600">Subject</label>
                <input
                  className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
                  value={emailSubject}
                  onChange={(e) => setEmailSubject(e.target.value)}
                  disabled={busy}
                />
              </div>

              <div>
                <label className="text-xs text-ink-600">Text</label>
                <textarea
                  className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
                  rows={4}
                  value={emailText}
                  onChange={(e) => setEmailText(e.target.value)}
                  disabled={busy}
                />
              </div>

              <div className="flex items-center gap-3">
                <button
                  className="rounded-lg bg-ink-900 px-4 py-2 text-xs font-semibold text-white disabled:opacity-50"
                  onClick={sendEmail}
                  disabled={busy || !emailTo}
                >
                  Send Email
                </button>

                {emailStatus?.ok === true && (
                  <span className="text-xs text-emerald-700">Sent</span>
                )}
                {emailStatus?.ok === false && (
                  <span className="text-xs text-red-700">{emailStatus.error}</span>
                )}
              </div>

              {emailStatus?.ok === false && emailStatus.details ? (
                <pre className="rounded-lg border border-border bg-white p-3 text-[11px] text-ink-600 overflow-auto">
                  {emailStatus.details}
                </pre>
              ) : null}
            </div>
          </section>

          <section className="rounded-card border border-border bg-card p-6">
            <h2 className="text-sm font-semibold text-ink-900">GCS Signed Upload</h2>

            <div className="mt-4 grid grid-cols-1 gap-4">
              <div>
                <label className="text-xs text-ink-600">File</label>
                <input
                  className="mt-1 w-full text-sm"
                  type="file"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  disabled={busy}
                />
              </div>

              <div className="flex items-center gap-3">
                <button
                  className="rounded-lg bg-ink-900 px-4 py-2 text-xs font-semibold text-white disabled:opacity-50"
                  onClick={uploadFile}
                  disabled={busy || !selectedFile}
                >
                  Upload via Signed URL
                </button>

                {uploadStatus?.ok === true && (
                  <span className="text-xs text-emerald-700">Uploaded</span>
                )}
                {uploadStatus?.ok === false && (
                  <span className="text-xs text-red-700">{uploadStatus.error}</span>
                )}
              </div>

              {uploadStatus?.ok === false && uploadStatus.details ? (
                <pre className="rounded-lg border border-border bg-white p-3 text-[11px] text-ink-600 overflow-auto">
                  {uploadStatus.details}
                </pre>
              ) : null}

              {uploadedInfo ? (
                <div className="rounded-lg border border-border bg-white p-3 text-xs text-ink-700">
                  <div className="grid grid-cols-1 gap-1">
                    <div>
                      <span className="text-ink-500">Bucket:</span> {uploadedInfo.bucket}
                    </div>
                    <div>
                      <span className="text-ink-500">Key:</span> {uploadedInfo.key}
                    </div>
                    <div>
                      <span className="text-ink-500">Expires:</span> {uploadedInfo.expiresAt}
                    </div>
                  </div>
                </div>
              ) : null}
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

export default PlatformTestPage
