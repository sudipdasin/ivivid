#include "MainWindow.hpp"
#include <QCheckBox>
#include <QComboBox>
#include <QFormLayout>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QMessageBox>
#include <QPushButton>
#include <QScrollArea>
#include <QSlider>
#include <QVBoxLayout>
#include <QWidget>
#include <QFileInfo>
#include <QStandardPaths>
#include <QApplication>
MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
    setWindowTitle("iVivid — Video Enhancement");
    resize(720, 690);
    auto *root = new QWidget(this);
    auto *layout = new QVBoxLayout(root);
    layout->setContentsMargins(24, 24, 24, 24);
    layout->setSpacing(14);
    auto *title = new QLabel("iVivid", root);
    title->setObjectName("appTitle");
    layout->addWidget(title);
    layout->addWidget(new QLabel("Fine-tune mpv playback for your Linux graphics hardware.", root));
    auto *video = new QGroupBox("Video", root);
    auto *vf = new QFormLayout(video);
    preset_ = new QComboBox(video);
    preset_->addItems({"Light — efficiency", "Balanced — everyday", "Max — visual quality"});
    preset_->setCurrentIndex(1);
    vf->addRow("Quality preset", preset_);
    auto slider = [this](int min, int max, int value) {
        auto *s = new QSlider(Qt::Horizontal, this);
        s->setRange(min, max); s->setValue(value);
        s->setTickInterval(10);
        return s;
    };
    saturation_ = slider(50, 200, 110); vf->addRow("Saturation (%)", saturation_);
    brightness_ = slider(-20, 20, 0); vf->addRow("Brightness", brightness_);
    contrast_ = slider(-20, 20, 0); vf->addRow("Contrast", contrast_);
    hardware_ = new QCheckBox("Enable safe hardware decoding", video); hardware_->setChecked(true);
    vf->addRow(hardware_);
    deband_ = new QCheckBox("Reduce color banding", video); deband_->setChecked(true);
    vf->addRow(deband_);
    layout->addWidget(video);
    auto *audio = new QGroupBox("Audio", root);
    auto *af = new QFormLayout(audio);
    bass_ = slider(0, 20, 0); af->addRow("Bass boost (dB)", bass_);
    treble_ = slider(0, 20, 0); af->addRow("Treble boost (dB)", treble_);
    normalize_ = new QCheckBox("Normalize loudness", audio); af->addRow(normalize_);
    layout->addWidget(audio);
    status_ = new QLabel(root);
    status_->setWordWrap(true);
    status_->setText(QStandardPaths::findExecutable("mpv").isEmpty()
        ? "mpv not found in PATH — install mpv before playback."
        : "mpv detected. Changes apply to future mpv playback.");
    layout->addWidget(status_);
    auto *actions = new QHBoxLayout();
    auto *preview = new QPushButton("Preview configuration", root);
    auto *apply = new QPushButton("Apply to mpv", root);
    apply->setObjectName("primaryButton");
    actions->addWidget(preview); actions->addWidget(apply);
    layout->addLayout(actions);
    connect(preview, &QPushButton::clicked, this, [this] {
        QMessageBox::information(this, "iVivid configuration preview", ivivid::renderMpv(settings()));
    });
    connect(apply, &QPushButton::clicked, this, [this] {
        QString error;
        if (!ivivid::applyConfig(settings(), &error)) {
            QMessageBox::critical(this, "Could not apply configuration", error);
        } else {
            status_->setText("Applied successfully. Restart playback to use the new settings.");
        }
    });
    setCentralWidget(root);
    setStyleSheet(R"(
      QMainWindow, QWidget { background: #121923; color: #e8eef7; font-size: 14px; }
      QLabel#appTitle { font-size: 30px; font-weight: 700; color: #79c7ff; }
      QGroupBox { border: 1px solid #334355; border-radius: 9px; margin-top: 14px; padding: 14px; font-weight: 600; }
      QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; }
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
