import QtQuick
import QtQuick.Controls
import QtQml.Models 2.8
import org.kde.plasma.components as PC
import org.kde.kirigami as Kirigami
import QtQuick.Layouts


Rectangle{
    property alias javasModel:filterModel.model
    property alias listCount:listPkg.count
    id: optionsGrid
    color:"transparent"

    GridLayout{
        id:mainGrid
        rows:3
        flow: GridLayout.TopToBottom
        rowSpacing:10
        anchors.left:parent.left
        anchors.fill:parent
        RowLayout{
            Layout.alignment:Qt.AlignRight
            spacing:10
            Layout.topMargin:40
            PC.Button{
                id:statusFilterBtn
                display:AbstractButton.IconOnly
                icon.name:"view-filter"
                visible:true
                enabled:{
                    if (javaStackBridge.totalErrorInProcess==0){
                        if (javaStackBridge.enableJavaList){
                            if (javaStackBridge.isAllInstalled[0] || javaStackBridge.isAllInstalled[1]){
                                false
                            }else{
                                true
                            }
                        }else{
                            false
                        }
                    }else{
                        true
                    }
                }
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-java-panel","Click to filter java by status")
                onClicked:optionsMenu.open();
               
                PC.Menu{
                    id:optionsMenu
                    y: statusFilterBtn.height
                    x:-(optionsMenu.width-statusFilterBtn.width/2)

                    PC.MenuItem{
                        icon.name:"installed"
                        text:i18nd("lliurex-java-panel","Show installed Java")
                        enabled:{
                            if (javaStackBridge.filterStatusValue!="installed"){
                                true
                            }else{
                                false
                            }
                        }
                        onClicked:javaStackBridge.manageStatusFilter("installed")
                    }

                    PC.MenuItem{
                        icon.name:"noninstalled"
                        text:i18nd("lliurex-java-panel","Show uninstalled Java")
                        enabled:{
                            if (javaStackBridge.filterStatusValue!="available"){
                                true
                            }else{
                                false
                            }
                        }
                        onClicked:javaStackBridge.manageStatusFilter("available")
                    }
                    PC.MenuItem{
                        icon.name:"emblem-error"
                        text:i18nd("lliurex-java-panel","Show Java with error")
                        enabled:{
                            if (javaStackBridge.filterStatusValue!="error"){
                                if (javaStackBridge.totalErrorInProcess>0){
                                    true
                                }else{
                                    false
                                }
                            }else{
                                false
                            }
                        }
                        onClicked:javaStackBridge.manageStatusFilter("error")
                    }
                    PC.MenuItem{
                        icon.name:"kt-remove-filters"
                        text:i18nd("lliurex-java-panel","Remove filter")
                        enabled:{
                            if (javaStackBridge.filterStatusValue!="all"){
                                true
                            }else{
                                false
                            }
                        }
                        onClicked:javaStackBridge.manageStatusFilter("all")
                    }
                }
            }
                
            PC.TextField{
                id:pkgSearchEntry
                font.pointSize:10
                horizontalAlignment:TextInput.AlignLeft
                Layout.alignment:Qt.AlignRight
                focus:true
                width:100
                visible:true
                enabled:javaStackBridge.enableJavaList
                placeholderText:i18nd("lliurex-java-panel","Search...")
                onTextChanged:{
                    filterModel.update()
                }
            }
        }

        Rectangle {
            id:pkgTable
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
                    id: listPkg
                    property int totalItems
                    anchors.fill:parent
                    height: parent.height
                    enabled:javaStackBridge.enableJavaList
                    currentIndex:-1
                    clip: true
                    focus:true
                    boundsBehavior: Flickable.StopAtBounds
                    highlight: Rectangle { color: "#add8e6"; opacity:0.8;border.color:"#53a1c9" }
                    highlightMoveDuration: 0
                    highlightResizeDuration: 0
                    model:FilterDelegateModel{
                        id:filterModel
                        model:javasModel
                        role:"name"
                        search:pkgSearchEntry.text.trim()
                        statusFilter:javaStackBridge.filterStatusValue
                        
                        delegate: ListDelegatePkgItem{
                            width:pkgTable.width
                            pkg:model.pkg
                            isChecked:model.isChecked
                            name:model.name
                            banner:model.banner
                            status:model.status
                            isVisible:model.isVisible
                            resultProcess:model.resultProcess
                            showSpinner:model.showSpinner
                            isManaged:model.isManaged
                        }
                    }

                    Kirigami.PlaceholderMessage { 
                        id: emptyHint
                        anchors.centerIn: parent
                        width: parent.width - (Kirigami.Units.largeSpacing * 4)
                        visible: listPkg.count==0?true:false
                        text: i18nd("lliurex-java-panel","Java versions not available")
                    }

                 } 
            }
        }
        RowLayout{
            Layout.fillWidth:true

            PC.Button {
                id:selectBtn
                visible:true
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:{
                    if (javaStackBridge.uncheckAll){
                        "list-remove"
                    }else{
                        "list-add"
                    }
                }
                text:{
                    if (javaStackBridge.uncheckAll){
                        i18nd("lliurex-java-panel","Uncheck all")
                    }else{
                        i18nd("lliurex-java-panel","Check all")
                    }
                }
                enabled:javaStackBridge.enableJavaList
                Layout.preferredHeight:40
                Layout.rightMargin:10
                Keys.onReturnPressed: selectBtn.clicked()
                Keys.onEnterPressed: selectBtn.clicked()
                onClicked:{
                    javaStackBridge.selectAll()
                }
            }

        }      
    }

}
