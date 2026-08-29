import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
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
    timeout: 60000,
  })
  return data
}

export async function speakArabic({ text }) {
  const { data } = await client.post(
    '/speak-arabic',
    { text },
    { responseType: 'blob', timeout: 30000 },
  )
  return data
}

export default client
