/**
 * Q&A Practice Application - Quiz JavaScript
 * 
 * This file contains HTMX interactions and dynamic functionality
 * for the quiz interface including question loading, answer submission,
 * and real-time feedback.
 */

// Global quiz state
window.QuizApp = {
    state: {
        sessionId: null,
        currentQuestion: null,
        answered: false,
        startTime: null,
        timer: null,
        stats: {
            correct: 0,
            incorrect: 0,
            skipped: 0,
            total: 0
        }
    },
    
    // Initialize the quiz application
    init: function(sessionId) {
        this.state.sessionId = sessionId;
        this.state.startTime = Date.now();
        this.setupEventListeners();
        this.startTimer();
    },
    
    // Setup HTMX event listeners
    setupEventListeners: function() {
        // HTMX before request - show loading state
        document.body.addEventListener('htmx:beforeRequest', function(evt) {
            const target = evt.detail.target;
            if (target && target.id === 'question-content') {
                QuizApp.showLoadingState();
            }
        });
        
        // HTMX after request - handle responses
        document.body.addEventListener('htmx:afterRequest', function(evt) {
            const target = evt.detail.target;
            const xhr = evt.detail.xhr;
            
            if (target && target.id === 'question-content') {
                QuizApp.hideLoadingState();
                if (evt.detail.successful) {
                    QuizApp.handleQuestionLoaded(xhr.responseText);
                } else {
                    QuizApp.handleError('Failed to load question');
                }
            }
            
            if (target && target.id === 'feedback-section') {
                QuizApp.handleAnswerResponse(xhr.responseText);
            }
            
            if (target && target.id === 'form-result') {
                QuizApp.handleSessionCreation(xhr.responseText);
            }
        });
        
        // HTMX error handling
        document.body.addEventListener('htmx:responseError', function(evt) {
            const xhr = evt.detail.xhr;
            QuizApp.handleError(`Request failed: ${xhr.status} ${xhr.statusText}`);
        });
        
        // HTMX swap - handle content updates
        document.body.addEventListener('htmx:afterSwap', function(evt) {
            const target = evt.detail.target;
            if (target) {
                QuizApp.animateContent(target);
            }
        });
    },
    
    // Show loading state for question loading
    showLoadingState: function() {
        const loadingState = document.getElementById('loading-state');
        const questionContent = document.getElementById('question-content');
        
        if (loadingState) loadingState.classList.remove('hidden');
        if (questionContent) questionContent.classList.add('hidden');
    },
    
    // Hide loading state
    hideLoadingState: function() {
        const loadingState = document.getElementById('loading-state');
        const questionContent = document.getElementById('question-content');
        
        if (loadingState) loadingState.classList.add('hidden');
        if (questionContent) questionContent.classList.remove('hidden');
    },
    
    // Handle successful question load
    handleQuestionLoaded: function(responseHtml) {
        this.state.answered = false;
        this.attachQuestionEventListeners();
        this.updateQuestionDisplay();
    },
    
    // Attach event listeners to question options
    attachQuestionEventListeners: function() {
        const optionButtons = document.querySelectorAll('.option-button');
        optionButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                if (!this.state.answered) {
                    this.selectOption(button);
                }
            });
        });
    },
    
    // Handle option selection
    selectOption: function(button) {
        if (this.state.answered) return;
        
        // Disable all buttons
        const allButtons = document.querySelectorAll('.option-button');
        allButtons.forEach(btn => btn.disabled = true);
        
        // Add selected state
        button.classList.add('selected');
        
        // Submit answer via HTMX
        const questionId = button.dataset.questionId;
        const answer = button.dataset.answer;
        
        this.submitAnswer(questionId, answer, button);
    },
    
    // Submit answer via HTMX
    submitAnswer: function(questionId, answer, buttonElement) {
        const formData = new FormData();
        formData.append('question_id', questionId);
        formData.append('answer', answer);
        
        htmx.ajax('POST', `/api/v1/sessions/${this.state.sessionId}/answer`, {
            target: '#feedback-section',
            swap: 'innerHTML',
            values: formData
        });
    },
    
    // Handle answer response
    handleAnswerResponse: function(responseHtml) {
        const feedbackSection = document.getElementById('feedback-section');
        
        if (feedbackSection) {
            feedbackSection.classList.remove('hidden');
            feedbackSection.classList.add('fade-in');
            
            // Check if answer was correct
            const isCorrect = feedbackSection.classList.contains('correct-answer');
            
            if (isCorrect) {
                this.state.stats.correct++;
                this.showCorrectFeedback();
            } else {
                this.state.stats.incorrect++;
                this.showIncorrectFeedback();
            }
            
            this.state.answered = true;
            this.updateStats();
            this.showNavigationButtons();
        }
    },
    
    // Show correct answer feedback
    showCorrectFeedback: function() {
        const selectedButton = document.querySelector('.option-button.selected');
        if (selectedButton) {
            selectedButton.classList.add('correct-answer');
            this.playFeedbackSound('correct');
            this.showFeedbackAnimation('success');
        }
    },
    
    // Show incorrect answer feedback
    showIncorrectFeedback: function() {
        const selectedButton = document.querySelector('.option-button.selected');
        if (selectedButton) {
            selectedButton.classList.add('incorrect-answer');
        }
        
        // Highlight correct answer
        const feedbackSection = document.getElementById('feedback-section');
        const correctAnswer = feedbackSection.dataset.correctAnswer;
        const correctButton = document.querySelector(`[data-answer="${correctAnswer}"]`);
        
        if (correctButton) {
            correctButton.classList.add('correct-answer');
        }
        
        this.playFeedbackSound('incorrect');
        this.showFeedbackAnimation('error');
    },
    
    // Show feedback animation
    showFeedbackAnimation: function(type) {
        const questionCard = document.querySelector('.question-card');
        if (questionCard) {
            questionCard.classList.add(`${type}-pulse`);
            setTimeout(() => {
                questionCard.classList.remove(`${type}-pulse`);
            }, 1000);
        }
    },
    
    // Play feedback sound ( optional, requires audio files )
    playFeedbackSound: function(type) {
        try {
            const audio = new Audio(`/static/sounds/${type}.mp3`);
            audio.volume = 0.3;
            audio.play().catch(() => {
                // Ignore audio errors ( autoplay policy, etc. )
            });
        } catch (e) {
            // Ignore if audio files don't exist
        }
    },
    
    // Show navigation buttons after answering
    showNavigationButtons: function() {
        const navButtons = document.getElementById('navigation-buttons');
        const nextButton = document.getElementById('next-button');
        const finishButton = document.getElementById('finish-button');
        
        if (navButtons) {
            navButtons.classList.remove('hidden');
            navButtons.classList.add('slide-up');
        }
        
        // Show appropriate button based on question count
        const currentQuestion = parseInt(document.getElementById('question-counter').textContent.split('/')[0]);
        const totalQuestions = parseInt(document.getElementById('question-counter').textContent.split('/')[1]);
        
        if (currentQuestion >= totalQuestions) {
            if (finishButton) finishButton.classList.remove('hidden');
            if (nextButton) nextButton.classList.add('hidden');
        } else {
            if (nextButton) nextButton.classList.remove('hidden');
            if (finishButton) finishButton.classList.add('hidden');
        }
    },
    
    // Update statistics display
    updateStats: function() {
        const correctElement = document.getElementById('correct-count');
        const incorrectElement = document.getElementById('incorrect-count');
        const skippedElement = document.getElementById('skipped-count');
        const scoreElement = document.getElementById('score-display');
        const accuracyElement = document.getElementById('accuracy-rate');
        
        if (correctElement) correctElement.textContent = this.state.stats.correct;
        if (incorrectElement) incorrectElement.textContent = this.state.stats.incorrect;
        if (skippedElement) skippedElement.textContent = this.state.stats.skipped;
        if (scoreElement) scoreElement.textContent = this.state.stats.correct;
        
        // Calculate accuracy
        const totalAttempted = this.state.stats.correct + this.state.stats.incorrect;
        const accuracy = totalAttempted > 0 ? 
            Math.round((this.state.stats.correct / totalAttempted) * 100) : 0;
        
        if (accuracyElement) accuracyElement.textContent = `${accuracy}%`;
    },
    
    // Update question display
    updateQuestionDisplay: function() {
        const questionCounter = document.getElementById('question-counter');
        const progressBar = document.getElementById('progress-bar');
        
        if (questionCounter && progressBar) {
            const currentText = questionCounter.textContent;
            const [current, total] = currentText.split('/').map(n => parseInt(n));
            const progress = (current / total) * 100;
            
            progressBar.style.width = `${progress}%`;
        }
    },
    
    // Handle session creation response
    handleSessionCreation: function(responseHtml) {
        try {
            const response = JSON.parse(responseHtml);
            if (response.session_id) {
                // Redirect to quiz page
                window.location.href = `/quiz/${response.session_id}`;
            }
        } catch (e) {
            console.error('Failed to parse session creation response:', e);
        }
    },
    
    // Timer functionality
    startTimer: function() {
        this.state.timer = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.state.startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            
            const timerElement = document.getElementById('timer');
            if (timerElement) {
                timerElement.textContent = 
                    `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        }, 1000);
    },
    
    stopTimer: function() {
        if (this.state.timer) {
            clearInterval(this.state.timer);
            this.state.timer = null;
        }
    },
    
    // Animate content updates
    animateContent: function(element) {
        element.classList.add('fade-in');
        setTimeout(() => {
            element.classList.remove('fade-in');
        }, 500);
    },
    
    // Handle errors
    handleError: function(message) {
        console.error('Quiz error:', message);
        
        // Show error toast
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-error-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 fade-in';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    },
    
    // Load next question
    loadNextQuestion: function() {
        this.state.currentQuestion++;
        this.showLoadingState();
        
        htmx.ajax('GET', `/api/v1/questions/random?session_id=${this.state.sessionId}`, {
            target: '#question-content',
            swap: 'innerHTML'
        });
    },
    
    // Skip current question
    skipQuestion: function() {
        this.state.stats.skipped++;
        this.updateStats();
        this.loadNextQuestion();
    },
    
    // End current session
    endSession: function() {
        this.stopTimer();
        window.location.href = `/results/${this.state.sessionId}`;
    }
};

// Global functions for button onclick handlers
window.nextQuestion = function() {
    window.QuizApp.loadNextQuestion();
};

window.skipQuestion = function() {
    window.QuizApp.skipQuestion();
};

window.finishQuiz = function() {
    window.QuizApp.endSession();
};

window.endSession = function() {
    document.getElementById('end-session-modal').classList.remove('hidden');
};

window.closeEndSessionModal = function() {
    document.getElementById('end-session-modal').classList.add('hidden');
};

window.confirmEndSession = function() {
    window.QuizApp.endSession();
};

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Only handle keys when quiz is active
    if (!window.QuizApp.state.sessionId || window.QuizApp.state.answered) return;
    
    const key = event.key.toUpperCase();
    
    // Option selection ( A, B, C, D )
    if (key >= 'A' && key <= 'D') {
        const optionButtons = document.querySelectorAll('.option-button');
        const index = key.charCodeAt(0) - 'A'.charCodeAt(0);
        
        if (index < optionButtons.length && !optionButtons[index].disabled) {
            optionButtons[index].click();
        }
    }
    
    // Skip question ( S )
    else if (key === 'S') {
        const skipButton = document.getElementById('skip-button');
        if (skipButton && !skipButton.disabled) {
            skipButton.click();
        }
    }
    
    // Next question ( Enter, N )
    else if ((key === 'ENTER' || key === 'N') && window.QuizApp.state.answered) {
        const nextButton = document.getElementById('next-button');
        const finishButton = document.getElementById('finish-button');
        
        if (nextButton && !nextButton.classList.contains('hidden')) {
            nextButton.click();
        } else if (finishButton && !finishButton.classList.contains('hidden')) {
            finishButton.click();
        }
    }
    
    // End session ( Escape )
    else if (key === 'ESCAPE') {
        endSession();
    }
});

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        window.QuizApp.stopTimer();
    } else {
        window.QuizApp.startTimer();
    }
});

// Handle page unload
window.addEventListener('beforeunload', function(event) {
    if (window.QuizApp.state.sessionId && window.QuizApp.state.currentQuestion > 0) {
        event.preventDefault();
        event.returnValue = 'You have an active quiz session. Are you sure you want to leave?';
        return event.returnValue;
    }
});

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Auto-initialize if session data is available
    const sessionData = document.querySelector('[data-session-id]');
    if (sessionData) {
        const sessionId = sessionData.dataset.sessionId;
        window.QuizApp.init(sessionId);
    }
});
