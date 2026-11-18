#include "../src/Config.hpp"
#include <cassert>
int main() {
    ivivid::Settings s;
    assert(ivivid::validate(s).isEmpty());
    assert(ivivid::renderMpv(s).contains("hwdec=auto-safe"));
    s.preset = -1;
    assert(!ivivid::validate(s).isEmpty());
    s.preset = 1;
    s.saturation = 201;
    assert(!ivivid::validate(s).isEmpty());
    s.saturation = 110;
    s.normalize = true;
    assert(ivivid::renderMpv(s).contains("loudnorm"));
}
