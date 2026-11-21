#include "MainWindow.hpp"
#include <QCheckBox>
#include <QClipboard>
#include <QGuiApplication>
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
#include <QSysInfo>
#include <QLibraryInfo>
#include <QDir>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QSaveFile>
#include <QShortcut>
#include <QKeySequence>
MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
    setWindowTitle("iVivid — Video Enhancement");
    resize(1020, 700);
    setMinimumSize(720, 580);
    auto *root = new QWidget(this);
    auto *layout = new QVBoxLayout(root);
    layout->setContentsMargins(18, 18, 18, 18);
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
    spatialAudio_ = new QCheckBox("3D Spatial Sound — stereo widening (headphones)", audio);
    spatialAudio_->setObjectName("spatialAudioEnabled");
    spatialAudio_->setToolTip("Uses FFmpeg stereowiden for a wider stereo image. This is not discrete surround or binaural object audio.");
    af->addRow(spatialAudio_);
    tabs->addTab(audio, "Audio");
    auto *experimental = new QWidget(tabs);
    auto *ef = new QVBoxLayout(experimental);
    auto *warning = new QLabel("Experimental options may increase CPU use, latency or audio distortion.", experimental);
    warning->setWordWrap(true); ef->addWidget(warning);
    normalize_ = new QCheckBox("Experimental: EBU R128 loudness normalization", experimental);
    normalize_->setObjectName("normalizeEnabled");
    normalize_->setToolTip("Uses FFmpeg loudnorm via mpv. Behavior depends on your mpv/FFmpeg build.");
    ef->addWidget(normalize_);
    ef->addWidget(new QLabel("Future experiments: GPU capability detection, custom shaders and synchronized A/B playback.", experimental));
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
    auto *actions = new QVBoxLayout();
    auto *presetActions = new QHBoxLayout();
    auto *toolActions = new QHBoxLayout();
    auto *playbackActions = new QHBoxLayout();
    auto *preview = new QPushButton("Preview settings", root);
    preview->setObjectName("previewSettings");
    auto *apply = new QPushButton("Save settings", root);
    apply->setObjectName("saveSettings");
    auto *copy = new QPushButton("Copy settings", root);
    copy->setObjectName("copySettings");
    auto *reset = new QPushButton("Reset defaults", root);
    reset->setObjectName("resetDefaults");
    auto *importPreset = new QPushButton("Import preset…", root);
    importPreset->setObjectName("importPreset");
    auto *exportPreset = new QPushButton("Export preset…", root);
    exportPreset->setObjectName("exportPreset");
    auto *inspect = new QPushButton("Inspect media…", root);
    inspect->setObjectName("inspectMedia");
    inspect->setToolTip("Inspect local video/audio metadata with ffprobe, without changing the file.");
    auto *diagnostics = new QPushButton("System diagnostics", root);
    diagnostics->setObjectName("systemDiagnostics");
    auto *compare = new QPushButton("Compare original…", root);
    compare->setObjectName("compareOriginal");
    compare->setToolTip("Play a video with no iVivid enhancements for an original-versus-enhanced comparison.");
    auto *play = new QPushButton("Test video…", root);
    play->setObjectName("testVideo");
    // Keep saveSettings as the stable automation identifier.
    presetActions->addWidget(importPreset); presetActions->addWidget(exportPreset); presetActions->addWidget(copy); presetActions->addWidget(reset);
    toolActions->addWidget(preview); toolActions->addWidget(inspect); toolActions->addWidget(diagnostics);
    playbackActions->addWidget(compare); playbackActions->addWidget(play); playbackActions->addWidget(apply);
    actions->addLayout(presetActions); actions->addLayout(toolActions); actions->addLayout(playbackActions);
    apply->setShortcut(QKeySequence::Save);
    preview->setShortcut(QKeySequence(Qt::CTRL | Qt::Key_P));
    importPreset->setShortcut(QKeySequence(Qt::CTRL | Qt::Key_O));
    layout->addLayout(actions);
    connect(copy, &QPushButton::clicked, this, [this] {
        QGuiApplication::clipboard()->setText(ivivid::renderMpv(settings()));
        status_->setText("Enhancement settings copied to clipboard.");
    });
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
        spatialAudio_->setChecked(defaults.spatialAudio);
        status_->setText("Default controls restored. Click Save settings to persist them.");
    });
    connect(exportPreset, &QPushButton::clicked, this, [this] {
        const QString path = QFileDialog::getSaveFileName(this, "Export iVivid preset", QString(), "mpv configuration (*.conf);;All files (*)");
        if (path.isEmpty()) return;
        const QString validation = ivivid::validate(settings());
        if (!validation.isEmpty()) {
            QMessageBox::warning(this, "Invalid settings", validation);
            return;
        }
        QSaveFile output(path);
        if (!output.open(QIODevice::WriteOnly) || output.write(ivivid::renderMpv(settings()).toUtf8()) < 0 || !output.commit()) {
            QMessageBox::warning(this, "Export failed", "Could not write the selected preset file.");
            return;
        }
        status_->setText("Exported preset: " + QFileInfo(path).fileName());
    });
    connect(importPreset, &QPushButton::clicked, this, [this] {
        const QString path = QFileDialog::getOpenFileName(this, "Import iVivid preset", QString(), "mpv configuration (*.conf);;All files (*)");
        if (path.isEmpty()) return;
        ivivid::Settings imported;
        QString error;
        if (!ivivid::loadConfigFile(path, &imported, &error)) {
            QMessageBox::warning(this, "Import rejected", error);
            return;
        }
        preset_->setCurrentIndex(imported.preset);
        saturation_->setValue(imported.saturation);
        brightness_->setValue(imported.brightness);
        contrast_->setValue(imported.contrast);
        bass_->setValue(imported.bass);
        treble_->setValue(imported.treble);
        hardware_->setChecked(imported.hardwareDecode);
        deband_->setChecked(imported.deband);
        normalize_->setChecked(imported.normalize);
        spatialAudio_->setChecked(imported.spatialAudio);
        status_->setText("Imported preset (not saved): " + QFileInfo(path).fileName());
    });
    connect(inspect, &QPushButton::clicked, this, [this] {
        const QString file = QFileDialog::getOpenFileName(this, "Inspect local media", QString(),
            "Media files (*.mp4 *.mkv *.webm *.avi *.mov *.m4v *.mp3 *.flac *.wav *.ogg);;All files (*)");
        if (file.isEmpty()) return;
        const QString probe = QStandardPaths::findExecutable("ffprobe");
        if (probe.isEmpty()) {
            QMessageBox::warning(this, "ffprobe unavailable", "Install ffmpeg to inspect media metadata.");
            return;
        }
        QProcess process;
        process.start(probe, {"-v", "error", "-show_entries", "format=duration,size:stream=codec_type,codec_name,width,height", "-of", "json", "--", file});
        if (!process.waitForStarted(3000) || !process.waitForFinished(10000)) {
            process.kill(); process.waitForFinished(1000);
            QMessageBox::warning(this, "Inspection timed out", "ffprobe could not inspect this file within 10 seconds.");
            return;
        }
        if (process.exitStatus() != QProcess::NormalExit || process.exitCode() != 0) {
            QMessageBox::warning(this, "Inspection failed", "ffprobe could not read metadata for this file.");
            return;
        }
        QJsonParseError parseError;
        const QJsonDocument doc = QJsonDocument::fromJson(process.readAllStandardOutput(), &parseError);
        if (parseError.error != QJsonParseError::NoError || !doc.isObject()) {
            QMessageBox::warning(this, "Inspection failed", "ffprobe returned invalid metadata.");
            return;
        }
        const QJsonObject data = doc.object();
        const QJsonObject format = data.value("format").toObject();
        QStringList lines;
        lines << "File: " + QFileInfo(file).fileName();
        lines << "Duration (seconds): " + format.value("duration").toString("unknown");
        lines << "Size (bytes): " + format.value("size").toString("unknown");
        for (const QJsonValue &entry : data.value("streams").toArray()) {
            const QJsonObject stream = entry.toObject();
            QString description = stream.value("codec_type").toString("stream") + ": " + stream.value("codec_name").toString("unknown");
            if (stream.contains("width") && stream.contains("height"))
                description += QString(" (%1 x %2)").arg(stream.value("width").toInt()).arg(stream.value("height").toInt());
            lines << description;
        }
        QMessageBox::information(this, "Local media inspection", lines.join("\\n"));
        status_->setText("Inspected metadata: " + QFileInfo(file).fileName());
    });
    connect(diagnostics, &QPushButton::clicked, this, [this] {
        const QString mpv = QStandardPaths::findExecutable("mpv");
        const QString report = QString("iVivid system diagnostics\\n\\nOS: %1\\nArchitecture: %2\\nQt version: %3\\nmpv: %4\\niVivid configuration: %5\\nConfig exists: %6\\n\\nHardware decode support requires playback on your actual GPU.")
            .arg(QSysInfo::prettyProductName(), QSysInfo::currentCpuArchitecture(),
                 QString::fromLatin1(qVersion()), mpv.isEmpty() ? QString("not installed") : mpv,
                 ivivid::configPath(), QFileInfo::exists(ivivid::configPath()) ? QString("yes") : QString("no"));
        QMessageBox::information(this, "iVivid system diagnostics", report);
    });
    connect(compare, &QPushButton::clicked, this, [this] {
        const QString file = QFileDialog::getOpenFileName(this, "Choose original video", QString(),
            "Video files (*.mp4 *.mkv *.webm *.avi *.mov *.m4v);;All files (*)");
        if (file.isEmpty()) return;
        const QString mpv = QStandardPaths::findExecutable("mpv");
        if (mpv.isEmpty()) {
            QMessageBox::warning(this, "mpv unavailable", "Install mpv to compare playback.");
            return;
        }
        if (!QProcess::startDetached(mpv, {"--no-config", "--", file})) {
            QMessageBox::critical(this, "Playback failed", "Could not launch original playback.");
            return;
        }
        status_->setText("Playing original without enhancements: " + QFileInfo(file).fileName());
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
        const QStringList args = {"--include=" + ivivid::configPath(), "--", file};
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
        spatialAudio_->setChecked(restored.spatialAudio);
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
    s.spatialAudio = spatialAudio_->isChecked();
    return s;
}
