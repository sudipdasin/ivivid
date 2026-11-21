#pragma once
#include <QString>
#include <QStringList>
namespace ivivid {
struct Settings {
    int preset = 1;
    int saturation = 110;
    int brightness = 0;
    int contrast = 0;
    int bass = 0;
    int treble = 0;
    bool hardwareDecode = true;
    bool deband = true;
    bool normalize = false;
    bool spatialAudio = false;
};
QString validate(const Settings &settings);
QString renderMpv(const Settings &settings);
QString configPath();
// Load settings saved by iVivid; leave defaults intact on missing/invalid files.
bool loadConfig(Settings *settings, QString *error);
bool loadConfigFile(const QString &path, Settings *settings, QString *error);
bool applyConfig(const Settings &settings, QString *error);
}
