class MCPClient {
    constructor() {
        this.serverUrl = process.env.NODE_ENV === 'production' 
            ? 'https://your-mcp-server.railway.app' 
            : 'http://localhost:8000';
        this.isConnected = false;
        this.init();
    }

    async init() {
        await this.connect();
        this.setupEventListeners();
        this.loadInitialData();
    }

    async connect() {
        try {
            const response = await fetch(`${this.serverUrl}/health`);
            this.isConnected = response.ok;
            this.updateConnectionStatus();
        } catch (error) {
            console.error('Failed to connect to MCP server:', error);
            this.isConnected = false;
            this.updateConnectionStatus();
        }
    }

    updateConnectionStatus() {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = this.isConnected ? 'Connected' : 'Disconnected';
            statusElement.className = this.isConnected ? 'status connected' : 'status disconnected';
        }
    }

    setupEventListeners() {
        const queryForm = document.getElementById('query-form');
        const queryInput = document.getElementById('query-input');
        const exampleQueries = document.querySelectorAll('.example-query');

        queryForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const query = queryInput.value.trim();
            if (query) {
                this.executeQuery(query);
            }
        });

        exampleQueries.forEach(example => {
            example.addEventListener('click', () => {
                queryInput.value = example.textContent;
                this.executeQuery(example.textContent);
            });
        });

        // Auto-resize textarea
        queryInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }

    async executeQuery(query) {
        this.showLoading(true);
        this.addMessage('user', query);

        try {
            const response = await fetch(`${this.serverUrl}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.handleQueryResponse(data);
        } catch (error) {
            console.error('Query failed:', error);
            this.addMessage('error', `Query failed: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    handleQueryResponse(data) {
        if (data.error) {
            this.addMessage('error', data.error);
            return;
        }

        // Add text response
        if (data.response) {
            this.addMessage('assistant', data.response);
        }

        // Add data visualization if available
        if (data.data && data.data.length > 0) {
            this.addDataVisualization(data);
        }

        // Add SQL query if available
        if (data.sql_query) {
            this.addSQLQuery(data.sql_query);
        }
    }

    addMessage(type, content) {
        const messagesContainer = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const timestamp = new Date().toLocaleTimeString();
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-type">${type === 'user' ? 'You' : type === 'assistant' ? 'AI Assistant' : 'Error'}</span>
                <span class="timestamp">${timestamp}</span>
            </div>
            <div class="message-content">${this.formatContent(content)}</div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    addDataVisualization(data) {
        const messagesContainer = document.getElementById('messages');
        const vizDiv = document.createElement('div');
        vizDiv.className = 'message assistant';
        
        const timestamp = new Date().toLocaleTimeString();
        
        // Create table for data
        let tableHTML = '<div class="data-table"><table><thead><tr>';
        
        if (data.data.length > 0) {
            Object.keys(data.data[0]).forEach(key => {
                tableHTML += `<th>${key}</th>`;
            });
            tableHTML += '</tr></thead><tbody>';
            
            data.data.slice(0, 10).forEach(row => { // Limit to 10 rows for display
                tableHTML += '<tr>';
                Object.values(row).forEach(value => {
                    tableHTML += `<td>${value}</td>`;
                });
                tableHTML += '</tr>';
            });
            tableHTML += '</tbody></table></div>';
            
            if (data.data.length > 10) {
                tableHTML += `<p class="data-note">Showing first 10 of ${data.data.length} results</p>`;
            }
        }
        
        vizDiv.innerHTML = `
            <div class="message-header">
                <span class="message-type">Data Results</span>
                <span class="timestamp">${timestamp}</span>
            </div>
            <div class="message-content">
                ${tableHTML}
            </div>
        `;
        
        messagesContainer.appendChild(vizDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    addSQLQuery(sqlQuery) {
        const messagesContainer = document.getElementById('messages');
        const sqlDiv = document.createElement('div');
        sqlDiv.className = 'message sql-query';
        
        const timestamp = new Date().toLocaleTimeString();
        
        sqlDiv.innerHTML = `
            <div class="message-header">
                <span class="message-type">Generated SQL</span>
                <span class="timestamp">${timestamp}</span>
            </div>
            <div class="message-content">
                <pre><code class="sql">${sqlQuery}</code></pre>
            </div>
        `;
        
        messagesContainer.appendChild(sqlDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    formatContent(content) {
        // Basic markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    showLoading(show) {
        const loadingElement = document.getElementById('loading');
        const submitButton = document.querySelector('#query-form button[type="submit"]');
        
        if (loadingElement) {
            loadingElement.style.display = show ? 'block' : 'none';
        }
        
        if (submitButton) {
            submitButton.disabled = show;
            submitButton.textContent = show ? 'Processing...' : 'Ask Question';
        }
    }

    async loadInitialData() {
        try {
            const response = await fetch(`${this.serverUrl}/schema`);
            if (response.ok) {
                const schema = await response.json();
                this.displaySchema(schema);
            }
        } catch (error) {
            console.error('Failed to load schema:', error);
        }
    }

    displaySchema(schema) {
        const schemaContainer = document.getElementById('schema-info');
        if (schemaContainer && schema.tables) {
            let schemaHTML = '<h3>Available Data</h3>';
            
            Object.entries(schema.tables).forEach(([tableName, columns]) => {
                schemaHTML += `
                    <div class="table-info">
                        <h4>${tableName}</h4>
                        <ul>
                            ${columns.map(col => `<li>${col}</li>`).join('')}
                        </ul>
                    </div>
                `;
            });
            
            schemaContainer.innerHTML = schemaHTML;
        }
    }
}

// Initialize the MCP client when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.mcpClient = new MCPClient();
});

// Example queries functionality
const exampleQueries = [
    "What's our total sales revenue this year?",
    "Which products have the highest profit margins?",
    "Show me customer churn rate by region",
    "What are the top 5 selling products?",
    "How do sales compare month over month?",
    "Which customers have the highest lifetime value?",
    "What's the average order value by product category?",
    "Show me sales performance by sales rep"
];

// Add example queries to the page
document.addEventListener('DOMContentLoaded', () => {
    const examplesContainer = document.getElementById('example-queries');
    if (examplesContainer) {
        examplesContainer.innerHTML = exampleQueries
            .map(query => `<button class="example-query">${query}</button>`)
            .join('');
    }
});