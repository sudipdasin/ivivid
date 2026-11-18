#include "MainWindow.hpp"
#include "Config.hpp"
#include <QApplication>
#include <QCoreApplication>
#include <QTextStream>
#include <QStringList>

int main(int argc, char **argv) {
    // Diagnostics work on headless Linux VMs and do not require a display server.
    QCoreApplication::setApplicationName("iVivid");
    QCoreApplication::setApplicationVersion("0.6.0-beta.1");
    const QStringList args = [&] {
        QStringList result;
        for (int i = 1; i < argc; ++i) result << QString::fromLocal8Bit(argv[i]);
        return result;
    }();
    if (args.contains("--version")) {
        QTextStream(stdout) << "iVivid 0.6.0-beta.1\n";
        return 0;
    }
    if (args.contains("--help")) {
        QTextStream(stdout) << "iVivid — Linux video and audio enhancement\n"
                            << "  --version        Print application version\n"
                            << "  --help           Show this help\n"
                            << "  --check-config   Validate saved iVivid mpv settings\n"
                            << "  --print-config   Print current effective mpv settings\n";
        return 0;
    }
    if (args.contains("--check-config") || args.contains("--print-config")) {
        ivivid::Settings settings;
        QString error;
        if (!ivivid::loadConfig(&settings, &error)) {
            QTextStream(stderr) << "iVivid config error: " << error << "\n";
            return 2;
        }
        if (args.contains("--print-config"))
            QTextStream(stdout) << ivivid::renderMpv(settings);
        else
            QTextStream(stdout) << "iVivid configuration valid\n";
        return 0;
    }
    QApplication app(argc, argv);
    app.setApplicationName("iVivid");
    app.setApplicationVersion("0.6.0-beta.1");
    app.setOrganizationName("iVivid Contributors");
    MainWindow window;
    window.show();
    return app.exec();
}
