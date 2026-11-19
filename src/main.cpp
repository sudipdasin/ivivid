#include "MainWindow.hpp"
#include "Config.hpp"
#include <QApplication>
#include <QCoreApplication>
#include <QFile>
#include <QSaveFile>
#include <QFileInfo>
#include <QDir>
#include <QTextStream>
#include <QStringList>

static bool sameConfigFile(const QString &candidate) {
    const QFileInfo source(candidate);
    const QFileInfo active(ivivid::configPath());
    if (source.absoluteFilePath() == active.absoluteFilePath()) return true;
    const QString canonicalSource = source.canonicalFilePath();
    const QString canonicalActive = active.canonicalFilePath();
    return !canonicalSource.isEmpty() && !canonicalActive.isEmpty() &&
           canonicalSource == canonicalActive;
}

int main(int argc, char **argv) {
    // Diagnostics work on headless Linux VMs and do not require a display server.
    QCoreApplication::setApplicationName("iVivid");
    QCoreApplication::setApplicationVersion("1.1.5-beta.1");
    const QStringList args = [&] {
        QStringList result;
        for (int i = 1; i < argc; ++i) result << QString::fromLocal8Bit(argv[i]);
        return result;
    }();
    if (args.contains("--version")) {
        QTextStream(stdout) << "iVivid 1.1.5-beta.1\n";
        return 0;
    }
    if (args.contains("--help")) {
        QTextStream(stdout) << "iVivid — Linux video and audio enhancement\n"
                            << "  --version        Print application version\n"
                            << "  --help           Show this help\n"
                            << "  --check-config   Validate saved iVivid mpv settings\n"
                            << "  --print-config   Print current effective mpv settings\n"
                            << "  --export-config FILE  Export effective settings atomically\n"
                            << "  --import-config FILE  Validate and atomically import settings\n";
        return 0;
    }
    const int importIndex = args.indexOf("--import-config");
    if (importIndex >= 0) {
        if (args.size() != 2 || importIndex != 0 || args.at(1).startsWith("--")) {
            QTextStream(stderr) << "iVivid: --import-config requires exactly one file path\n";
            return 2;
        }
        const QString source = args.at(1);
        if (sameConfigFile(source)) {
            QTextStream(stderr) << "iVivid: cannot import active settings onto themselves\n";
            return 2;
        }
        ivivid::Settings imported;
        QString error;
        if (!ivivid::loadConfigFile(source, &imported, &error) ||
            !ivivid::applyConfig(imported, &error)) {
            QTextStream(stderr) << "iVivid import error: " << error << "\n";
            return 2;
        }
        QTextStream(stdout) << "Imported iVivid settings\n";
        return 0;
    }
    const int exportIndex = args.indexOf("--export-config");
    if (exportIndex >= 0 && (exportIndex + 1 >= args.size() || args.at(exportIndex + 1).startsWith("--"))) {
        QTextStream(stderr) << "iVivid: --export-config requires a file path\n";
        return 2;
    }
    if (args.contains("--check-config") || args.contains("--print-config") || exportIndex >= 0) {
        ivivid::Settings settings;
        QString error;
        if (!ivivid::loadConfig(&settings, &error)) {
            QTextStream(stderr) << "iVivid config error: " << error << "\n";
            return 2;
        }
        if (exportIndex >= 0) {
            const QString path = args.at(exportIndex + 1);
            if (sameConfigFile(path)) {
                QTextStream(stderr) << "iVivid: export destination cannot overwrite active settings\n";
                return 2;
            }
            QSaveFile file(path);
            const QByteArray bytes = ivivid::renderMpv(settings).toUtf8();
            if (!file.open(QIODevice::WriteOnly | QIODevice::Text) ||
                file.write(bytes) != bytes.size() || !file.commit()) {
                QTextStream(stderr) << "iVivid export error: " << file.errorString() << "\n";
                return 2;
            }
            QTextStream(stdout) << "Exported iVivid settings to " << path << "\n";
            return 0;
        }
        if (args.contains("--print-config"))
            QTextStream(stdout) << ivivid::renderMpv(settings);
        else
            QTextStream(stdout) << "iVivid configuration valid\n";
        return 0;
    }
    QApplication app(argc, argv);
    app.setApplicationName("iVivid");
    app.setApplicationVersion("1.1.5-beta.1");
    app.setOrganizationName("iVivid Contributors");
    MainWindow window;
    window.show();
    return app.exec();
}
