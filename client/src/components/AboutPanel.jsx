import EyeLogo from './EyeLogo'

export default function AboutPanel() {
  return (
    <div className="rounded-2xl bg-card border border-line p-5">
      <h3 className="font-display text-sm font-semibold text-body mb-4 text-left" dir="rtl">
        عن EE
      </h3>
      <div className="flex items-center justify-center py-3">
        <EyeLogo size={68} />
      </div>
      <p dir="rtl" className="text-xs text-dim leading-relaxed text-center">
        EE رفيقك الغامض. اسأله أي حاجة، واسمع الرد بالصوت اللي يناسبك.
      </p>
      <p dir="rtl" className="text-[10px] text-moss text-center mt-3">
        أيها الداخلون اطرحوا عنكم كل أمل في الخروج
      </p>
    </div>
  )
}
