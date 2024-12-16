import QtQuick
import QtQuick.Controls
import QtQml.Models 2.8
import org.kde.plasma.components as PC
import org.kde.kirigami as Kirigami
import QtQuick.Layouts


Rectangle{
    property alias configurationModel:listSettings.model
    property alias listCount:listSettings.count
    id: optionsGrid
    color:"transparent"

    GridLayout{
        id:mainGrid
        rows:1
        flow: GridLayout.TopToBottom
        rowSpacing:10
        anchors.left:parent.left
        anchors.fill:parent
  
        Rectangle {
            id:settingsTable
            visible: true
            color:"white"
            Layout.fillHeight:true
            Layout.fillWidth:true
            Layout.topMargin:0
       
            border.color: "#d3d3d3"

            PC.ScrollView{
                implicitWidth:parent.width
                implicitHeight:parent.height
                anchors.leftMargin:10
       
                ListView{
                    id: listSettings
                    property int totalItems
                    anchors.fill:parent
                    height: parent.height
                    enabled:true
                    currentIndex:-1
                    clip: true
                    focus:true
                    boundsBehavior: Flickable.StopAtBounds
                    highlight: Rectangle { color: "#add8e6"; opacity:0.8;border.color:"#53a1c9" }
                    highlightMoveDuration: 0
                    highlightResizeDuration: 0
                    model:configurationModel
                    delegate: ListDelegateConfigItem{
                        width:settingsTable.width
                        name:model.id
                        banner:model.banner
     
                    }

                    Kirigami.PlaceholderMessage { 
                        id: emptyHint
                        anchors.centerIn: parent
                        width: parent.width - (Kirigami.Units.largeSpacing * 4)
                        visible: listSettings.count==0?true:false
                        text: i18nd("lliurex-java-panel","Configuration options not found")
                    }

                 } 
            }
        }
           
    }

}