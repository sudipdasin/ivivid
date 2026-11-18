#include "MainWindow.hpp"
#include <QCheckBox>
#include <QComboBox>
#include <QFormLayout>
#include <QFileDialog>
#include <QProcess>
#include <QFileInfo>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QMessageBox>
#include <QPushButton>
#include <QSlider>
#include <QTabWidget>
#include <QVBoxLayout>
#include <QWidget>
#include <QStandardPaths>
MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
    setWindowTitle("iVivid — Video Enhancement");
    resize(760, 630);
    auto *root = new QWidget(this);
    auto *layout = new QVBoxLayout(root);
    layout->setContentsMargins(24, 24, 24, 24);
    layout->setSpacing(14);
    auto *title = new QLabel("iVivid", root);
    title->setObjectName("appTitle");
    layout->addWidget(title);
    auto *subtitle = new QLabel("Video & audio enhancement  •  Linux  •  mpv engine", root);
    subtitle->setObjectName("subtitle");
    layout->addWidget(subtitle);
    auto slider = [this](int min, int max, int value) {
        auto *s = new QSlider(Qt::Horizontal, this);
        s->setRange(min, max); s->setValue(value);
        return s;
    };
    auto *tabs = new QTabWidget(root);
    auto *video = new QWidget(tabs);
    auto *vf = new QFormLayout(video);
    preset_ = new QComboBox(video);
    preset_->setObjectName("qualityPreset");
    preset_->addItems({"Light — efficiency", "Balanced — everyday", "Max — visual quality"});
    preset_->setCurrentIndex(1);
    vf->addRow("Quality preset", preset_);
    saturation_ = slider(50, 200, 110); saturation_->setObjectName("saturationSlider"); vf->addRow("Saturation (%)", saturation_);
    brightness_ = slider(-20, 20, 0); brightness_->setObjectName("brightnessSlider"); vf->addRow("Brightness", brightness_);
    contrast_ = slider(-20, 20, 0); contrast_->setObjectName("contrastSlider"); vf->addRow("Contrast", contrast_);
    hardware_ = new QCheckBox("Safe hardware decoding (when available)", video);
    hardware_->setObjectName("hardwareDecode");
    hardware_->setChecked(true); vf->addRow(hardware_);
    deband_ = new QCheckBox("Reduce color banding", video);
    deband_->setObjectName("debandEnabled");
    deband_->setChecked(true); vf->addRow(deband_);
    tabs->addTab(video, "Video");
    auto *audio = new QWidget(tabs);
    auto *af = new QFormLayout(audio);
    bass_ = slider(0, 20, 0); bass_->setObjectName("bassSlider"); af->addRow("Bass boost (dB)", bass_);
    treble_ = slider(0, 20, 0); treble_->setObjectName("trebleSlider"); af->addRow("Treble boost (dB)", treble_);
    tabs->addTab(audio, "Audio");
    auto *experimental = new QWidget(tabs);
    auto *ef = new QVBoxLayout(experimental);
    auto *warning = new QLabel("Experimental options may increase CPU use, latency or audio distortion.", experimental);
    warning->setWordWrap(true); ef->addWidget(warning);
    normalize_ = new QCheckBox("Experimental: EBU R128 loudness normalization", experimental);
    normalize_->setObjectName("normalizeEnabled");
    normalize_->setToolTip("Uses FFmpeg loudnorm via mpv. Behavior depends on your mpv/FFmpeg build.");
    ef->addWidget(normalize_);
    ef->addWidget(new QLabel("Future experiments: GPU capability detection, custom shaders and A/B playback.", experimental));
    ef->addStretch();
    tabs->addTab(experimental, "Experimental");
    tabs->setDocumentMode(true);
    layout->addWidget(tabs);
    auto *hint = new QLabel("STEP 1  Adjust enhancements     STEP 2  Preview or save     STEP 3  Test video", root);
    hint->setObjectName("workflowHint");
    layout->addWidget(hint);
    status_ = new QLabel(root);
    status_->setObjectName("statusMessage");
    status_->setWordWrap(true);
    status_->setText(QStandardPaths::findExecutable("mpv").isEmpty()
        ? "mpv not found in PATH. Install mpv before testing playback."
        : "mpv detected. iVivid settings are stored separately from your normal mpv.conf.");
    layout->addWidget(status_);
    auto *actions = new QHBoxLayout();
    auto *preview = new QPushButton("Preview settings", root);
    preview->setObjectName("previewSettings");
    auto *apply = new QPushButton("Save settings", root);
    apply->setObjectName("saveSettings");
    auto *reset = new QPushButton("Reset defaults", root);
    reset->setObjectName("resetDefaults");
    auto *play = new QPushButton("Test video…", root);
    play->setObjectName("testVideo");
    // Keep saveSettings as the stable automation identifier.
    actions->addWidget(preview); actions->addWidget(reset); actions->addWidget(apply); actions->addWidget(play);
    layout->addLayout(actions);
    connect(reset, &QPushButton::clicked, this, [this] {
        const ivivid::Settings defaults;
        preset_->setCurrentIndex(defaults.preset);
        saturation_->setValue(defaults.saturation);
        brightness_->setValue(defaults.brightness);
        contrast_->setValue(defaults.contrast);
        bass_->setValue(defaults.bass);
        treble_->setValue(defaults.treble);
        hardware_->setChecked(defaults.hardwareDecode);
        deband_->setChecked(defaults.deband);
        normalize_->setChecked(defaults.normalize);
        status_->setText("Default controls restored. Click Save settings to persist them.");
    });
    connect(play, &QPushButton::clicked, this, [this] {
        const QString file = QFileDialog::getOpenFileName(this, "Choose a video to test", QString(),
            "Video files (*.mp4 *.mkv *.webm *.avi *.mov *.m4v);;All files (*)");
        if (file.isEmpty()) return;
        QString error;
        if (!ivivid::applyConfig(settings(), &error)) {
            QMessageBox::critical(this, "Could not save settings", error);
            return;
        }
        const QString mpv = QStandardPaths::findExecutable("mpv");
        if (mpv.isEmpty()) {
            QMessageBox::warning(this, "mpv unavailable", "Install mpv to test playback.");
            return;
        }
        const QStringList args = {"--include=" + ivivid::configPath(), file};
        if (!QProcess::startDetached(mpv, args)) {
            QMessageBox::critical(this, "Playback failed", "Could not launch mpv.");
            return;
        }
        status_->setText("Started playback: " + QFileInfo(file).fileName());
    });
    connect(preview, &QPushButton::clicked, this, [this] {
        QMessageBox::information(this, "iVivid mpv settings", ivivid::renderMpv(settings()));
    });
    connect(apply, &QPushButton::clicked, this, [this] {
        QString error;
        if (!ivivid::applyConfig(settings(), &error))
            QMessageBox::critical(this, "Could not save settings", error);
        else status_->setText("Saved. Open a video with ivivid-play /path/to/video.mp4 to test.");
    });
    setCentralWidget(root);
    ivivid::Settings restored;
    QString restoreError;
    if (ivivid::loadConfig(&restored, &restoreError)) {
        preset_->setCurrentIndex(restored.preset);
        saturation_->setValue(restored.saturation);
        brightness_->setValue(restored.brightness);
        contrast_->setValue(restored.contrast);
        bass_->setValue(restored.bass);
        treble_->setValue(restored.treble);
        hardware_->setChecked(restored.hardwareDecode);
        deband_->setChecked(restored.deband);
        normalize_->setChecked(restored.normalize);
    } else {
        status_->setText("Could not restore saved settings: " + restoreError);
    }
    setStyleSheet(R"(
      QMainWindow, QWidget { background: #121923; color: #e8eef7; font-size: 14px; }
      QLabel#appTitle { font-size: 36px; font-weight: 800; color: #79c7ff; }
      QLabel#subtitle { color: #9eafc1; font-size: 13px; }
      QLabel#workflowHint { color: #89b7d8; font-weight: 600; font-size: 12px; }
      QLabel { padding: 3px; }
      QTabWidget { background: #121923; }
      QTabBar::tab:hover { background: #36526b; }
      QSlider::groove:horizontal { background: #304358; height: 6px; border-radius: 3px; }
      QSlider::sub-page:horizontal { background: #168bd7; border-radius: 3px; }
      QSlider::handle:horizontal { background: #a8ddff; width: 16px; margin: -5px 0; border-radius: 8px; }
      QCheckBox { spacing: 10px; }
      QCheckBox::indicator { width: 18px; height: 18px; }
      QCheckBox::indicator:checked { background: #168bd7; border-radius: 4px; }
      QCheckBox::indicator:unchecked { border: 1px solid #617c97; border-radius: 4px; }

      QTabWidget::pane { border: 1px solid #334355; border-radius: 8px; }
      QTabBar::tab { background: #27394d; padding: 10px 17px; margin-right: 3px; }
      QTabBar::tab:selected { background: #1479c8; }
      QPushButton { background: #27394d; border-radius: 7px; padding: 11px 15px; }
      QPushButton:hover { background: #35516c; }
      QPushButton#saveSettings { background: #1479c8; color: white; font-weight: 700; }
      QComboBox { background: #27394d; padding: 7px; border-radius: 5px; }
    )");
}
ivivid::Settings MainWindow::settings() const {
    ivivid::Settings s;
    s.preset = preset_->currentIndex();
    s.saturation = saturation_->value();
    s.brightness = brightness_->value();
    s.contrast = contrast_->value();
    s.bass = bass_->value();
    s.treble = treble_->value();
    s.hardwareDecode = hardware_->isChecked();
    s.deband = deband_->isChecked();
    s.normalize = normalize_->isChecked();
    return s;
}
