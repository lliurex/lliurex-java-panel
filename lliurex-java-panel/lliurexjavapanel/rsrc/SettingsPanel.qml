import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


Rectangle{
    color:"transparent"
    Text{ 
        text:i18nd("lliurex-java-panel","Configuration options")
        font.family: "Quattrocento Sans Bold"
        font.pointSize: 16
    }

    GridLayout{
        id:generalSettingsLayout
        rows:1
        flow: GridLayout.TopToBottom
        rowSpacing:10
        anchors.left:parent.left
        width:parent.width-10
        height:parent.height-22

        enabled:true

        SettingsList{
            id:settingsList
            Layout.fillHeight:true
            Layout.fillWidth:true
            Layout.topMargin: 50
            configurationModel:settingsStackBridge.configurationModel
        }
    
    }
} 
