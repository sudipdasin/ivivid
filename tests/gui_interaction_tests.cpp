#include "../src/MainWindow.hpp"
#include "../src/Config.hpp"
#include <QApplication>
#include <QCheckBox>
#include <QComboBox>
#include <QFile>
#include <QLabel>
#include <QPushButton>
#include <QSlider>
#include <QTabWidget>
#include <QTemporaryDir>
#include <QTest>
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
    auto *save = window.findChild<QPushButton *>("saveSettings");
    auto *reset = window.findChild<QPushButton *>("resetDefaults");
    auto *status = window.findChild<QLabel *>("statusMessage");
    CHECK(preset && sat && bass && normalize && save && reset && status);
    CHECK(preset->count() == 3);
    preset->setCurrentIndex(2);
    sat->setValue(140);
    tabs->setCurrentIndex(1);
    bass->setValue(6);
    tabs->setCurrentIndex(2);
    normalize->setChecked(true);
    tabs->setCurrentIndex(0);
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
    reset->click();
    CHECK(preset->currentIndex() == 1);
    CHECK(sat->value() == 110);
    CHECK(bass->value() == 0);
    CHECK(!normalize->isChecked());
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
    return 0;
}
