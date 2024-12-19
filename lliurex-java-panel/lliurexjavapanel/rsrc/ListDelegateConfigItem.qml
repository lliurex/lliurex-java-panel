import QtQuick
import QtQuick.Controls
import QtQml.Models
import org.kde.plasma.components as PC


PC.ItemDelegate{
	    id: listConfigItem
	    property string name
	    property string banner
	   
	    height:85
	    enabled:true
	      
	    Item{
		id: menuItem
		height:visible?80:0
		width:parent.width-25
		
		MouseArea {
			id: mouseAreaOption
			anchors.fill: parent
			hoverEnabled:true
			propagateComposedEvents:true
			
			onEntered: {
				listSettings.currentIndex=index
			}
		} 

		Image {
			id:packageIcon
			source:banner
			sourceSize.width:64
			sourceSize.height:64
			anchors.left:parent.left
			anchors.leftMargin:5
			anchors.verticalCenter:parent.verticalCenter
			cache:false
		} 

		Text{
			id: configName
			text: getConfigName(name)
			width:parent.width-configValues.width
			elide:Text.ElideMiddle
			clip: true
			font.family: "Quattrocento Sans Bold"
			font.pointSize: 10
			anchors.leftMargin:10
			anchors.left:packageIcon.right
			anchors.verticalCenter:parent.verticalCenter
		}

		ComboBox{
			id:configValues
            currentIndex:getCurrentValue(name)
            model:getModel(name)
            width:170
            anchors.leftMargin:10
			anchors.rightMargin:1.5
			anchors.right:parent.right
			anchors.verticalCenter:parent.verticalCenter
            onActivated:{
            	settingsStackBridge.manageAlternative([name,configValues.currentIndex])
            }
         } 
	}

	function getConfigName(configName){

		switch (configName){
			case "cpanel":
				var msg=i18nd("lliurex-java-panel","Java Control Panel. Select one tu run it")
				break;
			case "jws":
				var msg=i18nd("lliurex-java-panel","Java Web Start. Alternative configured:")
				break;
			case "jre":
				var msg=i18nd("lliurex-java-panel","Java Runtime Environment. Alternative configured:")
				break;
			case "firefox":
				var msg=i18nd("lliurex-java-panel","Firefox plugin. Alternative configured:")
				break;
		}

		return msg
	}

	function getCurrentValue(configName){

		switch(configName){
			case "cpanel":
				return 1
			case "jws":
				return settingsStackBridge.jwsCurrentAlternative
			case "jre":
				return settingsStackBridge.jreCurrentAlternative
			case "firefox":
				return settingsStackBridge.firefoxCurrentAlternative
		}
	}

	function getModel(configName){

		switch(configName){
			case "cpanel":
				return settingsStackBridge.cPanelModel
			case "jws":
				return settingsStackBridge.jwsModel
			case "jre":
				return settingsStackBridge.jreModel
			case "firefox":
				return settingsStackBridge.firefoxModel
		}

	}
}
