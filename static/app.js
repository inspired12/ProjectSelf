// API base URL
const API_BASE = '';

// State management
let currentQuestion = null;
let mediaRecorder = null;
let audioChunks = [];
let recordingStartTime = null;
let recordingTimer = null;
let listenersBound = false;

// DOM elements
const loadingState = document.getElementById('loading-state');
const questionState = document.getElementById('question-state');
const completeState = document.getElementById('complete-state');
const errorState = document.getElementById('error-state');
const processingState = document.getElementById('processing-state');

const questionNumber = document.getElementById('question-number');
const questionText = document.getElementById('question-text');
const categoryBadge = document.getElementById('category-badge');
const progressText = document.getElementById('progress-text');
const completionText = document.getElementById('completion-text');

const recordBtn = document.getElementById('record-btn');
const recordingIndicator = document.getElementById('recording-indicator');
const recordingTime = document.getElementById('recording-time');
const transcriptionSection = document.getElementById('transcription-section');
const transcriptionText = document.getElementById('transcription-text');
const retryBtn = document.getElementById('retry-btn');
const nextBtn = document.getElementById('next-btn');

const importModal = document.getElementById('import-modal');
const responsesModal = document.getElementById('responses-modal');
const importLink = document.getElementById('import-link');
const viewAllLink = document.getElementById('view-all-link');
const questionsInput = document.getElementById('questions-input');
const importSubmitBtn = document.getElementById('import-submit-btn');
const responsesList = document.getElementById('responses-list');

// Initialize the app
async function init() {
    showState('loading');
    await loadCurrentQuestion();
    updateStats();

    if (listenersBound) {
        return;
    }

    // Set up event listeners once
    recordBtn.addEventListener('click', toggleRecording);
    retryBtn.addEventListener('click', retryRecording);
    nextBtn.addEventListener('click', moveToNextQuestion);
    importLink.addEventListener('click', (e) => {
        e.preventDefault();
        openModal(importModal);
    });
    viewAllLink.addEventListener('click', (e) => {
        e.preventDefault();
        viewAllResponses();
    });
    document.getElementById('view-responses-btn').addEventListener('click', viewAllResponses);
    document.getElementById('restart-btn').addEventListener('click', restartProgress);
    document.getElementById('retry-load-btn').addEventListener('click', () => {
        loadCurrentQuestion();
        updateStats();
    });
    importSubmitBtn.addEventListener('click', importQuestions);

    // Modal close buttons
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', () => {
            closeBtn.closest('.modal').style.display = 'none';
        });
    });

    // Close modal on outside click
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });

    listenersBound = true;
}

// Show specific state
function showState(state) {
    loadingState.style.display = 'none';
    questionState.style.display = 'none';
    completeState.style.display = 'none';
    errorState.style.display = 'none';

    switch(state) {
        case 'loading':
            loadingState.style.display = 'block';
            break;
        case 'question':
            questionState.style.display = 'block';
            break;
        case 'complete':
            completeState.style.display = 'block';
            break;
        case 'error':
            errorState.style.display = 'block';
            break;
    }
}

// Load current question
async function loadCurrentQuestion() {
    try {
        const response = await fetch(`${API_BASE}/api/current-question`);
        const data = await response.json();

        if (data.success && data.question) {
            currentQuestion = data.question;
            displayQuestion(data.question);
            showState('question');
        } else {
            // No more questions
            await updateStats();
            showState('complete');
        }
    } catch (error) {
        console.error('Error loading question:', error);
        showError('Failed to load question. Please check if the server is running.');
    }
}

// Display question
function displayQuestion(question) {
    questionNumber.textContent = `Question ${question.current_index + 1} of ${question.total_questions}`;
    questionText.textContent = question.question_text;
    categoryBadge.textContent = question.category || 'General';

    // Reset recording UI
    recordBtn.disabled = false;
    recordBtn.classList.remove('recording');
    recordBtn.innerHTML = '<span class="btn-icon">🎙️</span> Start Recording';
    recordingIndicator.style.display = 'none';
    transcriptionSection.style.display = 'none';
    processingState.style.display = 'none';
}

// Toggle recording
async function toggleRecording() {
    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        await startRecording();
    } else {
        stopRecording();
    }
}

// Start recording
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            await transcribeAudio(audioBlob);

            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();

        // Update UI
        recordBtn.innerHTML = '<span class="btn-icon">⏹️</span> Stop Recording';
        recordBtn.classList.add('recording');
        recordingIndicator.style.display = 'inline-flex';

        // Start timer
        recordingStartTime = Date.now();
        recordingTimer = setInterval(updateRecordingTime, 100);

    } catch (error) {
        console.error('Error starting recording:', error);
        alert('Could not access microphone. Please grant microphone permissions.');
    }
}

// Stop recording
function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        clearInterval(recordingTimer);

        recordBtn.disabled = true;
        recordingIndicator.style.display = 'none';
    }
}

// Update recording time display
function updateRecordingTime() {
    const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    recordingTime.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

// Transcribe audio
async function transcribeAudio(audioBlob) {
    processingState.style.display = 'block';

    try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        formData.append('question_id', currentQuestion.id);

        const response = await fetch(`${API_BASE}/api/transcribe`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        processingState.style.display = 'none';

        if (data.success) {
            displayTranscription(data.transcription);
        } else {
            alert('Transcription failed: ' + (data.error || 'Unknown error'));
            resetRecordingUI();
        }
    } catch (error) {
        console.error('Error transcribing:', error);
        processingState.style.display = 'none';
        alert('Failed to transcribe audio. Please try again.');
        resetRecordingUI();
    }
}

// Display transcription
function displayTranscription(text) {
    transcriptionText.textContent = text;
    transcriptionSection.style.display = 'block';
}

// Reset recording UI
function resetRecordingUI() {
    recordBtn.disabled = false;
    recordBtn.classList.remove('recording');
    recordBtn.innerHTML = '<span class="btn-icon">🎙️</span> Start Recording';
    recordingIndicator.style.display = 'none';
    transcriptionSection.style.display = 'none';
}

// Retry recording
function retryRecording() {
    resetRecordingUI();
}

// Move to next question
async function moveToNextQuestion() {
    try {
        await fetch(`${API_BASE}/api/next-question`, {
            method: 'POST'
        });

        await loadCurrentQuestion();
        await updateStats();
    } catch (error) {
        console.error('Error moving to next question:', error);
        alert('Failed to move to next question.');
    }
}

// Update statistics
async function updateStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const data = await response.json();

        if (data.success) {
            const stats = data.stats;
            progressText.textContent = `${stats.total_responses} / ${stats.total_questions}`;
            completionText.textContent = `${Math.round(stats.completion_percentage)}%`;

            if (completeState.style.display === 'block') {
                document.getElementById('total-responses').textContent = stats.total_responses;
            }
        }
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Import questions
async function importQuestions() {
    try {
        const questionsText = questionsInput.value.trim();
        if (!questionsText) {
            alert('Please enter questions in JSON format.');
            return;
        }

        const questions = JSON.parse(questionsText);

        const response = await fetch(`${API_BASE}/api/import-questions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ questions })
        });

        const data = await response.json();

        if (data.success) {
            alert(data.message);
            importModal.style.display = 'none';
            questionsInput.value = '';
            await loadCurrentQuestion();
            await updateStats();
        } else {
            alert('Import failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error importing questions:', error);
        alert('Failed to import questions. Please check the JSON format.');
    }
}

// View all responses
async function viewAllResponses() {
    try {
        const response = await fetch(`${API_BASE}/api/responses`);
        const data = await response.json();

        if (data.success) {
            displayResponses(data.responses);
            openModal(responsesModal);
        }
    } catch (error) {
        console.error('Error loading responses:', error);
        alert('Failed to load responses.');
    }
}

// Display responses in modal
function displayResponses(responses) {
    if (responses.length === 0) {
        responsesList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No responses yet.</p>';
        return;
    }

    responsesList.innerHTML = responses.map(r => `
        <div class="response-item">
            <h4>${r.question_text}</h4>
            <p>${r.transcription}</p>
            <div class="meta">
                <span>${r.category || 'General'}</span> •
                <span>${new Date(r.created_at).toLocaleString()}</span>
            </div>
        </div>
    `).join('');
}

// Restart progress
async function restartProgress() {
    if (confirm('Are you sure you want to restart from the beginning? This will not delete your responses.')) {
        try {
            await fetch(`${API_BASE}/api/reset-progress`, {
                method: 'POST'
            });

            await loadCurrentQuestion();
            await updateStats();
        } catch (error) {
            console.error('Error restarting:', error);
            alert('Failed to restart progress.');
        }
    }
}

// Show error
function showError(message) {
    document.getElementById('error-message').textContent = message;
    showState('error');
}

// Open modal
function openModal(modal) {
    modal.style.display = 'block';
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
