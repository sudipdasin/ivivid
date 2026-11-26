#include "../src/MainWindow.hpp"
#include "../src/Config.hpp"
#include <QApplication>
#include <QKeySequence>
#include <QCheckBox>
#include <QClipboard>
#include <QGuiApplication>
#include <QComboBox>
#include <QFile>
#include <QLabel>
#include <QPushButton>
#include <QSlider>
#include <QTabWidget>
#include <QTemporaryDir>
#include <QTest>
#include <QMetaObject>
#include <cstdlib>
#include <cstdio>
#define CHECK(expr) do { if (!(expr)) { std::fprintf(stderr, "CHECK failed: %s at %s:%d\\n", #expr, __FILE__, __LINE__); std::fflush(stderr); std::abort(); } } while (false)

int main(int argc, char **argv) {
    QTemporaryDir configRoot;
    CHECK(configRoot.isValid());
    CHECK(qputenv("XDG_CONFIG_HOME", configRoot.path().toUtf8()));
    QApplication app(argc, argv);
    MainWindow window;
    window.show();
    QCoreApplication::processEvents();
    CHECK(window.isVisible());
    auto *tabs = window.findChild<QTabWidget *>();
    CHECK(tabs && tabs->count() == 3);
    auto *preset = window.findChild<QComboBox *>("qualityPreset");
    auto *sat = window.findChild<QSlider *>("saturationSlider");
    auto *bass = window.findChild<QSlider *>("bassSlider");
    auto *normalize = window.findChild<QCheckBox *>("normalizeEnabled");
    auto *spatial = window.findChild<QCheckBox *>("spatialAudioEnabled");
    CHECK(spatial);
    auto *audioProfiles = window.findChild<QComboBox *>("audioQuickProfile");
    CHECK(audioProfiles && audioProfiles->count() == 5);
    auto *save = window.findChild<QPushButton *>("saveSettings");
    auto *reset = window.findChild<QPushButton *>("resetDefaults");
    auto *copy = window.findChild<QPushButton *>("copySettings");
    auto *importPreset = window.findChild<QPushButton *>("importPreset");
    auto *exportPreset = window.findChild<QPushButton *>("exportPreset");
    CHECK(importPreset && exportPreset);
    CHECK(window.width() >= 720);
    CHECK(window.findChild<QPushButton *>("saveSettings")->shortcut() == QKeySequence::Save);
    auto *inspect = window.findChild<QPushButton *>("inspectMedia");
    auto *diagnostics = window.findChild<QPushButton *>("systemDiagnostics");
    auto *compare = window.findChild<QPushButton *>("compareOriginal");
    CHECK(inspect && diagnostics && compare);
    auto *status = window.findChild<QLabel *>("statusMessage");
    CHECK(preset && sat && bass && normalize && save && reset && copy && status);
    CHECK(preset->count() == 3);
    auto *treble = window.findChild<QSlider *>("trebleSlider");
    CHECK(treble);
    const int expectedBass[] = {0, 3, 6, 0, 2};
    const int expectedTreble[] = {0, 3, 2, 5, 3};
    const bool expectedSpatial[] = {false, false, true, false, true};
    for (int profile = 1; profile <= 4; ++profile) {
        audioProfiles->setCurrentIndex(profile);
        CHECK(QMetaObject::invokeMethod(audioProfiles, "activated", Qt::DirectConnection, Q_ARG(int, profile)));
        CHECK(audioProfiles->currentIndex() == 0);
        CHECK(bass->value() == expectedBass[profile]);
        CHECK(treble->value() == expectedTreble[profile]);
        CHECK(spatial->isChecked() == expectedSpatial[profile]);
        CHECK(!QFile::exists(ivivid::configPath()));
    }
    preset->setCurrentIndex(2);
    sat->setValue(140);
    tabs->setCurrentIndex(1);
    bass->setValue(6);
    spatial->setChecked(true);
    tabs->setCurrentIndex(2);
    normalize->setChecked(true);
    tabs->setCurrentIndex(0);
    copy->click();
    CHECK(QGuiApplication::clipboard()->text().contains("saturation=40"));
    CHECK(QGuiApplication::clipboard()->text().contains("loudnorm"));
    CHECK(QGuiApplication::clipboard()->text().contains("stereowiden"));
    CHECK(!QFile::exists(ivivid::configPath()));
    save->click();
    QCoreApplication::processEvents();
    CHECK(status->text().startsWith("Saved."));
    QFile file(ivivid::configPath());
    CHECK(file.open(QIODevice::ReadOnly));
    const QString settings = QString::fromUtf8(file.readAll());
    CHECK(settings.contains("saturation=40"));
    CHECK(settings.contains("scale=ewa_lanczossharp"));
    CHECK(settings.contains("equalizer=f=100"));
    CHECK(settings.contains("loudnorm"));
    CHECK(!QFile::exists(configRoot.path() + "/mpv/mpv.conf"));
    // A second window must restore the saved values from the isolated XDG config.
    MainWindow reopened;
    CHECK(reopened.findChild<QComboBox *>("qualityPreset")->currentIndex() == 2);
    CHECK(reopened.findChild<QSlider *>("saturationSlider")->value() == 140);
    CHECK(reopened.findChild<QSlider *>("bassSlider")->value() == 6);
    CHECK(reopened.findChild<QCheckBox *>("normalizeEnabled")->isChecked());
    CHECK(reopened.findChild<QCheckBox *>("spatialAudioEnabled")->isChecked());
    reset->click();
    CHECK(preset->currentIndex() == 1);
    CHECK(sat->value() == 110);
    CHECK(bass->value() == 0);
    CHECK(!normalize->isChecked());
    CHECK(!spatial->isChecked());
    // Reset is non-destructive until the user explicitly saves.
    ivivid::Settings persisted;
    QString error;
    CHECK(ivivid::loadConfig(&persisted, &error));
    CHECK(persisted.saturation == 140);
    save->click();
    CHECK(ivivid::loadConfig(&persisted, &error));
    CHECK(persisted.saturation == 110);
    CHECK(persisted.bass == 0);
    CHECK(!persisted.normalize);
    CHECK(!persisted.spatialAudio);
    return 0;
}
