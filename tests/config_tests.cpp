#include "../src/Config.hpp"
#include <cassert>
#include <QDir>
#include <QFile>
#include <QTemporaryDir>
int main() {
    ivivid::Settings s;
    assert(ivivid::validate(s).isEmpty());
    assert(ivivid::renderMpv(s).contains("hwdec=auto-safe"));
    assert(ivivid::renderMpv(s).contains("saturation=10"));
    for (int p = 0; p < 3; ++p) {
        s.preset = p;
        assert(ivivid::validate(s).isEmpty());
        assert(ivivid::renderMpv(s).contains("scale="));
    }
    s.preset = -1; assert(!ivivid::validate(s).isEmpty());
    s.preset = 3; assert(!ivivid::validate(s).isEmpty());
    s.preset = 1;
    s.saturation = 49; assert(!ivivid::validate(s).isEmpty());
    s.saturation = 201; assert(!ivivid::validate(s).isEmpty());
    s.saturation = 110;
    s.brightness = -21; assert(!ivivid::validate(s).isEmpty());
    s.brightness = 21; assert(!ivivid::validate(s).isEmpty());
    s.brightness = 0;
    s.contrast = -21; assert(!ivivid::validate(s).isEmpty());
    s.contrast = 21; assert(!ivivid::validate(s).isEmpty());
    s.contrast = 0;
    s.bass = 21; assert(!ivivid::validate(s).isEmpty());
    s.bass = 0;
    s.treble = 21; assert(!ivivid::validate(s).isEmpty());
    s.treble = 0;
    s.normalize = true;
    assert(ivivid::renderMpv(s).contains("loudnorm"));
    s.normalize = false;
    assert(!ivivid::renderMpv(s).contains("loudnorm"));
    s.hardwareDecode = false;
    assert(ivivid::renderMpv(s).contains("hwdec=no"));
    s.deband = false;
    assert(ivivid::renderMpv(s).contains("deband=no"));
}
