
// Onboarding / Home Page Upload
async function homeUpload() {
    const fileInput = document.getElementById('homeUploadFile');
    const uploadBtn = document.getElementById('btnUploadHome');
    const statusDiv = document.getElementById('uploadStatus');
    const warningsDiv = document.getElementById('uploadWarnings');

    if (!fileInput.files[0]) {
        alert("Please select a file first!");
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    uploadBtn.disabled = true;
    uploadBtn.textContent = "Analyzing...";
    statusDiv.textContent = "";
    statusDiv.className = "";
    warningsDiv.textContent = "";

    try {
        const response = await fetch('/api/upload_inventory', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (response.ok && result.status === 'success') {
            statusDiv.textContent = "✅ Success! " + result.message;
            statusDiv.style.color = "green";

            // Show warnings if any
            if (result.warnings && result.warnings.length > 0) {
                warningsDiv.textContent = "⚠️ Note: " + result.warnings.join("\n");
            }

            // Redirect after short delay
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            statusDiv.textContent = "❌ Error: " + (result.error || "Upload failed");
            statusDiv.style.color = "#e74c3c";
            if (result.missing_columns) {
                warningsDiv.textContent = "Missing mandatory columns: " + result.missing_columns.join(", ");
            }
            uploadBtn.disabled = false;
            uploadBtn.textContent = "Analyze My Store";
        }
    } catch (e) {
        statusDiv.textContent = "❌ Network Error: " + e.message;
        statusDiv.style.color = "#e74c3c";
        uploadBtn.disabled = false;
        uploadBtn.textContent = "Analyze My Store";
    }
}
