/** @format */

import React from "react"

const Report = ({ data }) => {
	if (!data) {
		return null
	}

  const formatText = (text) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\* (.*?)(\n|$)/g, "<li>$1</li>")
      .replace(/\n/g, "<br/>")
  }

  return (
    <div>
      <h2>Report</h2>
      <div
        style={{ whiteSpace: "pre-wrap", textAlign: "justify" }}
        dangerouslySetInnerHTML={{ __html: formatText(data) }}
      ></div>
    </div>
  )
}

export default Report
