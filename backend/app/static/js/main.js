// Global Utility: Toast Notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) {
        const c = document.createElement('div');
        c.id = 'toast-container';
        document.body.appendChild(c);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let borderStyle = '';
    if (type === 'success') borderStyle = 'var(--color-success)';
    else if (type === 'error') borderStyle = 'var(--color-error)';
    else borderStyle = 'var(--color-blue)';
    
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-weight: 600;">${message}</span>
        </div>
        <button class="modal-close" style="font-size: 1rem; border: none; background: none; cursor: pointer; color: white;" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    document.getElementById('toast-container').appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Simple Markdown Formatter Helper
function formatMarkdown(text) {
    if (!text) return '';
    let formatted = text
        .replace(/### (.*?)\n/g, '<h4 style="margin: 14px 0 8px 0; color: var(--color-primary); font-family: var(--font-heading);">$1</h4>')
        .replace(/## (.*?)\n/g, '<h3 style="margin: 18px 0 10px 0; color: white; font-family: var(--font-heading);">$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code style="background: rgba(255,255,255,0.08); padding: 2px 6px; border-radius: 4px; font-family: monospace;">$1</code>')
        .replace(/\n\n/g, '<p style="margin-bottom: 12px;"></p>')
        .replace(/\n- (.*?)\n/g, '<li style="margin-left: 20px; margin-bottom: 6px;">$1</li>')
        .replace(/\n\* (.*?)\n/g, '<li style="margin-left: 20px; margin-bottom: 6px;">$1</li>');
        
    // Wrap lists if they exist
    if (formatted.includes('<li>')) {
        formatted = formatted.replace(/(<li>.*?<\/li>)/g, '<ul style="margin-bottom: 16px;">$1</ul>');
    }
    
    return formatted;
}

// Show/Hide Loading Indicator
function toggleLoader(cardId, show, placeholderText = "Processing request...") {
    const card = document.getElementById(cardId);
    if (!card) return;
    
    if (show) {
        card.setAttribute('data-original-content', card.innerHTML);
        card.innerHTML = `
            <div class="output-placeholder">
                <div class="spinner" style="width: 48px; height: 48px; margin-bottom: 16px;"></div>
                <h4 style="font-weight: 500; font-family: var(--font-heading);">${placeholderText}</h4>
                <p style="font-size: 0.85rem; color: var(--color-text-muted); margin-top: 4px;">Google Gemini is formulating your educational resources.</p>
            </div>
        `;
    } else {
        const originalContent = card.getAttribute('data-original-content');
        if (originalContent) {
            card.innerHTML = originalContent;
        }
    }
}

// =====================================================================
// FRONTEND ROUTE HANDLERS
// =====================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Determine active page based on window pathname
    const path = window.location.pathname;
    
    // Set Sidebar Active State
    const menuLinks = document.querySelectorAll('.sidebar-menu a');
    menuLinks.forEach(link => {
        if (link.getAttribute('href') === path) {
            link.parentElement.classList.add('active');
        } else {
            link.parentElement.classList.remove('active');
        }
    });
    
    if (path === '/login') initLoginPage();
    else if (path === '/signup') initSignupPage();
    else if (path === '/dashboard') initDashboardPage();
    else if (path === '/qa') initQAPage();
    else if (path === '/explain') initExplainPage();
    else if (path === '/quiz') initQuizPage();
    else if (path === '/summary') initSummaryPage();
    else if (path === '/roadmap') initRoadmapPage();
    else if (path === '/history') initHistoryPage();
    else if (path === '/profile') initProfilePage();
});

// =====================================================================
// AUTHENTICATION LOGIN & SIGNUP
// =====================================================================
function initLoginPage() {
    const form = document.getElementById('login-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        
        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ Email: email, Password: password })
            });
            
            const data = await res.json();
            if (res.ok) {
                showToast("Login successful!", "success");
                window.location.href = '/dashboard';
            } else {
                showToast(data.detail || "Authentication failed.", "error");
            }
        } catch (err) {
            showToast("Network error occurred.", "error");
        }
    });
}

function initSignupPage() {
    const form = document.getElementById('signup-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        
        if (password !== confirmPassword) {
            showToast("Passwords do not match.", "error");
            return;
        }
        
        try {
            const res = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ UserName: username, Email: email, Password: password })
            });
            
            const data = await res.json();
            if (res.ok) {
                showToast("Account created! Please log in.", "success");
                setTimeout(() => { window.location.href = '/login'; }, 1500);
            } else {
                showToast(data.detail || "Sign up failed.", "error");
            }
        } catch (err) {
            showToast("Network error occurred.", "error");
        }
    });
}

// =====================================================================
// DASHBOARD
// =====================================================================
async function initDashboardPage() {
    try {
        const res = await fetch('/api/history/dashboard/stats');
        if (!res.ok) return;
        const data = await res.json();
        
        // Populate counts
        document.getElementById('total-queries').innerText = data.total_queries;
        document.getElementById('qa-count').innerText = data.queries_by_type.qa || 0;
        document.getElementById('quiz-count').innerText = data.queries_by_type.quiz || 0;
        document.getElementById('roadmap-count').innerText = data.queries_by_type.learn || 0;
        
        // Populate recent activity
        const activityList = document.getElementById('recent-activity-list');
        if (activityList) {
            if (data.recent_activity.length === 0) {
                activityList.innerHTML = `<li style="padding: 12px; color: var(--color-text-muted);">No recent activities yet. Start learning!</li>`;
            } else {
                activityList.innerHTML = data.recent_activity.map(item => `
                    <li style="padding: 16px; border-bottom: 1px solid var(--glass-border); display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span class="badge" style="text-transform: uppercase; font-size: 0.65rem;">${item.QueryType}</span>
                            <span style="font-weight: 500; margin-left: 10px;">${item.QueryText.substring(0, 40)}...</span>
                        </div>
                        <span style="font-size: 0.8rem; color: var(--color-text-muted);">${new Date(item.CreatedAt).toLocaleDateString()}</span>
                    </li>
                `).join('');
            }
        }
        
        // Draw Chart.js Visualization
        const ctx = document.getElementById('usageChart');
        if (ctx && typeof Chart !== 'undefined') {
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Q&A', 'Concept Explanations', 'Quizzes', 'Summaries', 'Roadmaps'],
                    datasets: [{
                        label: 'Interactions',
                        data: [
                            data.queries_by_type.qa || 0,
                            data.queries_by_type.explain || 0,
                            data.queries_by_type.quiz || 0,
                            data.queries_by_type.summarize || 0,
                            data.queries_by_type.learn || 0
                        ],
                        backgroundColor: [
                            'rgba(108, 99, 255, 0.6)',
                            'rgba(79, 70, 229, 0.6)',
                            'rgba(139, 92, 246, 0.6)',
                            'rgba(59, 130, 246, 0.6)',
                            'rgba(16, 185, 129, 0.6)'
                        ],
                        borderColor: [
                            '#6C63FF', '#4F46E5', '#8B5CF6', '#3B82F6', '#10B981'
                        ],
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            ticks: { color: '#9CA3AF' }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { color: '#9CA3AF' }
                        }
                    }
                }
            });
        }
    } catch (err) {
        console.error("Dashboard data load failed: ", err);
    }
}

// =====================================================================
// MODULE: Q&A
// =====================================================================
function initQAPage() {
    const form = document.getElementById('qa-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = document.getElementById('question-input').value.trim();
        if (!question) return;
        
        toggleLoader('qa-output-card', true, "Finding the answer...");
        
        try {
            const res = await fetch('/api/modules/qa', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ Question: question })
            });
            
            const data = await res.json();
            toggleLoader('qa-output-card', false);
            
            if (res.ok) {
                const output = document.getElementById('qa-output-card');
                output.innerHTML = `
                    <div class="output-header">
                        <h3 class="page-title" style="font-size: 1.25rem;">Answer</h3>
                        <span class="badge">Gemini 1.5 Pro</span>
                    </div>
                    <div class="output-content">
                        <div style="margin-bottom: 24px;">${formatMarkdown(data.Answer)}</div>
                        <h4 style="margin-bottom: 12px; color: var(--color-purple); font-family: var(--font-heading);">Related Concepts</h4>
                        <ul style="margin-bottom: 20px; list-style-type: none; display: flex; flex-wrap: wrap; gap: 8px; padding-left: 0;">
                            ${data.RelatedConcepts.map(c => `<li class="badge" style="font-weight: 500; font-size: 0.8rem; cursor: pointer; padding: 6px 12px;" onclick="document.getElementById('question-input').value = 'Explain ${c}';">${c}</li>`).join('')}
                        </ul>
                        <h4 style="margin-bottom: 8px; color: var(--color-blue); font-family: var(--font-heading);">Additional Context</h4>
                        <div style="background: rgba(255,255,255,0.02); border-left: 3px solid var(--color-blue); padding: 12px; border-radius: 4px; font-size: 0.9rem; color: var(--color-text-muted);">${data.AdditionalContext}</div>
                    </div>
                `;
            } else {
                showToast(data.detail || "Error retrieving response.", "error");
            }
        } catch (err) {
            toggleLoader('qa-output-card', false);
            showToast("Network connection error.", "error");
        }
    });
}

// =====================================================================
// MODULE: CONCEPT EXPLANATION
// =====================================================================
function initExplainPage() {
    const form = document.getElementById('explain-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const topic = document.getElementById('topic-input').value.trim();
        if (!topic) return;
        
        toggleLoader('explain-output-card', true, "Generating simple explanation...");
        
        try {
            const res = await fetch('/api/modules/explain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ Topic: topic })
            });
            
            const data = await res.json();
            toggleLoader('explain-output-card', false);
            
            if (res.ok) {
                const output = document.getElementById('explain-output-card');
                output.innerHTML = `
                    <div class="output-header">
                        <h3 class="page-title" style="font-size: 1.25rem;">Simple Explanation</h3>
                        <span class="badge">LaMini-Flan-T5</span>
                    </div>
                    <div class="output-content">
                        <div style="margin-bottom: 20px;">
                            <h4 style="color: var(--color-primary); font-family: var(--font-heading); margin-bottom: 6px;">Definition</h4>
                            <p>${data.Definition}</p>
                        </div>
                        <div style="margin-bottom: 20px;">
                            <h4 style="color: var(--color-purple); font-family: var(--font-heading); margin-bottom: 6px;">Illustrative Examples</h4>
                            <ul style="margin-left: 20px;">
                                ${data.Examples.map(ex => `<li style="margin-bottom: 6px; color: var(--color-text-main);">${ex}</li>`).join('')}
                            </ul>
                        </div>
                        <div style="margin-bottom: 20px;">
                            <h4 style="color: var(--color-blue); font-family: var(--font-heading); margin-bottom: 6px;">Real-world Applications</h4>
                            <ul style="margin-left: 20px;">
                                ${data.Applications.map(app => `<li style="margin-bottom: 6px; color: var(--color-text-main);">${app}</li>`).join('')}
                            </ul>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); border-top: 1px solid var(--glass-border); padding-top: 12px; font-size: 0.95rem; font-style: italic; color: var(--color-text-muted);">
                            <strong>Summary:</strong> ${data.Summary}
                        </div>
                    </div>
                `;
            } else {
                showToast(data.detail || "Failed to retrieve explanation.", "error");
            }
        } catch (err) {
            toggleLoader('explain-output-card', false);
            showToast("Network connection error.", "error");
        }
    });
}

// =====================================================================
// MODULE: INTERACTIVE QUIZ
// =====================================================================
let currentQuizData = [];
let currentQuestionIndex = 0;
let userAnswers = [];

function initQuizPage() {
    const form = document.getElementById('quiz-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const topic = document.getElementById('quiz-topic').value.trim();
        const difficulty = document.getElementById('quiz-difficulty').value;
        const count = parseInt(document.getElementById('quiz-count').value, 10);
        if (!topic) return;
        
        toggleLoader('quiz-output-card', true, "Formulating MCQs...");
        
        try {
            const res = await fetch('/api/modules/quiz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ Topic: topic, Difficulty: difficulty, QuestionCount: count })
            });
            
            const data = await res.json();
            toggleLoader('quiz-output-card', false);
            
            if (res.ok) {
                currentQuizData = data.Quizzes;
                currentQuestionIndex = 0;
                userAnswers = new Array(currentQuizData.length).fill(null);
                renderQuizQuestion();
            } else {
                showToast(data.detail || "Failed to generate quiz.", "error");
            }
        } catch (err) {
            toggleLoader('quiz-output-card', false);
            showToast("Network connection error.", "error");
        }
    });
}

function renderQuizQuestion() {
    const container = document.getElementById('quiz-output-card');
    if (!container || currentQuizData.length === 0) return;
    
    const question = currentQuizData[currentQuestionIndex];
    const totalQuestions = currentQuizData.length;
    const progressPercent = ((currentQuestionIndex + 1) / totalQuestions) * 100;
    
    container.innerHTML = `
        <div class="output-header">
            <h3 class="page-title" style="font-size: 1.25rem;">Question ${currentQuestionIndex + 1} of ${totalQuestions}</h3>
            <span class="badge">Gemini 1.5 Pro</span>
        </div>
        <div style="background: rgba(255,255,255,0.05); height: 6px; border-radius: 3px; margin-bottom: 24px; overflow: hidden;">
            <div style="background: linear-gradient(95deg, var(--color-primary), var(--color-purple)); width: ${progressPercent}%; height: 100%; transition: width 0.3s ease;"></div>
        </div>
        <div class="output-content">
            <h4 style="font-size: 1.15rem; margin-bottom: 20px; line-height: 1.5; color: white;">${question.QuestionText}</h4>
            <div class="quiz-question-container">
                <div class="quiz-option" id="opt-A" onclick="selectQuizOption('A')">
                    <div class="option-badge">A</div>
                    <span>${question.OptionA}</span>
                </div>
                <div class="quiz-option" id="opt-B" onclick="selectQuizOption('B')">
                    <div class="option-badge">B</div>
                    <span>${question.OptionB}</span>
                </div>
                <div class="quiz-option" id="opt-C" onclick="selectQuizOption('C')">
                    <div class="option-badge">C</div>
                    <span>${question.OptionC}</span>
                </div>
                <div class="quiz-option" id="opt-D" onclick="selectQuizOption('D')">
                    <div class="option-badge">D</div>
                    <span>${question.OptionD}</span>
                </div>
            </div>
            
            <div id="quiz-explanation-container" style="display: none;">
                <div class="quiz-explanation-box">
                    <strong style="color: var(--color-blue);">Explanation:</strong>
                    <p style="margin-top: 6px; font-size: 0.85rem; line-height: 1.5;">${question.Explanation}</p>
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-top: 24px;">
                <button class="btn-secondary" id="btn-quiz-prev" onclick="changeQuizQuestion(-1)" ${currentQuestionIndex === 0 ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}>Previous</button>
                <button class="btn-primary" id="btn-quiz-next" onclick="submitOrNextQuestion()" disabled>Check Answer</button>
            </div>
        </div>
    `;
    
    // Restore selection if user already answered this
    if (userAnswers[currentQuestionIndex] !== null) {
        revealQuestionResult(userAnswers[currentQuestionIndex]);
    }
}

window.selectQuizOption = function(option) {
    if (userAnswers[currentQuestionIndex] !== null) return; // Answer already lock
    
    // Remove selected style from all
    document.querySelectorAll('.quiz-option').forEach(el => el.classList.remove('selected'));
    
    const selectedOpt = document.getElementById(`opt-${option}`);
    if (selectedOpt) {
        selectedOpt.classList.add('selected');
    }
    
    const nextBtn = document.getElementById('btn-quiz-next');
    nextBtn.removeAttribute('disabled');
    nextBtn.setAttribute('data-selected-option', option);
};

window.submitOrNextQuestion = function() {
    const nextBtn = document.getElementById('btn-quiz-next');
    const selectedOption = nextBtn.getAttribute('data-selected-option');
    
    if (userAnswers[currentQuestionIndex] === null) {
        // Submit (Lock in and show corrections)
        userAnswers[currentQuestionIndex] = selectedOption;
        revealQuestionResult(selectedOption);
    } else {
        // Move to next
        currentQuestionIndex++;
        if (currentQuestionIndex < currentQuizData.length) {
            renderQuizQuestion();
        } else {
            renderQuizResults();
        }
    }
};

function revealQuestionResult(selectedOption) {
    const correctOpt = currentQuizData[currentQuestionIndex].CorrectOption.toUpperCase().trim();
    
    // Highlight correct & incorrect
    document.querySelectorAll('.quiz-option').forEach(el => {
        const optLetter = el.id.split('-')[1];
        if (optLetter === correctOpt) {
            el.classList.add('correct');
        } else if (optLetter === selectedOption) {
            el.classList.add('incorrect');
        }
    });
    
    // Show explanation
    document.getElementById('quiz-explanation-container').style.display = 'block';
    
    // Update button text
    const nextBtn = document.getElementById('btn-quiz-next');
    nextBtn.removeAttribute('disabled');
    if (currentQuestionIndex === currentQuizData.length - 1) {
        nextBtn.innerText = "Finish & See Score";
    } else {
        nextBtn.innerText = "Next Question";
    }
}

window.changeQuizQuestion = function(direction) {
    currentQuestionIndex += direction;
    renderQuizQuestion();
};

function renderQuizResults() {
    const container = document.getElementById('quiz-output-card');
    if (!container) return;
    
    let correctCount = 0;
    currentQuizData.forEach((q, idx) => {
        if (userAnswers[idx] === q.CorrectOption.toUpperCase().trim()) {
            correctCount++;
        }
    });
    
    const scorePercent = Math.round((correctCount / currentQuizData.length) * 100);
    let feedback = "";
    if (scorePercent >= 80) feedback = "Excellent! You have a solid grasp of this topic.";
    else if (scorePercent >= 50) feedback = "Good job. Try reviewing the explanations to master the gaps.";
    else feedback = "We suggest studying the topic some more and retaking the quiz.";
    
    container.innerHTML = `
        <div class="output-header" style="justify-content: center;">
            <h3 class="page-title" style="font-size: 1.5rem;">Quiz Completed</h3>
        </div>
        <div class="output-content" style="text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px;">
            <div style="width: 140px; height: 140px; border-radius: 50%; border: 8px solid rgba(255,255,255,0.05); border-top: 8px solid var(--color-success); display: flex; align-items: center; justify-content: center; font-size: 2.2rem; font-weight: 800; font-family: var(--font-heading); margin-bottom: 24px; box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);">
                ${scorePercent}%
            </div>
            <h4 style="font-size: 1.3rem; margin-bottom: 8px; color: white;">Your Score: ${correctCount} / ${currentQuizData.length}</h4>
            <p style="color: var(--color-text-muted); max-width: 400px; margin-bottom: 30px; line-height: 1.5;">${feedback}</p>
            <button class="btn-primary" onclick="window.location.reload()">Take Another Quiz</button>
        </div>
    `;
}

// =====================================================================
// MODULE: SUMMARY & PDF UPLOADER
// =====================================================================
function initSummaryPage() {
    const form = document.getElementById('summary-form');
    const fileInput = document.getElementById('pdf-file');
    const notesInput = document.getElementById('notes-input');
    
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // If file exists, do PDF upload summary
        if (fileInput && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);
            
            toggleLoader('summary-output-card', true, "Extracting and summarizing PDF content...");
            
            try {
                const res = await fetch('/api/modules/summarize/pdf', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await res.json();
                toggleLoader('summary-output-card', false);
                
                if (res.ok) {
                    renderSummaryResult(data);
                } else {
                    showToast(data.detail || "Failed to process PDF.", "error");
                }
            } catch (err) {
                toggleLoader('summary-output-card', false);
                showToast("Network connection error.", "error");
            }
        } else {
            // Text summary
            const notes = notesInput.value.trim();
            if (!notes) {
                showToast("Please enter notes or upload a PDF first.", "error");
                return;
            }
            
            toggleLoader('summary-output-card', true, "Generating summary...");
            
            try {
                const res = await fetch('/api/modules/summarize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ Notes: notes })
                });
                
                const data = await res.json();
                toggleLoader('summary-output-card', false);
                
                if (res.ok) {
                    renderSummaryResult(data);
                } else {
                    showToast(data.detail || "Failed to summarize text.", "error");
                }
            } catch (err) {
                toggleLoader('summary-output-card', false);
                showToast("Network connection error.", "error");
            }
        }
    });
}

function renderSummaryResult(data) {
    const output = document.getElementById('summary-output-card');
    if (!output) return;
    
    output.innerHTML = `
        <div class="output-header">
            <h3 class="page-title" style="font-size: 1.25rem;">Content Summary</h3>
            <button class="btn-secondary" style="padding: 6px 12px; font-size: 0.8rem;" onclick="copySummaryText()">Copy Summary</button>
        </div>
        <div class="output-content">
            <div style="margin-bottom: 24px;">
                <h4 style="color: var(--color-primary); font-family: var(--font-heading); margin-bottom: 6px;">Summary Overview</h4>
                <p id="summary-main-text" style="color: white; font-size: 0.95rem; line-height: 1.6;">${data.Summary}</p>
            </div>
            
            ${data.ImportantPoints.length > 0 ? `
                <div style="margin-bottom: 20px;">
                    <h4 style="color: var(--color-purple); font-family: var(--font-heading); margin-bottom: 6px;">Key Takeaways</h4>
                    <ul style="margin-left: 20px;">
                        ${data.ImportantPoints.map(pt => `<li style="margin-bottom: 6px; color: var(--color-text-main);">${pt}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${data.Formulas.length > 0 ? `
                <div style="margin-bottom: 20px;">
                    <h4 style="color: var(--color-blue); font-family: var(--font-heading); margin-bottom: 6px;">Key Formulas & Equations</h4>
                    <ul style="list-style-type: none; padding-left: 0;">
                        ${data.Formulas.map(f => `<li style="margin-bottom: 8px; font-family: monospace; background: rgba(59,130,246,0.1); border: 1px dashed rgba(59,130,246,0.3); padding: 8px 12px; border-radius: 6px;">${f}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${data.Definitions.length > 0 ? `
                <div style="margin-bottom: 20px;">
                    <h4 style="color: var(--color-indigo); font-family: var(--font-heading); margin-bottom: 6px;">Core Terminology & Definitions</h4>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        ${data.Definitions.map(d => {
                            const parts = d.split(':');
                            const term = parts[0] || 'Term';
                            const desc = parts.slice(1).join(':') || '';
                            return `<div style="background: rgba(255,255,255,0.01); border: 1px solid var(--glass-border); border-radius: 6px; padding: 10px 12px;">
                                <strong style="color: #818CF8;">${term}:</strong> <span style="font-size: 0.88rem; color: var(--color-text-main);">${desc}</span>
                            </div>`;
                        }).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${data.ExamNotes ? `
                <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-left: 4px solid var(--color-success); padding: 16px; border-radius: 8px; margin-top: 24px;">
                    <h4 style="color: var(--color-success); font-family: var(--font-heading); margin-bottom: 6px; font-size: 0.95rem;">Exam & Study Tips</h4>
                    <p style="font-size: 0.88rem; color: var(--color-text-muted); line-height: 1.5;">${data.ExamNotes}</p>
                </div>
            ` : ''}
        </div>
    `;
}

window.copySummaryText = function() {
    const summaryTextEl = document.getElementById('summary-main-text');
    if (!summaryTextEl) return;
    
    navigator.clipboard.writeText(summaryTextEl.innerText)
        .then(() => showToast("Summary copied to clipboard!", "success"))
        .catch(() => showToast("Failed to copy text.", "error"));
};

// =====================================================================
// MODULE: PERSONALIZED LEARNING PATH (ROADMAP)
// =====================================================================
function initRoadmapPage() {
    const form = document.getElementById('roadmap-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const skill = document.getElementById('skill-input').value.trim();
        if (!skill) return;
        
        toggleLoader('roadmap-output-card', true, "Generating personalized learning roadmap...");
        
        try {
            const res = await fetch('/api/modules/learn/recommendations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ SkillName: skill })
            });
            
            const data = await res.json();
            toggleLoader('roadmap-output-card', false);
            
            if (res.ok) {
                renderRoadmapResult(data);
            } else {
                showToast(data.detail || "Failed to generate learning path.", "error");
            }
        } catch (err) {
            toggleLoader('roadmap-output-card', false);
            showToast("Network connection error.", "error");
        }
    });
}

function renderRoadmapResult(data) {
    const output = document.getElementById('roadmap-output-card');
    if (!output) return;
    
    output.innerHTML = `
        <div class="output-header">
            <h3 class="page-title" style="font-size: 1.25rem;">Roadmap for: ${data.Topic}</h3>
            <span class="badge">Gemini 1.5 Pro</span>
        </div>
        <div class="output-content">
            <div class="timeline">
                <!-- Beginner Section -->
                <div class="timeline-item">
                    <div class="timeline-dot"></div>
                    <div class="timeline-title">Stage 1: Beginner <span style="font-size: 0.8rem; font-weight: normal; color: var(--color-primary); margin-left: 10px;">(${data.Beginner.Timeline})</span></div>
                    <div class="timeline-content">
                        <div style="margin-bottom: 12px;">
                            <strong style="color: var(--color-primary); font-size: 0.9rem;">Core Topics:</strong>
                            <ul style="margin-left: 20px; font-size: 0.85rem; margin-top: 4px;">
                                ${data.Beginner.Topics.map(t => `<li>${t}</li>`).join('')}
                            </ul>
                        </div>
                        <div style="margin-bottom: 12px;">
                            <strong style="color: var(--color-blue); font-size: 0.9rem;">Starter Projects:</strong>
                            <ul style="margin-left: 20px; font-size: 0.85rem; margin-top: 4px;">
                                ${data.Beginner.Projects.map(p => `<li>${p}</li>`).join('')}
                            </ul>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px;">
                            <div>
                                <strong style="font-size: 0.8rem; color: var(--color-text-muted);">Resources:</strong>
                                <p style="font-size: 0.8rem; margin-top: 2px;">${data.Beginner.Resources.join(', ') || 'Online Docs'}</p>
                            </div>
                            <div>
                                <strong style="font-size: 0.8rem; color: var(--color-text-muted);">Certifications:</strong>
                                <p style="font-size: 0.8rem; margin-top: 2px;">${data.Beginner.Certifications.join(', ') || 'N/A'}</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Intermediate Section -->
                <div class="timeline-item">
                    <div class="timeline-dot" style="border-color: var(--color-purple); box-shadow: 0 0 8px var(--color-purple);"></div>
                    <div class="timeline-title">Stage 2: Intermediate <span style="font-size: 0.8rem; font-weight: normal; color: var(--color-purple); margin-left: 10px;">(${data.Intermediate.Timeline})</span></div>
                    <div class="timeline-content">
                        <div style="margin-bottom: 12px;">
                            <strong style="color: var(--color-purple); font-size: 0.9rem;">Core Topics:</strong>
                            <ul style="margin-left: 20px; font-size: 0.85rem; margin-top: 4px;">
                                ${data.Intermediate.Topics.map(t => `<li>${t}</li>`).join('')}
                            </ul>
                        </div>
                        <div style="margin-bottom: 12px;">
                            <strong style="color: var(--color-blue); font-size: 0.9rem;">Intermediate Projects:</strong>
                            <ul style="margin-left: 20px; font-size: 0.85rem; margin-top: 4px;">
                                ${data.Intermediate.Projects.map(p => `<li>${p}</li>`).join('')}
                            </ul>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px;">
                            <div>
                                <strong style="font-size: 0.8rem; color: var(--color-text-muted);">Resources:</strong>
                                <p style="font-size: 0.8rem; margin-top: 2px;">${data.Intermediate.Resources.join(', ') || 'Advanced guides'}</p>
                            </div>
                            <div>
                                <strong style="font-size: 0.8rem; color: var(--color-text-muted);">Certifications:</strong>
                                <p style="font-size: 0.8rem; margin-top: 2px;">${data.Intermediate.Certifications.join(', ') || 'N/A'}</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Advanced Section -->
                <div class="timeline-item">
                    <div class="timeline-dot" style="border-color: var(--color-blue); box-shadow: 0 0 8px var(--color-blue);"></div>
                    <div class="timeline-title">Stage 3: Advanced <span style="font-size: 0.8rem; font-weight: normal; color: var(--color-blue); margin-left: 10px;">(${data.Advanced.Timeline})</span></div>
                    <div class="timeline-content">
                        <div style="margin-bottom: 12px;">
                            <strong style="color: var(--color-blue); font-size: 0.9rem;">Advanced Concepts:</strong>
                            <ul style="margin-left: 20px; font-size: 0.85rem; margin-top: 4px;">
                                ${data.Advanced.Topics.map(t => `<li>${t}</li>`).join('')}
                            </ul>
                        </div>
                        <div style="margin-bottom: 12px;">
                            <strong style="color: var(--color-blue); font-size: 0.9rem;">Capstone Projects:</strong>
                            <ul style="margin-left: 20px; font-size: 0.85rem; margin-top: 4px;">
                                ${data.Advanced.Projects.map(p => `<li>${p}</li>`).join('')}
                            </ul>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px;">
                            <div>
                                <strong style="font-size: 0.8rem; color: var(--color-text-muted);">Resources:</strong>
                                <p style="font-size: 0.8rem; margin-top: 2px;">${data.Advanced.Resources.join(', ') || 'Expert whitepapers'}</p>
                            </div>
                            <div>
                                <strong style="font-size: 0.8rem; color: var(--color-text-muted);">Certifications:</strong>
                                <p style="font-size: 0.8rem; margin-top: 2px;">${data.Advanced.Certifications.join(', ') || 'Professional Certs'}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            ${data.CareerSuggestions.length > 0 ? `
                <div style="background: rgba(108,99,255,0.06); border: 1px solid rgba(108,99,255,0.2); border-radius: 8px; padding: 16px; margin-top: 32px;">
                    <h4 style="color: var(--color-primary); font-family: var(--font-heading); margin-bottom: 8px; font-size: 0.95rem;">Recommended Career Paths</h4>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                        ${data.CareerSuggestions.map(job => `<span class="badge" style="background: rgba(108,99,255,0.15); border-color: rgba(108,99,255,0.4); font-size: 0.78rem; padding: 6px 12px;">${job}</span>`).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

// =====================================================================
// LEARNING QUERY HISTORY TABLE & MODAL
// =====================================================================
async function initHistoryPage() {
    const listBody = document.getElementById('history-list-body');
    if (!listBody) return;
    
    try {
        const res = await fetch('/api/history');
        if (!res.ok) return;
        const historyItems = await res.json();
        
        if (historyItems.length === 0) {
            listBody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; padding: 32px; color: var(--color-text-muted);">
                        No history records found. Start requesting content to see logs here.
                    </td>
                </tr>
            `;
            return;
        }
        
        listBody.innerHTML = historyItems.map(item => `
            <tr style="border-bottom: 1px solid var(--glass-border);">
                <td style="padding: 16px;">
                    <span class="badge" style="text-transform: uppercase;">${item.QueryType}</span>
                </td>
                <td style="padding: 16px; font-weight: 500;">
                    ${item.QueryText.substring(0, 50)}${item.QueryText.length > 50 ? '...' : ''}
                </td>
                <td style="padding: 16px; color: var(--color-text-muted); font-size: 0.85rem;">
                    ${item.ResponsePreview || 'Processing...'}
                </td>
                <td style="padding: 16px; font-size: 0.85rem; color: var(--color-text-muted);">
                    ${new Date(item.CreatedAt).toLocaleDateString()}
                </td>
                <td style="padding: 16px;">
                    <button class="btn-secondary" style="padding: 6px 12px; font-size: 0.78rem;" onclick="openHistoryDetails(${item.QueryID})">View Details</button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        showToast("Error loading history data.", "error");
    }
}

window.openHistoryDetails = async function(queryId) {
    const modal = document.getElementById('history-modal');
    const modalContent = document.getElementById('history-modal-body');
    if (!modal || !modalContent) return;
    
    modalContent.innerHTML = `<div style="text-align: center; padding: 40px;"><div class="spinner"></div></div>`;
    modal.style.display = 'flex';
    
    try {
        const res = await fetch(`/api/history/${queryId}`);
        if (!res.ok) {
            showToast("Failed to fetch history details.", "error");
            modal.style.display = 'none';
            return;
        }
        
        const data = await res.json();
        let bodyHtml = "";
        
        // Format modal body based on query type
        if (data.QueryType === 'qa') {
            bodyHtml = `
                <div style="margin-bottom: 16px;">
                    <span class="badge" style="text-transform: uppercase;">Q&A</span>
                    <h3 style="margin-top: 12px; margin-bottom: 8px;">Question: "${data.QueryText}"</h3>
                    <p style="font-size: 0.82rem; color: var(--color-text-muted);">Asked on ${new Date(data.CreatedAt).toLocaleString()} using ${data.ModelUsed}</p>
                </div>
                <hr style="border: 0; border-top: 1px solid var(--glass-border); margin: 16px 0;">
                <div>
                    <h4 style="color: var(--color-primary); margin-bottom: 8px;">Answer</h4>
                    <div>${formatMarkdown(data.Details.Answer)}</div>
                    
                    ${data.Details.RelatedConcepts ? `
                        <h4 style="color: var(--color-purple); margin-top: 20px; margin-bottom: 8px;">Related Concepts</h4>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                            ${data.Details.RelatedConcepts.map(c => `<span class="badge">${c}</span>`).join('')}
                        </div>
                    ` : ''}
                    
                    ${data.Details.AdditionalContext ? `
                        <h4 style="color: var(--color-blue); margin-top: 20px; margin-bottom: 8px;">Additional Context</h4>
                        <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 4px; border-left: 3px solid var(--color-blue);">${data.Details.AdditionalContext}</div>
                    ` : ''}
                </div>
            `;
        } else if (data.QueryType === 'explain') {
            bodyHtml = `
                <div style="margin-bottom: 16px;">
                    <span class="badge" style="text-transform: uppercase;">Concept Explanation</span>
                    <h3 style="margin-top: 12px; margin-bottom: 8px;">Topic: "${data.QueryText}"</h3>
                    <p style="font-size: 0.82rem; color: var(--color-text-muted);">Requested on ${new Date(data.CreatedAt).toLocaleString()} using ${data.ModelUsed}</p>
                </div>
                <hr style="border: 0; border-top: 1px solid var(--glass-border); margin: 16px 0;">
                <div>
                    <h4 style="color: var(--color-primary); margin-bottom: 6px;">Definition</h4>
                    <p style="margin-bottom: 16px;">${data.Details.Definition}</p>
                    
                    <h4 style="color: var(--color-purple); margin-bottom: 6px;">Examples</h4>
                    <ul style="margin-left: 20px; margin-bottom: 16px;">
                        ${data.Details.Examples ? data.Details.Examples.map(e => `<li>${e}</li>`).join('') : ''}
                    </ul>
                    
                    <h4 style="color: var(--color-blue); margin-bottom: 6px;">Applications</h4>
                    <ul style="margin-left: 20px; margin-bottom: 16px;">
                        ${data.Details.Applications ? data.Details.Applications.map(a => `<li>${a}</li>`).join('') : ''}
                    </ul>
                    
                    <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 4px; font-style: italic;">
                        <strong>Summary:</strong> ${data.Details.Summary}
                    </div>
                </div>
            `;
        } else if (data.QueryType === 'quiz') {
            const list = data.Details.Quizzes || [];
            bodyHtml = `
                <div style="margin-bottom: 16px;">
                    <span class="badge" style="text-transform: uppercase;">Quiz</span>
                    <h3 style="margin-top: 12px; margin-bottom: 8px;">Quiz: "${data.QueryText}"</h3>
                    <p style="font-size: 0.82rem; color: var(--color-text-muted);">Generated on ${new Date(data.CreatedAt).toLocaleString()} using ${data.ModelUsed}</p>
                </div>
                <hr style="border: 0; border-top: 1px solid var(--glass-border); margin: 16px 0;">
                <div style="display: flex; flex-direction: column; gap: 20px;">
                    ${list.map((q, idx) => `
                        <div style="background: rgba(255,255,255,0.015); border: 1px solid var(--glass-border); padding: 16px; border-radius: 8px;">
                            <strong style="color: white; font-size: 0.95rem;">Q${idx+1}: ${q.QuestionText}</strong>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 12px;">
                                <div style="font-size: 0.85rem; padding: 6px; border-radius: 4px; background: ${q.CorrectOption === 'A' ? 'rgba(16,185,129,0.15); border: 1px solid var(--color-success)' : 'rgba(0,0,0,0.1)'};">A) ${q.OptionA}</div>
                                <div style="font-size: 0.85rem; padding: 6px; border-radius: 4px; background: ${q.CorrectOption === 'B' ? 'rgba(16,185,129,0.15); border: 1px solid var(--color-success)' : 'rgba(0,0,0,0.1)'};">B) ${q.OptionB}</div>
                                <div style="font-size: 0.85rem; padding: 6px; border-radius: 4px; background: ${q.CorrectOption === 'C' ? 'rgba(16,185,129,0.15); border: 1px solid var(--color-success)' : 'rgba(0,0,0,0.1)'};">C) ${q.OptionC}</div>
                                <div style="font-size: 0.85rem; padding: 6px; border-radius: 4px; background: ${q.CorrectOption === 'D' ? 'rgba(16,185,129,0.15); border: 1px solid var(--color-success)' : 'rgba(0,0,0,0.1)'};">D) ${q.OptionD}</div>
                            </div>
                            <div style="background: rgba(59,130,246,0.08); padding: 10px; border-radius: 6px; margin-top: 10px; font-size: 0.82rem; line-height: 1.4;">
                                <strong>Explanation:</strong> ${q.Explanation}
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else if (data.QueryType === 'summarize') {
            bodyHtml = `
                <div style="margin-bottom: 16px;">
                    <span class="badge" style="text-transform: uppercase;">Content Summary</span>
                    <h3 style="margin-top: 12px; margin-bottom: 8px;">Source Notes Summary</h3>
                    <p style="font-size: 0.82rem; color: var(--color-text-muted);">Summarized on ${new Date(data.CreatedAt).toLocaleString()} using ${data.ModelUsed}</p>
                </div>
                <hr style="border: 0; border-top: 1px solid var(--glass-border); margin: 16px 0;">
                <div>
                    <h4 style="color: var(--color-primary); margin-bottom: 6px;">Summary Overview</h4>
                    <p style="margin-bottom: 16px; font-size: 0.92rem; line-height: 1.5; color: white;">${data.Details.Summary}</p>
                    
                    ${data.Details.ImportantPoints && data.Details.ImportantPoints.length > 0 ? `
                        <h4 style="color: var(--color-purple); margin-bottom: 6px;">Important Takeaways</h4>
                        <ul style="margin-left: 20px; margin-bottom: 16px;">
                            ${data.Details.ImportantPoints.map(p => `<li>${p}</li>`).join('')}
                        </ul>
                    ` : ''}
                    
                    ${data.Details.Formulas && data.Details.Formulas.length > 0 ? `
                        <h4 style="color: var(--color-blue); margin-bottom: 6px;">Formulas</h4>
                        <ul style="margin-left: 20px; margin-bottom: 16px; font-family: monospace;">
                            ${data.Details.Formulas.map(f => `<li>${f}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>
            `;
        } else if (data.QueryType === 'learn') {
            const b = data.Details.Beginner || {};
            const i = data.Details.Intermediate || {};
            const a = data.Details.Advanced || {};
            bodyHtml = `
                <div style="margin-bottom: 16px;">
                    <span class="badge" style="text-transform: uppercase;">Roadmap</span>
                    <h3 style="margin-top: 12px; margin-bottom: 8px;">Learning Path: "${data.QueryText}"</h3>
                    <p style="font-size: 0.82rem; color: var(--color-text-muted);">Generated on ${new Date(data.CreatedAt).toLocaleString()} using ${data.ModelUsed}</p>
                </div>
                <hr style="border: 0; border-top: 1px solid var(--glass-border); margin: 16px 0;">
                <div>
                    <div style="display: flex; flex-direction: column; gap: 16px;">
                        <div style="background: rgba(255,255,255,0.015); border: 1px solid var(--glass-border); padding: 16px; border-radius: 8px;">
                            <strong style="color: var(--color-primary);">Beginner Stage (${b.Timeline || 'N/A'})</strong>
                            <p style="font-size: 0.85rem; margin-top: 6px;"><strong>Topics:</strong> ${b.Topics ? b.Topics.join(', ') : ''}</p>
                            <p style="font-size: 0.85rem; margin-top: 4px;"><strong>Projects:</strong> ${b.Projects ? b.Projects.join(', ') : ''}</p>
                        </div>
                        <div style="background: rgba(255,255,255,0.015); border: 1px solid var(--glass-border); padding: 16px; border-radius: 8px;">
                            <strong style="color: var(--color-purple);">Intermediate Stage (${i.Timeline || 'N/A'})</strong>
                            <p style="font-size: 0.85rem; margin-top: 6px;"><strong>Topics:</strong> ${i.Topics ? i.Topics.join(', ') : ''}</p>
                            <p style="font-size: 0.85rem; margin-top: 4px;"><strong>Projects:</strong> ${i.Projects ? i.Projects.join(', ') : ''}</p>
                        </div>
                        <div style="background: rgba(255,255,255,0.015); border: 1px solid var(--glass-border); padding: 16px; border-radius: 8px;">
                            <strong style="color: var(--color-blue);">Advanced Stage (${a.Timeline || 'N/A'})</strong>
                            <p style="font-size: 0.85rem; margin-top: 6px;"><strong>Topics:</strong> ${a.Topics ? a.Topics.join(', ') : ''}</p>
                            <p style="font-size: 0.85rem; margin-top: 4px;"><strong>Projects:</strong> ${a.Projects ? a.Projects.join(', ') : ''}</p>
                        </div>
                    </div>
                </div>
            `;
        }
        
        modalContent.innerHTML = bodyHtml;
    } catch (err) {
        showToast("Error retrieving query details.", "error");
        modal.style.display = 'none';
    }
};

window.closeHistoryModal = function() {
    const modal = document.getElementById('history-modal');
    if (modal) modal.style.display = 'none';
};

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('history-modal');
    if (event.target === modal) {
        modal.style.display = "none";
    }
};

// =====================================================================
// USER PROFILE SETTINGS
// =====================================================================
function initProfilePage() {
    // Form is loaded from base layout
}
