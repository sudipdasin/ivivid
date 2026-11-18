#pragma once
#include <QMainWindow>
#include "Config.hpp"
class QComboBox;
class QSlider;
class QCheckBox;
class QLabel;
class MainWindow : public QMainWindow {
public:
    explicit MainWindow(QWidget *parent = nullptr);
private:
    QComboBox *preset_;
    QSlider *saturation_, *brightness_, *contrast_, *bass_, *treble_;
    QCheckBox *hardware_, *deband_, *normalize_;
    QLabel *status_;
    ivivid::Settings settings() const;
};
