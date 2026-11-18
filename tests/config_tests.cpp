#include "../src/Config.hpp"
#include <cstdlib>
#define CHECK(expr) do { if (!(expr)) std::abort(); } while (false)
#include <QDir>
#include <QFile>
#include <QTemporaryDir>
int main() {
    QTemporaryDir configRoot;
    CHECK(configRoot.isValid());
    CHECK(qputenv("XDG_CONFIG_HOME", configRoot.path().toUtf8()));
    CHECK(ivivid::configPath() == configRoot.path() + "/iVivid/mpv.conf");

    ivivid::Settings s;
    CHECK(ivivid::validate(s).isEmpty());
    CHECK(ivivid::renderMpv(s).contains("hwdec=auto-safe"));
    CHECK(ivivid::renderMpv(s).contains("saturation=10"));
    for (int p = 0; p < 3; ++p) {
        s.preset = p;
        CHECK(ivivid::validate(s).isEmpty());
        CHECK(ivivid::renderMpv(s).contains("scale="));
    }
    s.preset = -1; CHECK(!ivivid::validate(s).isEmpty());
    s.preset = 3; CHECK(!ivivid::validate(s).isEmpty());
    s.preset = 1;
    s.saturation = 49; CHECK(!ivivid::validate(s).isEmpty());
    s.saturation = 201; CHECK(!ivivid::validate(s).isEmpty());
    s.saturation = 110;
    s.brightness = -21; CHECK(!ivivid::validate(s).isEmpty());
    s.brightness = 21; CHECK(!ivivid::validate(s).isEmpty());
    s.brightness = 0;
    s.contrast = -21; CHECK(!ivivid::validate(s).isEmpty());
    s.contrast = 21; CHECK(!ivivid::validate(s).isEmpty());
    s.contrast = 0;
    s.bass = 21; CHECK(!ivivid::validate(s).isEmpty());
    s.bass = 0;
    s.treble = 21; CHECK(!ivivid::validate(s).isEmpty());
    s.treble = 0;
    s.normalize = true;
    CHECK(ivivid::renderMpv(s).contains("loudnorm"));
    s.normalize = false;
    CHECK(!ivivid::renderMpv(s).contains("loudnorm"));
    s.hardwareDecode = false;
    CHECK(ivivid::renderMpv(s).contains("hwdec=no"));
    s.deband = false;
    CHECK(ivivid::renderMpv(s).contains("deband=no"));
    QString error;
    CHECK(ivivid::applyConfig(s, &error));
    QFile saved(ivivid::configPath());
    CHECK(saved.open(QIODevice::ReadOnly));
    CHECK(QString::fromUtf8(saved.readAll()) == ivivid::renderMpv(s));
    CHECK(!QFile::exists(configRoot.path() + "/mpv/mpv.conf"));
    ivivid::Settings loaded;
    CHECK(ivivid::loadConfig(&loaded, &error));
    CHECK(loaded.preset == s.preset);
    CHECK(loaded.saturation == s.saturation);
    CHECK(loaded.brightness == s.brightness);
    CHECK(loaded.contrast == s.contrast);
    CHECK(loaded.bass == s.bass);
    CHECK(loaded.treble == s.treble);
    CHECK(loaded.hardwareDecode == s.hardwareDecode);
    CHECK(loaded.deband == s.deband);
    CHECK(loaded.normalize == s.normalize);
    CHECK(ivivid::renderMpv(loaded) == ivivid::renderMpv(s));
    QFile invalid(ivivid::configPath());
    CHECK(invalid.open(QIODevice::WriteOnly | QIODevice::Truncate));
    CHECK(invalid.write("saturation=not-a-number\\n") > 0);
    invalid.close();
    ivivid::Settings untouched;
    untouched.saturation = 133;
    CHECK(!ivivid::loadConfig(&untouched, &error));
    CHECK(untouched.saturation == 133);
}
