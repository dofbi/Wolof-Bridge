// Initialize UI elements when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded, initializing UI elements...');
    
    // Get all required elements using proper selectors
    const elements = {
        queryInput: document.getElementById('query'),
        submitButton: document.getElementById('submitButton'),
        spinner: document.getElementById('spinner'),
        errorElement: document.getElementById('errorMessage'),
        resultsSection: document.getElementById('resultsSection'),
        resultElements: {
            originalQuery: document.getElementById('originalQuery'),
            frenchQuery: document.getElementById('frenchQuery'),
            frenchResponse: document.getElementById('frenchResponse'),
            wolofResponse: document.getElementById('wolofResponse')
        }
    };

    // Verify all elements exist
    const missingElements = [];
    
    // Check main elements
    for (const [key, element] of Object.entries(elements)) {
        if (key !== 'resultElements' && !element) {
            missingElements.push(key);
        }
    }
    
    // Check result elements
    if (elements.resultElements) {
        for (const [key, element] of Object.entries(elements.resultElements)) {
            if (!element) {
                missingElements.push(`resultElements.${key}`);
            }
        }
    }

    if (missingElements.length > 0) {
        console.error('Missing UI elements:', missingElements);
        const error = document.getElementById('errorMessage');
        if (error) {
            error.textContent = 'Application initialization failed. Please refresh the page.';
            error.classList.add('visible');
        }
        return;
    }

    console.log('All UI elements initialized successfully');

    // Initialize event listeners with proper error handling
    elements.submitButton.addEventListener('click', () => {
        processQuery(elements)
            .catch(error => {
                console.error('Error in query processing:', error);
                showError(error.message || 'An unexpected error occurred', elements);
            });
    });

    elements.queryInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            processQuery(elements)
                .catch(error => {
                    console.error('Error in query processing:', error);
                    showError(error.message || 'An unexpected error occurred', elements);
                });
        }
    });

    // Global error handler
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        const errorMsg = event.reason?.message || 'An unexpected error occurred';
        showError(errorMsg, elements);
        setLoadingState(false, elements);
        event.preventDefault();
    });
});

async function processQuery(elements) {
    if (!elements?.queryInput) {
        throw new Error('Required UI elements not available');
    }

    const query = elements.queryInput.value.trim();
    
    if (!query) {
        throw new Error('Please enter a question in Wolof');
    }

    try {
        console.log('Starting query processing...');
        resetUI(elements);
        setLoadingState(true, elements);

        const response = await fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({
                error: `Server error: ${response.status}`
            }));
            throw new Error(errorData.error || 'An unknown error occurred');
        }

        const data = await response.json();
        validateResponseData(data);
        await displayResults(data, elements);
        elements.resultsSection.classList.add('visible');
        
    } catch (error) {
        console.error('Error during query processing:', error);
        throw error;
    } finally {
        setLoadingState(false, elements);
    }
}

function validateResponseData(data) {
    if (!data || typeof data !== 'object') {
        throw new Error('Invalid response data: Expected an object');
    }

    const requiredFields = ['original_query', 'french_query', 'french_response', 'wolof_response'];
    const missingFields = requiredFields.filter(field => !data[field]);
    
    if (missingFields.length > 0) {
        throw new Error(`Invalid response format: missing fields: ${missingFields.join(', ')}`);
    }
}

async function displayResults(data, elements) {
    if (!elements?.resultElements) {
        throw new Error('Result elements not available');
    }

    const updates = {
        originalQuery: data.original_query,
        frenchQuery: data.french_query,
        frenchResponse: data.french_response,
        wolofResponse: data.wolof_response
    };

    for (const [key, value] of Object.entries(updates)) {
        const element = elements.resultElements[key];
        if (element) {
            element.textContent = value || 'No response available';
        }
    }
}

function showError(message, elements) {
    if (!elements?.errorElement) {
        console.error('Error element not available');
        return;
    }

    elements.errorElement.textContent = message;
    elements.errorElement.classList.add('visible');
    elements.resultsSection?.classList.remove('visible');
}

function setLoadingState(isLoading, elements) {
    if (!elements?.submitButton || !elements?.spinner) {
        console.error('Loading state elements not available');
        return;
    }
    
    elements.submitButton.disabled = isLoading;
    elements.spinner.classList.toggle('visible', isLoading);
}

function resetUI(elements) {
    if (!elements?.errorElement || !elements?.resultsSection) {
        throw new Error('Reset UI elements not available');
    }
    
    elements.errorElement.classList.remove('visible');
    elements.resultsSection.classList.remove('visible');
}
