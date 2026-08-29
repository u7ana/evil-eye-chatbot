const ARABIC_RANGE = /[؀-ۿݐ-ݿ]/

export function isArabicText(text) {
  return ARABIC_RANGE.test(text)
}

/** Best system voice for a language prefix (only 'en' is used - Arabic
    speech goes through the backend's edge-tts instead of a system voice,
    see useSpeechSynthesis.js). Prefers higher-quality "Natural" voices
    when the OS provides them. */
export function bestVoiceFor(voices, prefix) {
  const list = voices.filter((v) => v.lang?.toLowerCase().startsWith(prefix))
  if (!list.length) return null
  return list.find((v) => /natural/i.test(v.name)) || list[0]
}
