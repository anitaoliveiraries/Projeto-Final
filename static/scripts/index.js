const fileInput = document.getElementById("csv-file");
const dropzone = document.getElementById("dropzone");
const fileDetails = document.getElementById("file-details");
const fileName = document.getElementById("file-name");
const fileSize = document.getElementById("file-size");
const errorMessage = document.getElementById("error-message");
const removeButton = document.getElementById("remove-file");
const uploadForm = document.getElementById("upload-form");
const confirmButton = document.getElementById("confirm-upload");

function formatFileSize(bytes) {
    if (bytes < 1024) return `${bytes} bytes`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function showFile(file) {
    const isCsv = file && (file.name.toLowerCase().endsWith(".csv") || file.type === "text/csv");
    if (!isCsv) {
        fileInput.value = "";
        fileDetails.classList.add("d-none");
        confirmButton.disabled = true;
        errorMessage.textContent = "Please choose a file in CSV format.";
        errorMessage.classList.remove("d-none");
        return;
    }

    errorMessage.textContent = "";
    errorMessage.classList.add("d-none");
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileDetails.classList.remove("d-none");
    fileDetails.classList.add("d-flex");
    confirmButton.disabled = false;
}

fileInput.addEventListener("change", () => {
    if (fileInput.files.length) showFile(fileInput.files[0]);
});

removeButton.addEventListener("click", () => {
    fileInput.value = "";
    fileDetails.classList.add("d-none");
    fileDetails.classList.remove("d-flex");
    confirmButton.disabled = true;
    errorMessage.textContent = "";
    errorMessage.classList.add("d-none");
    fileInput.focus();
});

dropzone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropzone.classList.add("is-dragging");
});

dropzone.addEventListener("dragleave", (event) => {
    if (!dropzone.contains(event.relatedTarget)) dropzone.classList.remove("is-dragging");
});

dropzone.addEventListener("drop", (event) => {
    event.preventDefault();
    dropzone.classList.remove("is-dragging");
    const [file] = event.dataTransfer.files;
    if (file) {
        const transfer = new DataTransfer();
        transfer.items.add(file);
        fileInput.files = transfer.files;
        showFile(file);
    }
});

uploadForm.addEventListener("submit", (event) => {
    if (!fileInput.files.length) {
        event.preventDefault();
        errorMessage.textContent = "Selecione um arquivo CSV antes de confirmar o envio.";
        errorMessage.classList.remove("d-none");
    }
});