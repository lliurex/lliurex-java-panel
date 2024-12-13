import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import org.kde.plasma.components as PC
import org.kde.kirigami as Kirigami

GridLayout{
    id: optionsGrid
    columns: 2
    flow: GridLayout.LeftToRight
    columnSpacing:10

    Rectangle{
        width:130
        Layout.minimumHeight:460
        Layout.preferredHeight:460
        Layout.fillHeight:true
        border.color: "#d3d3d3"

        GridLayout{
            id: menuGrid
            rows:4 
            flow: GridLayout.TopToBottom
            rowSpacing:0

            MenuOptionBtn {
                id:packagesOption
                optionText:i18nd("epi-gtk","Home")
                optionIcon:"/usr/share/icons/breeze/places/22/user-home.svg"
                visible:true
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(0)
                        if (packageStackBridge.currentPkgOption==2){
                            packageStackBridge.showPkgInfo([1,""])
                        }
                    }
                }
            }
            /*
            MenuOptionBtn {
                id:detailsOption
                optionText:i18nd("epi-gtk","View details")
                optionIcon:"/usr/share/icons/breeze/apps/22/utilities-terminal.svg"
                visible:mainStackBridge.enableKonsole
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(1)
                    }
                }
            }
            */
            MenuOptionBtn {
                id:helpOption
                optionText:i18nd("epi-gtk","Help")
                optionIcon:"/usr/share/icons/breeze/actions/22/help-contents.svg"
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.openHelp()
                    }
                }
            }
        }
    }

    GridLayout{
        id: layoutGrid
        rows:3 
        flow: GridLayout.TopToBottom
        rowSpacing:0

        StackLayout {
            id: optionsLayout
            currentIndex:mainStackBridge.currentOptionsStack
            Layout.fillHeight:true
            Layout.fillWidth:true
            Layout.alignment:Qt.AlignHCenter

            JavasPanel{
                id:javasPanel
            }
            
        }

         Kirigami.InlineMessage {
            id: messageLabel
            visible:mainStackBridge.showStatusMessage[0]
            text:getFeedBackText(mainStackBridge.showStatusMessage[1])
            type:getMsgType()
            Layout.minimumWidth:555
            Layout.fillWidth:true
            Layout.rightMargin:10
            
        }

        RowLayout{
            id:feedbackRow
            spacing:10
            Layout.topMargin:10
            Layout.bottomMargin:10
            Layout.fillWidth:true

            ColumnLayout{
                id:feedbackColumn
                spacing:10
                Layout.alignment:Qt.AlignHCenter
                Text{
                    id:feedBackText
                    text:getFeedBackText(mainStackBridge.feedbackCode)
                    visible:true
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 10
                    horizontalAlignment:Text.AlignHCenter
                    Layout.preferredWidth:200
                    Layout.fillWidth:true
                    Layout.alignment:Qt.AlignHCenter
                    wrapMode: Text.WordWrap
                }
                
                ProgressBar{
                    id:feedBackBar
                    indeterminate:true
                    visible:mainStackBridge.isProgressBarVisible
                    implicitWidth:100
                    Layout.alignment:Qt.AlignHCenter
                }
                
            }
               
            PC.Button {
                id:installBtn
                visible:true
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-ok"
                text:i18nd("lliurex-java-panel","Install")
                enabled:{
                    if (mainStackBridge.enableApplyBtn){
                        true
                  }else{
                        false
                    }
                }
                Layout.preferredHeight:40
                Layout.leftMargin:10
                Layout.rightMargin:10
                Keys.onReturnPressed: installBtn.clicked()
                Keys.onEnterPressed: installBtn.clicked()
                onClicked:{}
            }
        }
    }
   
    Timer{
        id:timer
    }

    function delay(delayTime,cb){
        timer.interval=delayTime;
        timer.repeat=true;
        timer.triggered.connect(cb);
        timer.start()
    }
   
    /*
    function applyChanges(){
        delay(100, function() {
            if (mainStackBridge.endProcess){
                timer.stop()
                
            }else{
                if (mainStackBridge.endCurrentCommand){
                    mainStackBridge.getNewCommand()
                    var newCommand=mainStackBridge.currentCommand
                    konsolePanel.runCommand(newCommand)
                }
            }
          })
    } 
    */
    function getFeedBackText(code){

        var msg="";
        var errorHeaded=i18nd("epi-gtk","The selected applications cannot be uninstalled.\n")
        var warningHeaded=i18nd("epi-gtk","Some selected application successfully uninstalled.\nOthers not because ")
        switch (code){
            default:
                break;
        }
        return msg;
    }

    function getMsgType(){

        switch(mainStackBridge.showStatusMessage[2]){
            case "Ok":
                return Kirigami.MessageType.Positive;
            case "Error":
                return Kirigami.MessageType.Error;
            case "Info":
                return Kirigami.MessageType.Information;
            case "Warning":
                return Kirigami.MessageType.Warning;
        }
    }

}

