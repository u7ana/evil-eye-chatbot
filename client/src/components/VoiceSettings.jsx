function SliderRow({ label, value, displayValue, min, max, step, onChange }) {
  return (
    <div className="mb-4 last:mb-0">
      <div className="flex items-center justify-between mb-1.5 text-sm">
        <span className="text-body">{label}</span>
        <span className="text-dim text-xs">{displayValue}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full"
        aria-label={label}
      />
    </div>
  )
}

export default function VoiceSettings({ speed, pitch, volume, onChange }) {
  return (
    <div className="rounded-2xl bg-card border border-line p-4">
      <h3 className="font-display text-sm font-semibold text-body mb-4">
        Voice settings
      </h3>
      <SliderRow
        label="Speed"
        value={speed}
        displayValue={`${speed.toFixed(1)}x`}
        min={0.5}
        max={2}
        step={0.1}
        onChange={(v) => onChange({ speed: v })}
      />
      <SliderRow
        label="Pitch"
        value={pitch}
        displayValue={pitch}
        min={-10}
        max={10}
        step={1}
        onChange={(v) => onChange({ pitch: v })}
      />
      <SliderRow
        label="Volume"
        value={volume}
        displayValue={`${Math.round(volume * 100)}%`}
        min={0}
        max={1}
        step={0.05}
        onChange={(v) => onChange({ volume: v })}
      />
    </div>
  )
}
