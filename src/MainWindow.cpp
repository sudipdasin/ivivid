#include "MainWindow.hpp"
#include <QCheckBox>
#include <QComboBox>
#include <QFormLayout>
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
    layout->addWidget(new QLabel("Enhance mpv playback without changing your existing mpv configuration.", root));
    auto slider = [this](int min, int max, int value) {
        auto *s = new QSlider(Qt::Horizontal, this);
        s->setRange(min, max); s->setValue(value);
        return s;
    };
    auto *tabs = new QTabWidget(root);
    auto *video = new QWidget(tabs);
    auto *vf = new QFormLayout(video);
    preset_ = new QComboBox(video);
    preset_->addItems({"Light — efficiency", "Balanced — everyday", "Max — visual quality"});
    preset_->setCurrentIndex(1);
    vf->addRow("Quality preset", preset_);
    saturation_ = slider(50, 200, 110); vf->addRow("Saturation (%)", saturation_);
    brightness_ = slider(-20, 20, 0); vf->addRow("Brightness", brightness_);
    contrast_ = slider(-20, 20, 0); vf->addRow("Contrast", contrast_);
    hardware_ = new QCheckBox("Safe hardware decoding (when available)", video);
    hardware_->setChecked(true); vf->addRow(hardware_);
    deband_ = new QCheckBox("Reduce color banding", video);
    deband_->setChecked(true); vf->addRow(deband_);
    tabs->addTab(video, "Video");
    auto *audio = new QWidget(tabs);
    auto *af = new QFormLayout(audio);
    bass_ = slider(0, 20, 0); af->addRow("Bass boost (dB)", bass_);
    treble_ = slider(0, 20, 0); af->addRow("Treble boost (dB)", treble_);
    tabs->addTab(audio, "Audio");
    auto *experimental = new QWidget(tabs);
    auto *ef = new QVBoxLayout(experimental);
    auto *warning = new QLabel("Experimental options may increase CPU use, latency or audio distortion.", experimental);
    warning->setWordWrap(true); ef->addWidget(warning);
    normalize_ = new QCheckBox("Experimental: EBU R128 loudness normalization", experimental);
    normalize_->setToolTip("Uses FFmpeg loudnorm via mpv. Behavior depends on your mpv/FFmpeg build.");
    ef->addWidget(normalize_);
    ef->addWidget(new QLabel("Future experiments: GPU capability detection, custom shaders and A/B playback.", experimental));
    ef->addStretch();
    tabs->addTab(experimental, "Experimental");
    layout->addWidget(tabs);
    status_ = new QLabel(root);
    status_->setWordWrap(true);
    status_->setText(QStandardPaths::findExecutable("mpv").isEmpty()
        ? "mpv not found in PATH. Install mpv before testing playback."
        : "mpv detected. iVivid settings are stored separately from your normal mpv.conf.");
    layout->addWidget(status_);
    auto *actions = new QHBoxLayout();
    auto *preview = new QPushButton("Preview settings", root);
    auto *apply = new QPushButton("Save settings", root);
    apply->setObjectName("primaryButton");
    actions->addWidget(preview); actions->addWidget(apply);
    layout->addLayout(actions);
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
    setStyleSheet(R"(
      QMainWindow, QWidget { background: #121923; color: #e8eef7; font-size: 14px; }
      QLabel#appTitle { font-size: 30px; font-weight: 700; color: #79c7ff; }
      QTabWidget::pane { border: 1px solid #334355; border-radius: 8px; }
      QTabBar::tab { background: #27394d; padding: 10px 17px; margin-right: 3px; }
      QTabBar::tab:selected { background: #1479c8; }
      QPushButton { background: #27394d; border-radius: 7px; padding: 11px 15px; }
      QPushButton:hover { background: #35516c; }
      QPushButton#primaryButton { background: #1479c8; color: white; font-weight: 700; }
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
