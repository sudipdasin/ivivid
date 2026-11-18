#include "../src/Config.hpp"
#include <cstdlib>
#define CHECK(expr) do { if (!(expr)) std::abort(); } while (false)
#include <QDir>
#include <QFile>
#include <QTemporaryDir>
int main() {
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
}
