#include "MainWindow.hpp"
#include <QApplication>
int main(int argc, char **argv) {
    QApplication app(argc, argv);
    app.setApplicationName("iVivid");
    app.setApplicationVersion("0.2.0-beta.1");
    app.setOrganizationName("iVivid Contributors");
    MainWindow window;
    window.show();
    return app.exec();
}
