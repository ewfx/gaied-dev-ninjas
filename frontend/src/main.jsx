/** @format */

import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import "./email.css"
import Email from "./Email.jsx"

createRoot(document.getElementById("root")).render(
	<StrictMode>
		<Email />
	</StrictMode>
)
