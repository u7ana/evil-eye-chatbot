import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// The backend's free-tier host spins down when idle and can take 50+
// seconds to wake back up on the next request (Render's own warning) - the
// timeout has to comfortably clear that, not just normal response time.
const COLD_START_TIMEOUT = 90000

const client = axios.create({
  baseURL: BASE_URL,
  timeout: COLD_START_TIMEOUT,
})

export async function sendChatMessage({ message, history }) {
  const { data } = await client.post('/chat', { message, history })
  return data
}

export async function transcribeAudio({ blob, language }) {
  const form = new FormData()
  form.append('audio', blob, 'speech.webm')
  if (language) form.append('language', language)

  const { data } = await client.post('/transcribe', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function speakArabic({ text }) {
  const { data } = await client.post(
    '/speak-arabic',
    { text },
    { responseType: 'blob' },
  )
  return data
}

export default client
