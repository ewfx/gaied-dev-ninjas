/** @format */

import React, { useState } from "react"
import "./email.css"
import Report from "./Report"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

async function apiCall(endpoint, method = "GET", body = null) {
	const options = {
		method,
		headers: {
			"Content-Type": "application/json",
		},
	}

	if (body) {
		options.body = body instanceof FormData ? body : JSON.stringify(body)
	}

	const response = await fetch(`${API_BASE_URL}${endpoint}`, options)

	if (!response.ok) {
		throw new Error("Network response was not ok")
	}

	const data = await response.json()
	return data
}

async function classifyEmail(selectedItems) {
	return apiCall("/email/classify", "POST", selectedItems)
}

export default function Email() {
	const [uploadedFile, setUploadedFile] = useState(null)
	const [emailData, setEmailData] = useState({
		body: "",
		attachments: [],
		subject: "",
		from: "",
		to: "",
	})
	const [isIntentSourceBody, setIsIntentSourceBody] = useState(false)
	const [loading, setLoading] = useState(false) // 🔹 Loading state
	const [message, setMessage] = useState("")
	const [selectedAttachments, setSelectedAttachments] = useState({})
	const [classificationResults, setClassificationResults] = useState(null)
	const [classificationInProgress, setClassificationInProgress] =
		useState(false)

	const handleFileChange = (event) => {
		setUploadedFile(event.target.files[0])
		setMessage("") // Clear message when selecting a new file
	}

	const handleUpload = (event) => {
		if (!uploadedFile) {
			setMessage("Please select a file before uploading.")
			return
		}
		if (!uploadedFile.name.toLowerCase().endsWith(".eml")) {
			setMessage("Only .eml files are allowed!")
			event.target.value = "" // Clear the input
			return
		}

		setLoading(true) // 🔹 Start loading
		setMessage("") // Clear previous messages

		const formData = new FormData()
		formData.append("file", uploadedFile)

		fetch(`${API_BASE_URL}/email/process`, {
			method: "POST",
			body: formData,
		})
			.then((response) => response.json())
			.then((parsedEmail) => {
				const data = parsedEmail?.data
				setEmailData({
					body: data?.body,
					attachments: data?.attachments,
					subject: data?.subject,
					from: data?.from,
					to: data?.to,
					id: data?.email_id,
				})
				setMessage("✅ Upload successful!") // 🔹 Success message
			})
			.catch((error) => {
				console.error("Error uploading file:", error)
				setMessage("❌ Upload failed. Please try again.") // 🔹 Error message
			})
			.finally(() => setLoading(false)) // 🔹 Stop loading
	}

	console.log({ selectedAttachments })

	const hasSelectedAttachments = Object.values(selectedAttachments).some(
		(value) => value
	)

	const category_type =
		isIntentSourceBody && !hasSelectedAttachments
			? "BODY"
			: isIntentSourceBody && hasSelectedAttachments
			? "BODYANDATTACHMENT"
			: !isIntentSourceBody && hasSelectedAttachments
			? "ATTACHMENT"
			: null

	const onProceedClick = () => {
		const selectedItems = {
			body: isIntentSourceBody ? emailData.body : null,
			category_type,
			email_id: emailData?.id,
			attachments: Object.keys(selectedAttachments)
				.filter((key) => selectedAttachments[key])
				.map((key) => emailData.attachments[key]),
		}
		console.log("Selected items:", selectedItems)
		setClassificationInProgress(true)
		classifyEmail(selectedItems)
			.then((data) => {
				setClassificationInProgress(false)
				setMessage("✅ Classification successful!")
				setClassificationResults(data)
			})
			.catch(() => {
				setMessage("❌ Classification failed. Please try again.")
				setClassificationInProgress(false)
			})
	}

	// Handle checkbox change for attachments
	const handleAttachmentCheckbox = (index) => {
		setSelectedAttachments((prev) => ({
			...prev,
			[index]: !prev[index],
		}))
	}

	// Check if any checkbox is selected
	const isAnyCheckboxSelected =
		isIntentSourceBody || Object.values(selectedAttachments).includes(true)

	return (
		<div className="container">
			<h1>Email Classification</h1>
			<input type="file" onChange={handleFileChange} accept=".eml" />
			<button onClick={handleUpload} disabled={loading}>
				{loading ? "Uploading..." : "Upload"}
			</button>
			{message && <p className="status-message">{message}</p>}{" "}
			{/* 🔹 Show status message */}
			{(loading || classificationInProgress) && (
				<div className="overlay">
					<div className="spinner"></div>
				</div>
			)}
			{classificationResults ? (
				<Report data={classificationResults?.data} />
			) : (
				<React.Fragment>
					{emailData.subject && (
						<>
							<label>Subject</label>
							<input type="text" value={emailData.subject} readOnly />
						</>
					)}

					{emailData.from && (
						<>
							<label>From</label>
							<input type="text" value={emailData.from} readOnly />
						</>
					)}

					{emailData.to && (
						<>
							<label>To</label>
							<input type="text" value={emailData.to} readOnly />
						</>
					)}

					{emailData.body && (
						<>
							<label>Body</label>
							<textarea value={emailData.body} readOnly rows="10" />
							<div className="checkbox-container">
								<input
									type="checkbox"
									id="select-body"
									checked={isIntentSourceBody}
									onChange={() => setIsIntentSourceBody(!isIntentSourceBody)}
								/>
								<label htmlFor="select-body">Select body</label>
							</div>
						</>
					)}

					{emailData.attachments?.length > 0 && (
						<div className="attachments">
							<label>Attachments</label>
							{emailData.attachments.map((attachment, index) => (
								<div key={index} className="attachment-item">
									<div className="attachment-header">
										<input
											type="checkbox"
											id={`attach-${index}`}
											checked={!!selectedAttachments[index]}
											onChange={() => handleAttachmentCheckbox(index)}
										/>
										<label htmlFor={`attach-${index}`}>
											{attachment?.filename}
										</label>
									</div>
									<textarea
										className="attachment-textarea"
										value={attachment?.extracted_text}
										readOnly
										rows="5"
									></textarea>
								</div>
							))}
						</div>
					)}
					{isAnyCheckboxSelected && (
						<button onClick={onProceedClick}>Proceed For Classification</button>
					)}
				</React.Fragment>
			)}
		</div>
	)
}
