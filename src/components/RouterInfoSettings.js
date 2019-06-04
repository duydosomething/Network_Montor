import React from "react";
import { Tab } from "semantic-ui-react";
import RouterInfo from "./RouterInfo";
import Settings from "./Settings";

class RouterInfoSettings extends React.Component {
	render() {
		const panes = [
			{
				menuItem: "Router Info",
				pane: { content: <RouterInfo /> }
			},
			{
				menuItem: "Settings",
				pane: { content: <Settings /> }
			}
		];
		return <Tab renderActiveOnly={false} panes={panes} />;
	}
}

export default RouterInfoSettings;
