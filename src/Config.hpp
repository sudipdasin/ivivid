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
};
QString validate(const Settings &settings);
QString renderMpv(const Settings &settings);
QString configPath();
bool applyConfig(const Settings &settings, QString *error);
}
