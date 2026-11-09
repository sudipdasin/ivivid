#!/usr/bin/env python3
# ============================================================
# mpv-config.py v4 — iGPU Optimized
# Maximizes video quality on built-in graphics
# Save as: mpv-config.py | chmod +x mpv-config.py
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import re

MPV_DIR = os.path.expanduser("~/.config/mpv")
SHADER_DIR = os.path.join(MPV_DIR, "shaders")
CONF_FILE = os.path.join(MPV_DIR, "mpv.conf")
INPUT_FILE = os.path.join(MPV_DIR, "input.conf")

SHADERS = {
    "KrigBilateral.glsl": "https://raw.githubusercontent.com/boned101/MPV-Custom-Shaders/main/KrigBilateral.glsl",
    "adaptive-sharpen.glsl": "https://raw.githubusercontent.com/boned101/MPV-Custom-Shaders/main/adaptive-sharpen.glsl",
    "ravu-r3-rgb.glsl": "https://raw.githubusercontent.com/akirasuper/ravu/main/ravu-r3-rgb.glsl",
    "CfL_Prediction.glsl": "https://raw.githubusercontent.com/boned101/MPV-Custom-Shaders/main/CfL_Prediction.glsl",
    "hdeband.glsl": "https://raw.githubusercontent.com/akirasuper/hdeband/main/hdeband.glsl",
}

# --- iGPU detection ---
def detect_igpu():
    """Detect integrated GPU and return (name, tier) where tier: 0=weak, 1=mid, 2=strong"""
    try:
        r = subprocess.run(["lspci"], capture_output=True, text=True, timeout=5)
        gpu_line = ""
        for line in r.stdout.splitlines():
            if "VGA" in line or "Display" in line or "3D" in line:
                gpu_line = line
                break
        if "HD Graphics 620" in gpu_line or "620" in gpu_line:
            return ("Intel HD Graphics 620", 0)
        elif "UHD Graphics 630" in gpu_line or "630" in gpu_line:
            return ("Intel UHD Graphics 630", 0)
        elif "UHD Graphics 630" in gpu_line or "630" in gpu_line:
            return ("Intel UHD Graphics 630", 0)
        elif "Iris Xe" in gpu_line or "Iris Plus" in gpu_line:
            return ("Intel Iris Xe/Plus", 2)
        elif "UHD Graphics" in gpu_line:
            return ("Intel UHD Graphics", 1)
        elif "Vega" in gpu_line or "Radeon" in gpu_line:
            return ("AMD Radeon (iGPU)", 1)
        elif "HD Graphics" in gpu_line:
            m = re.search(r'(\d+)', gpu_line)
            num = int(m.group(1)) if m else 0
            if num >= 630:
                return (f"Intel HD {num}", 1)
            else:
                return (f"Intel HD {num}", 0)
        else:
            return ("Unknown iGPU", 1)
    except Exception:
        return ("Unknown iGPU", 1)

# --- Shader templates ---
VIVID_SHADER = '''// vivid_hdr.glsl — SDR to HDR-like look (iGPU optimized)
// Parameters set via uniform or hardcoded for simplicity
void main() {
    vec4 color = texture(samp, TexCoord0);

    // Black point crush
    color.rgb -= 0.02;

    // S-curve contrast
    color.rgb = 0.5 + (color.rgb - 0.5) * 1.25;

    // Gamma lift (brighter midtones)
    color.rgb = pow(max(color.rgb, 0.0), vec3(0.92));

    // Saturation boost
    float luma = dot(color.rgb, vec3(0.2126, 0.7152, 0.0722));
    color.rgb = mix(vec3(luma), color.rgb, 1.35);

    // Warm tint (cinematic)
    color.r *= 1.03; color.g *= 1.01; color.b *= 0.97;

    // Soft-clip highlights
    color.rgb = 1.0 - exp(-color.rgb * 1.08);

    // Clamp
    color.rgb = clamp(color.rgb, 0.0, 1.0);
    FragColor = color;
}
'''

SOFT_SHADER = '''// soft_look.glsl — Gentle enhancement (lightest shader)
void main() {
    vec4 color = texture(samp, TexCoord0);
    // Mild contrast
    color.rgb = 0.5 + (color.rgb - 0.5) * 1.08;
    // Slight saturation
    float luma = dot(color.rgb, vec3(0.2126, 0.7152, 0.0722));
    color.rgb = mix(vec3(luma), color.rgb, 1.12);
    // Gentle black crush
    color.rgb *= 1.02;
    color.rgb = clamp(color.rgb, 0.0, 1.0);
    FragColor = color;
}
'''

# --- Help text ---
HELP = {
    "preset": "Quality presets auto-configure all options:\n\n• LIGHT — minimum GPU load, 60fps guaranteed\n  (no heavy shaders, basic scaling)\n\n• BALANCED — best quality/perf ratio\n  (vivid HDR + adaptive sharpen + lanczos)\n\n• MAX — maximum visual quality\n  (all shaders, KrigBilateral, full pipeline)\n  May drop below 60fps on weak iGPU",
    "fullscreen": "Opens video in fullscreen immediately.\nToggle during playback: press F\nWorks with both mpv and SMPlayer",
    "keepaspect": "Locks video to native aspect ratio.\n16:9 on 16:9 = perfect fill\nPrevents stretching on 4:3 content",
    "autoplay": "Next file in folder starts automatically.\nSorted alphabetically\nVideo/audio files only",
    "hwdec": "Offloads decode to iGPU (VA-API/VA-API2).\nFrees CPU, reduces heat\nESSENTIAL for smooth playback on iGPU\nGreen artifacts? Try 'auto-safe' instead of 'vaapi'",
    "hwdec_mode": "Choose hardware decode backend:\n\n• vaapi — standard, works on all Intel\n• auto-safe — tries vaapi, falls back to CPU\n• auto — tries all, picks best (slower start)\n\nUse 'auto-safe' if you get green/purple artifacts",
    "profile_fast": "Lower internal precision, skips expensive passes.\n~15-20% faster rendering\nCRITICAL for weak iGPU (HD 620, UHD 630)\nOn Iris Xe you can turn this off",
    "vo_gpu_next": "mpv's newer GPU backend.\nBetter perf + shader support\nMore stable on Intel drivers\nAlways keep ON",
    "scale_lanczos": "Highest-quality scaler available.\nPreserves fine detail during 480p→1080p\nMost impactful quality setting\nCost: ~2-3ms (negligible on all iGPUs)",
    "scale_sinc": "Sinc (Lanczos) with windowing — even sharper.\nSlightly more aliasing than lanczossharp\nUse if you want maximum crispness\nCost: ~3-4ms",
    "sigmoid": "S-curve on scaler output.\nReduces ringing/halos around edges\nMakes upscale look smoother\nCost: negligible",
    "correct_downscale": "Improves 4K→1080p quality.\nNo effect on 480p source\nFuture-proofing\nCost: negligible",
    "deband": "Removes color bands in gradients.\n480p suffers heavily (256 levels/channel)\n4 iterations, threshold 48\nCost: very low",
    "deband_hq": "hdeband.glsl — GPU-accelerated debanding.\nBetter quality than built-in deband\nWorks in shader pipeline (order matters)\nCost: low (~1ms)\nEnable INSTEAD of built-in deband for best results",
    "dither": "Subtle noise after debanding.\nBreaks up remaining quantization\nMakes gradients silky smooth\nCost: negligible",
    "krig": "HEAVIEST shader. Upscales chroma separately.\nSharper, more accurate colors\nOn HD 620: ~5-8ms per frame\nOn Iris Xe: ~2-3ms (fine)\nUNCHECK FIRST if you see stutter on weak iGPU",
    "cfl": "CfL_Prediction — chroma upscaling (lighter than Krig).\n~50% cheaper than KrigBilateral\nSlightly less sharp but still good\nRECOMMENDED for HD 620 / UHD 630\nCost: ~2-3ms",
    "vivid_hdr": "Makes SDR look 'HDR-like':\n• S-curve contrast (1.25×)\n• Gamma 0.92 (brighter midtones)\n• Saturation 1.35× (vivid colors)\n• Warm tint (cinematic feel)\n• Soft-clip (smooth highlight roll-off)\nCost: very low (simple math)",
    "soft_look": "Gentle enhancement — safest shader.\n• Mild contrast (1.08×)\n• Slight saturation (1.12×)\n• Gentle black crush\nUse if vivid_hdr looks too aggressive\nCost: negligible",
    "adaptive_sharpen": "Edge-aware sharpening.\nSharpens edges, leaves flat areas alone\nNo halos or ringing\nPerfect for 480p→1080p\nCost: ~1-2ms",
    "ravu": "Lighter alternative to adaptive-sharpen.\nSimpler algorithm\nUse only if adaptive causes issues\nDon't enable both",
    "bass": "Boosts low frequencies.\n• +5dB — subtle warmth\n• +10dB — punchy (default)\n• +15dB — heavy bass (small speakers)\nCost: negligible (DSP)",
    "treble": "Boosts high frequencies.\n• +5dB — gentle air\n• +10dB — crisp (default)\n• +15dB — very bright (may sizzle)\nCost: negligible (DSP)",
    "surround": "Widens stereo image for spatial feel.\n• Narrow — subtle widening\n• Wide — obvious 3D effect\n• Ultra — maximum spread (may sound hollow)\nBest for movies, less effective on music",
    "acompressor": "Dynamic range compression.\nLouds quiet parts, tames loud parts\nConsistent volume throughout\nAlways last in audio chain\nCost: negligible",
    "loudnorm": "EBU R128 loudness normalization.\nStandardizes volume to -16 LUFS\nGreat for mixing content from different sources\nUse INSTEAD of compressor (not both)",
    "volume_150": "Starts at 150% volume.\nFine on headphones\nMay distort on speakers above 120%\nAdjust with +/- during playback",
    "subtitles": "Auto-load matching subtitle files (.srt/.ass)\nfrom the same folder as the video.\nFont: default, size: auto\nCost: negligible",
    "compositor_off": "Disables XFCE window compositor.\nRemoves extra GPU copy pass\nBIGGEST performance win for video on iGPU\nSide effect: no shadows/transparency\nRe-enable: xfconf-query -c xfwm4 -p /general/use_compositing -t bool -s true",
    "vsync": "Synchronizes frame output to monitor refresh.\nPrevents tearing\nOn iGPU: usually free (no extra cost)\nIf you see stutter, try unchecking",
}


class Tooltip:
    def __init__(self, widget, text, help_key=None):
        self.widget = widget
        self.text = text
        self.help_key = help_key
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
    def show(self, event=None):
        if self.tip: return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        content = self.text
        if self.help_key and self.help_key in HELP:
            content += "\n\n" + HELP[self.help_key]
        tk.Label(tw, text=content, justify=tk.LEFT,
                 background="#ffffe0", foreground="#1e1e2e",
                 relief=tk.SOLID, borderwidth=1,
                 font=("Arial", 9), padx=10, pady=8,
                 wraplength=380).pack()
    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


class MpVConfig:
    def __init__(self, root):
        self.root = root
        root.title("mpv Configurator — iGPU Optimized")
        root.geometry("660x880")
        root.resizable(False, False)
        root.configure(bg="#1e1e2e")

        # Detect iGPU
        self.gpu_name, self.gpu_tier = detect_igpu()

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Arial", 13, "bold"))
        style.configure("Sub.TLabel", background="#1e1e2e", foreground="#a6adc8", font=("Arial", 9))
        style.configure("GPU.TLabel", background="#1e1e2e", foreground="#94e2d5", font=("Arial", 10, "bold"))
        style.configure("Section.TLabel", background="#1e1e2e", foreground="#89b4fa", font=("Arial", 10, "bold"))
        style.configure("Detail.TLabel", background="#1e1e2e", foreground="#a6adc8", font=("Arial", 8))
        style.configure("Dark.TCheckbutton", background="#1e1e2e", foreground="#cdd6f4", font=("Arial", 9))
        style.configure("Dark.TFrame", background="#1e1e2e")
        style.configure("Dark.TCombobox", background="#313244", foreground="#cdd6f4",
                        fieldbackground="#313244", arrowcolor="#cdd6f4")
        style.configure("Dark.TScale", background="#1e1e2e", troughcolor="#313244")
        style.configure("Status.TLabel", background="#1e1e2e", foreground="#a6e3a1", font=("Arial", 9))
        style.configure("Warn.TLabel", background="#1e1e2e", foreground="#f9e2af", font=("Arial", 9, "bold"))

        self.vars = {}
        self.build_ui()
        self.apply_preset("balanced")  # Default to balanced

    def build_ui(self):
        # === TOP ===
        top = ttk.Frame(self.root, style="Dark.TFrame")
        top.pack(fill=tk.X, padx=10, pady=(8, 0))
        ttk.Label(top, text="⚙ mpv + SMPlayer — iGPU Optimized", style="Title.TLabel").pack(anchor=tk.W)
        gpu_label = f"🖥 Detected: {self.gpu_name}"
        tier_text = {0: " (LIGHT preset recommended)", 1: " (BALANCED recommended)", 2: " (MAX recommended)"}
        ttk.Label(top, text=gpu_label + tier_text.get(self.gpu_tier, ""), style="GPU.TLabel").pack(anchor=tk.W, pady=(2, 0))
        ttk.Label(top, text="Hover any option for detailed help", style="Sub.TLabel").pack(anchor=tk.W)

        # === SCROLL AREA ===
        mid = ttk.Frame(self.root, style="Dark.TFrame")
        mid.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        canvas = tk.Canvas(mid, bg="#1e1e2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(mid, orient=tk.VERTICAL, command=canvas.yview)
        self.inner = ttk.Frame(canvas, style="Dark.TFrame")
        self.inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self.build_sections()

        # === BOTTOM BUTTONS (pinned) ===
        btn_frame = ttk.Frame(self.root, style="Dark.TFrame")
        btn_frame.pack(fill=tk.X, padx=10, pady=(5, 8))
        tk.Button(btn_frame, text="  ✓  APPLY  ", command=self.apply,
                  bg="#a6e3a1", fg="#1e1e2e", relief=tk.RAISED, bd=2,
                  font=("Arial", 11, "bold"), padx=18, pady=8,
                  activebackground="#94e2d5", activeforeground="#1e1e2e",
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(btn_frame, text="  ⚡  LIGHT  ", command=lambda: self.apply_preset("light"),
                  bg="#94e2d5", fg="#1e1e2e", relief=tk.RAISED, bd=2,
                  font=("Arial", 10, "bold"), padx=12, pady=8,
                  activebackground="#89dceb", activeforeground="#1e1e2e",
                  cursor="hand2").pack(side=tk.LEFT, padx=3)
        tk.Button(btn_frame, text="  ⚖  BALANCED  ", command=lambda: self.apply_preset("balanced"),
                  bg="#89b4fa", fg="#1e1e2e", relief=tk.RAISED, bd=2,
                  font=("Arial", 10, "bold"), padx=12, pady=8,
                  activebackground="#74c7ec", activeforeground="#1e1e2e",
                  cursor="hand2").pack(side=tk.LEFT, padx=3)
        tk.Button(btn_frame, text="  🔥  MAX  ", command=lambda: self.apply_preset("max"),
                  bg="#fab387", fg="#1e1e2e", relief=tk.RAISED, bd=2,
                  font=("Arial", 10, "bold"), padx=12, pady=8,
                  activebackground="#f9e2af", activeforeground="#1e1e2e",
                  cursor="hand2").pack(side=tk.LEFT, padx=3)
        tk.Button(btn_frame, text="  ↺  RESET  ", command=self.reset_all_off,
                  bg="#f38ba8", fg="#1e1e2e", relief=tk.RAISED, bd=2,
                  font=("Arial", 10, "bold"), padx=12, pady=8,
                  activebackground="#eba0ac", activeforeground="#1e1e2e",
                  cursor="hand2").pack(side=tk.LEFT, padx=3)

        self.status = ttk.Label(self.root, text=f"Ready — {self.gpu_name} detected", style="Status.TLabel")
        self.status.pack(fill=tk.X, padx=10, pady=(0, 5))

    def build_sections(self):
        # === PRESETS ===
        self.section("⚡  QUALITY PRESET (one-click)")
        preset_row = ttk.Frame(self.inner, style="Dark.TFrame")
        preset_row.pack(fill=tk.X, pady=2, padx=2)
        ttk.Label(preset_row, text="  Quick set:  ", style="Dark.TCheckbutton").pack(side=tk.LEFT)
        self.preset_var = tk.StringVar(value="balanced")
        for txt, val in [("Light", "light"), ("Balanced", "balanced"), ("Max", "max")]:
            ttk.Radiobutton(preset_row, text=txt, value=val, variable=self.preset_var,
                            style="Dark.TCheckbutton",
                            command=lambda v=val: self.apply_preset(v)).pack(side=tk.LEFT, padx=8)
        Tooltip(preset_row, "One-click presets", help_key="preset")

        # === PLAYBACK ===
        self.section("▶  PLAYBACK")
        self.check("Fullscreen", "Start maximized", "fullscreen", True, "Opens fullscreen. Toggle: F")
        self.check("Keep Aspect Ratio", "No distortion", "keepaspect", True, "16:9 on 16:9 = perfect fill")
        self.check("Auto-play next in folder", "Queue all videos", "autoplay", True, "Next file starts automatically")
        self.check("Auto-load subtitles (.srt/.ass)", "Match by filename", "subtitles", True, "Loads matching subtitle from same folder")
        self.check("VSync", "Sync to monitor refresh", "vsync", True, "Prevents tearing. Free on iGPU")

        # === PERFORMANCE ===
        self.section(f"⚡  PERFORMANCE ({self.gpu_name})")
        self.check("Hardware Decode", "GPU decodes — frees CPU", "hwdec", True, "Essential for iGPU playback")
        # hwdec mode selector
        hw_row = ttk.Frame(self.inner, style="Dark.TFrame")
        hw_row.pack(fill=tk.X, pady=1, padx=14)
        ttk.Label(hw_row, text="Decode mode:", style="Detail.TLabel").pack(side=tk.LEFT)
        self.hwdec_mode = tk.StringVar(value="vaapi")
        cb = ttk.Combobox(hw_row, textvariable=self.hwdec_mode, values=["vaapi", "auto-safe", "auto"],
                          width=12, state="readonly", style="Dark.TCombobox")
        cb.pack(side=tk.LEFT, padx=(8, 0))
        Tooltip(cb, "Hardware decode backend", help_key="hwdec_mode")
        self.check("Profile: fast", "Optimized for weak iGPU", "profile_fast", True, "Lower precision, ~15% faster")
        self.check("vo=gpu-next", "Modern renderer", "vo_gpu_next", True, "Newer GPU backend, better on Intel")

        # === UPSCALING ===
        self.section("📐  UPSCALING (480p → 1080p)")
        self.check("EWA Lanczos Sharp", "Best quality scaler", "scale_lanczos", True, "Highest perceived quality")
        self.check("Sigmoid Upscaling", "Reduces ringing", "sigmoid", True, "S-curve, less halo")
        self.check("Correct Downscaling", "For 4K→1080p", "correct_downscale", True, "No effect on 480p")

        # === COLOR & LOOK ===
        self.section("🎨  COLOR & LOOK")
        self.check("Vivid HDR (aggressive)", "S-curve + sat 1.35× + warm", "vivid_hdr", True, "Full HDR-like look")
        self.check("Soft Look (gentle)", "Mild contrast + slight sat", "soft_look", False, "Subtle enhancement, safest")
        self.check("Debanding (built-in)", "Fixes color bands", "deband", True, "Removes bands in gradients")
        self.check("hdeband (GPU shader)", "Better debanding via shader", "deband_hq", False, "GPU-accelerated, use instead of built-in")
        self.check("Dithering", "Hides artifacts", "dither", True, "Smooth gradients")

        # === SHARPENING & CHROMA ===
        self.section("🔬  SHARPENING & CHROMA")
        self.check("KrigBilateral (chroma)", "⚠ HEAVY — sharpest colors", "krig", False, "UNCHECK FIRST if stutter")
        self.check("CfL_Prediction (chroma)", "Lighter chroma upscale", "cfl", True, "50% cheaper than Krig. RECOMMENDED for HD 620")
        self.check("Adaptive Sharpen", "Edge-aware, no halos", "adaptive_sharpen", True, "Sharpens edges only")
        self.check("Ravu Sharpen (light)", "Lighter alternative", "ravu", False, "Use if adaptive causes issues")

        # === AUDIO ===
        self.section("🔊  AUDIO")
        # Bass level
        bass_row = ttk.Frame(self.inner, style="Dark.TFrame")
        bass_row.pack(fill=tk.X, pady=2, padx=2)
        self.bass_var = tk.IntVar(value=10)
        ttk.Label(bass_row, text="  Bass: ", style="Dark.TCheckbutton").pack(side=tk.LEFT)
        ttk.Scale(bass_row, from_=0, to=20, variable=self.bass_var, orient=tk.HORIZONTAL,
                  length=150, style="Dark.TScale").pack(side=tk.LEFT, padx=5)
        self.bass_label = ttk.Label(bass_row, text="+10dB", style="Detail.TLabel")
        self.bass_label.pack(side=tk.LEFT)
        self.bass_var.trace_add("write", lambda *a: self.bass_label.config(text=f"+{self.bass_var.get()}dB"))
        Tooltip(bass_row, "Bass boost level", help_key="bass")

        # Treble level
        treb_row = ttk.Frame(self.inner, style="Dark.TFrame")
        treb_row.pack(fill=tk.X, pady=2, padx=2)
        self.treble_var = tk.IntVar(value=10)
        ttk.Label(treb_row, text="  Treble: ", style="Dark.TCheckbutton").pack(side=tk.LEFT)
        ttk.Scale(treb_row, from_=0, to=20, variable=self.treble_var, orient=tk.HORIZONTAL,
                  length=150, style="Dark.TScale").pack(side=tk.LEFT, padx=5)
        self.treble_label = ttk.Label(treb_row, text="+10dB", style="Detail.TLabel")
        self.treble_label.pack(side=tk.LEFT)
        self.treble_var.trace_add("write", lambda *a: self.treble_label.config(text=f"+{self.treble_var.get()}dB"))
        Tooltip(treb_row, "Treble boost level", help_key="treble")

        # Surround width
        surr_row = ttk.Frame(self.inner, style="Dark.TFrame")
        surr_row.pack(fill=tk.X, pady=2, padx=2)
        self.surr_var = tk.StringVar(value="wide")
        ttk.Label(surr_row, text="  Surround: ", style="Dark.TCheckbutton").pack(side=tk.LEFT)
        for txt, val in [("Off", "off"), ("Narrow", "narrow"), ("Wide", "wide"), ("Ultra", "ultra")]:
            ttk.Radiobutton(surr_row, text=txt, value=val, variable=self.surr_var,
                            style="Dark.TCheckbutton").pack(side=tk.LEFT, padx=4)
        Tooltip(surr_row, "3D surround width", help_key="surround")

        self.check("Compressor (acompressor)", "Even volume", "acompressor", True, "Louds quiet, tames loud")
        self.check("Loudness Normalize (R128)", "Standardize to -16 LUFS", "loudnorm", False, "Use instead of compressor")
        self.check("Volume 150%", "⚠ LOUD — max from start", "volume_150", True, "Starts at 150%")

        # === SYSTEM ===
        self.section("🖥  SYSTEM")
        self.check("Disable XFCE Compositor", "BIGGEST perf win", "compositor_off", True, "Removes extra GPU pass")

    def section(self, title):
        ttk.Separator(self.inner, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(10, 2))
        ttk.Label(self.inner, text=title, style="Section.TLabel").pack(anchor=tk.W)

    def check(self, label, detail, var_name, default, tooltip_short):
        row = ttk.Frame(self.inner, style="Dark.TFrame")
        row.pack(fill=tk.X, pady=2, padx=2)
        var = tk.BooleanVar(value=default)
        self.vars[var_name] = var
        cb = ttk.Checkbutton(row, text=f"  {label}  ", variable=var, style="Dark.TCheckbutton")
        cb.pack(side=tk.LEFT)
        ttk.Label(row, text=detail, style="Detail.TLabel").pack(side=tk.LEFT, padx=(4, 0))
        Tooltip(cb, f"{label}\n{tooltip_short}", help_key=var_name)
        cb.bind("<Enter>", lambda e, n=label: self.status.config(text=f"ℹ {n}"))
        cb.bind("<Leave>", lambda e: self.status.config(text=f"Ready — {self.gpu_name}"))

    def apply_preset(self, preset):
        """Apply quality preset based on iGPU tier"""
        self.preset_var.set(preset)
        if preset == "light":
            cfg = {
                "fullscreen": True, "keepaspect": True, "autoplay": True,
                "subtitles": True, "vsync": True,
                "hwdec": True, "profile_fast": True, "vo_gpu_next": True,
                "scale_lanczos": True, "sigmoid": True, "correct_downscale": True,
                "vivid_hdr": False, "soft_look": True,
                "deband": True, "deband_hq": False, "dither": True,
                "krig": False, "cfl": False, "adaptive_sharpen": True, "ravu": False,
                "acompressor": True, "loudnorm": False, "volume_150": True,
                "compositor_off": True,
            }
        elif preset == "balanced":
            cfg = {
                "fullscreen": True, "keepaspect": True, "autoplay": True,
                "subtitles": True, "vsync": True,
                "hwdec": True, "profile_fast": True, "vo_gpu_next": True,
                "scale_lanczos": True, "sigmoid": True, "correct_downscale": True,
                "vivid_hdr": True, "soft_look": False,
                "deband": True, "deband_hq": False, "dither": True,
                "krig": False, "cfl": True, "adaptive_sharpen": True, "ravu": False,
                "acompressor": True, "loudnorm": False, "volume_150": True,
                "compositor_off": True,
            }
        else:  # max
            cfg = {
                "fullscreen": True, "keepaspect": True, "autoplay": True,
                "subtitles": True, "vsync": True,
                "hwdec": True, "profile_fast": self.gpu_tier >= 1, "vo_gpu_next": True,
                "scale_lanczos": True, "sigmoid": True, "correct_downscale": True,
                "vivid_hdr": True, "soft_look": False,
                "deband": False, "deband_hq": True, "dither": True,
                "krig": self.gpu_tier >= 1, "cfl": self.gpu_tier == 0,
                "adaptive_sharpen": True, "ravu": False,
                "acompressor": True, "loudnorm": False, "volume_150": True,
                "compositor_off": True,
            }
        for k, v in cfg.items():
            if k in self.vars:
                self.vars[k].set(v)
        # Audio levels
        if preset == "light":
            self.bass_var.set(5); self.treble_var.set(5); self.surr_var.set("narrow")
        elif preset == "balanced":
            self.bass_var.set(10); self.treble_var.set(10); self.surr_var.set("wide")
        else:
            self.bass_var.set(12); self.treble_var.set(12); self.surr_var.set("wide")
        self.bass_label.config(text=f"+{self.bass_var.get()}dB")
        self.treble_label.config(text=f"+{self.treble_var.get()}dB")
        self.status.config(text=f"✓ {preset.upper()} preset applied for {self.gpu_name}")

    def reset_all_off(self):
        for v in self.vars.values(): v.set(False)
        self.bass_var.set(0); self.treble_var.set(0); self.surr_var.set("off")
        self.bass_label.config(text="+0dB"); self.treble_label.config(text="+0dB")
        self.status.config(text="All unchecked")

    def apply(self):
        os.makedirs(SHADER_DIR, exist_ok=True)

        # Determine active shaders
        sl = []
        if self.vars["deband_hq"].get():
            sl.append("~~/shaders/hdeband.glsl")
        if self.vars["cfl"].get():
            sl.append("~~/shaders/CfL_Prediction.glsl")
        if self.vars["krig"].get():
            sl.append("~~/shaders/KrigBilateral.glsl")
        if self.vars["vivid_hdr"].get():
            sl.append("~~/shaders/vivid_hdr.glsl")
        elif self.vars["soft_look"].get():
            sl.append("~~/shaders/soft_look.glsl")
        if self.vars["adaptive_sharpen"].get():
            sl.append("~~/shaders/adaptive-sharpen.glsl")
        if self.vars["ravu"].get():
            sl.append("~~/shaders/ravu-r3-rgb.glsl")

        # Download needed shaders
        needed = [s.split("/")[-1] for s in sl]
        for s in needed:
            p = os.path.join(SHADER_DIR, s)
            if not os.path.exists(p) and s in SHADERS:
                downloaded = False
                try:
                    subprocess.run(["curl","-sL","--connect-timeout","10","--max-time","120","-o",p,SHADERS[s]],check=True,timeout=130)
                    downloaded = True
                except: pass
                if not downloaded:
                    try:
                        subprocess.run(["wget","-q","-O",p,SHADERS[s]],check=True,timeout=130)
                        downloaded = True
                    except: pass
                if not downloaded:
                    messagebox.showerror("Download Failed",
                        f"Could not get {s}\n\nSave manually to:\n{p}\n\nURL:\n{SHADERS[s]}\n\nThen click Apply again.")
                    return

        # Write local shaders
        if self.vars["vivid_hdr"].get():
            with open(os.path.join(SHADER_DIR, "vivid_hdr.glsl"), "w") as f: f.write(VIVID_SHADER)
        if self.vars["soft_look"].get():
            with open(os.path.join(SHADER_DIR, "soft_look.glsl"), "w") as f: f.write(SOFT_SHADER)

        # Build mpv.conf
        lines = []
        if self.vars["profile_fast"].get(): lines.append("profile=fast")
        if self.vars["vo_gpu_next"].get(): lines.append("vo=gpu-next")
        if self.vars["hwdec"].get():
            lines.append(f"hwdec={self.hwdec_mode.get()}")
        if self.vars["fullscreen"].get(): lines.append("fullscreen=yes")
        if self.vars["keepaspect"].get(): lines.append("keepaspect=yes")
        if self.vars["autoplay"].get(): lines.append("autocreate-playlist=same")
        if self.vars["subtitles"].get():
            lines.append("sub-auto=fuzzy")
        if self.vars["vsync"].get(): lines.append("display-fps-match=yes")
        if self.vars["scale_lanczos"].get():
            lines += ["scale=ewa_lanczossharp", "cscale=bicubic", "dscale=mitchell"]
        if self.vars["sigmoid"].get(): lines.append("sigmoid-upscaling=yes")
        if self.vars["correct_downscale"].get(): lines.append("correct-downscaling=yes")
        if self.vars["deband"].get():
            lines += ["deband=yes", "deband-iterations=4", "deband-threshold=48", "deband-range=16", "deband-grain=12"]
        if self.vars["dither"].get():
            lines += ["dither-depth=auto", "temporal-dither=yes"]
        if sl: lines.append(f"glsl-shader={':'.join(sl)}")

        # Audio
        lines.append("ao=alsa")
        if self.vars["volume_150"].get(): lines += ["volume=150", "volume-max=150"]
        af = []
        if self.bass_var.get() > 0: af.append(f"bass=g={self.bass_var.get()}")
        if self.treble_var.get() > 0: af.append(f"treble=g={self.treble_var.get()}")
        surr = self.surr_var.get()
        if surr == "narrow": af.append("stereowiden=angle=20")
        elif surr == "wide": af.append("stereowiden=angle=35")
        elif surr == "ultra": af.append("stereowiden=angle=50")
        if self.vars["acompressor"].get(): af.append("acompressor")
        if self.vars["loudnorm"].get(): af.append("loudnorm=I=-16:TP=-1.5")
        if af: lines.append(f"af={':'.join(af)}")
        lines += ["osc=yes", "ytdl=no"]

        with open(CONF_FILE, "w") as f: f.write("\n".join(lines) + "\n")

        # input.conf
        il = []
        if sl:
            il.append(f'CTRL+1 no-osd change-list glsl-shaders set "{":".join(sl)}" : show-text "Shaders ON"')
            il.append('CTRL+2 no-osd change-list glsl-shaders clr : show-text "Shaders OFF"')
        il += ["+ add volume 5", "- add volume -5", "f cycle fullscreen"]
        with open(INPUT_FILE, "w") as f: f.write("\n".join(il) + "\n")

        # Compositor
        val = "false" if self.vars["compositor_off"].get() else "true"
        subprocess.run(["xfconf-query","-c","xfwm4","-p","/general/use_compositing","-t","bool","-s",val],capture_output=True)

        self.status.config(text=f"✓ Applied — {len(lines)} lines | {self.gpu_name}")
        messagebox.showinfo("Done",
            f"✓ Applied for {self.gpu_name}\n\n"
            f"Preset: {self.preset_var.get().upper()}\n"
            f"Lines: {len(lines)}\n"
            f"Shaders: {len(sl)}\n\n"
            "Test:\n  mpv /path/to/video.mp4\n  smplayer /path/to/video.mp4")


if __name__ == "__main__":
    root = tk.Tk()
    app = MpVConfig(root)
    root.mainloop()   
