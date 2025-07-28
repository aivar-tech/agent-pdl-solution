// ========== UI Section Info ===========
const sectionTooltips = {
  'problem_statement': 'What is the core problem and context?',
  'goals_and_success_metrics': 'List of goals with a measurable success metric for each.',
  'user_stories': 'User stories, each with a role and story.',
  'constraints': 'Any technical, legal, or business constraints.',
  'milestones': 'Key implementation milestones and target dates.',
  'hypothesis': 'Hypothesis statement.',
  'rationale': 'Reasoning behind the hypothesis.',
  'test': 'How to test/validate the hypothesis.'
};

const agentMeta = {
  scope_document: {
    label: 'Scoping Agent',
    icon: '🧭',
    cardId: 'scope-card'
  },
  data_analysis: {
    label: 'Data Analysis Agent',
    icon: '📊',
    cardId: 'data-card'
  },
  hypotheses: {
    label: 'Hypothesis Generation Agent',
    icon: '💡',
    cardId: 'hypo-card'
  },
  hypothesis_test_results: {
    label: 'Hypothesis Testing Agent',
    icon: '🧪',
    cardId: 'hypo-test-card'
  }
};

// ========== Section Accordion Renderer ===========
function renderSectionAccordion(sectionKey, value) {
  const tooltip = sectionTooltips[sectionKey] ? `<span class="tooltip" title="${sectionTooltips[sectionKey]}">ⓘ</span>` : '';
  let contentHtml = '';
  if (Array.isArray(value)) {
    if (value.length === 0) {
      contentHtml = '<div class="section-content">(None)</div>';
    } else if (typeof value[0] === 'object') {
      // List of objects
      contentHtml = '<div class="section-content section-list">';
      value.forEach((obj, idx) => {
        contentHtml += '<div style="margin-bottom:0.7em;">';
        Object.entries(obj).forEach(([k, v]) => {
          contentHtml += `<div><b>${k.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}:</b> <span style="white-space:pre-line;">${v}</span></div>`;
        });
        contentHtml += '</div>';
      });
      contentHtml += '</div>';
    } else {
      // List of strings
      contentHtml = '<ul class="section-content section-list">' + value.map(v => `<li>${v}</li>`).join('') + '</ul>';
    }
  } else if (typeof value === 'object' && value !== null) {
    contentHtml = '<div class="section-content">';
    Object.entries(value).forEach(([k, v]) => {
      if (typeof v === 'object' && v !== null) {
        // For nested objects like hypothesis test results
        contentHtml += `<div class="nested-object"><b>${k.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}:</b>`;
        contentHtml += '<div class="nested-content">';
        Object.entries(v).forEach(([subK, subV]) => {
          // Special formatting for status field in hypothesis testing
          if (subK === 'status') {
            const statusClass = subV.toLowerCase().includes('support') ? 'status-supported' : 
                              subV.toLowerCase().includes('contradict') ? 'status-contradicted' : 'status-insufficient';
            contentHtml += `<div><b>${subK.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}:</b> <span class="${statusClass}">${subV}</span></div>`;
          } else if (subK === 'confidence') {
            // Format confidence as percentage with color coding
            const confidenceValue = parseInt(subV);
            const confidenceClass = confidenceValue >= 70 ? 'confidence-high' : 
                                   confidenceValue >= 40 ? 'confidence-medium' : 'confidence-low';
            contentHtml += `<div><b>${subK.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}:</b> <span class="${confidenceClass}">${confidenceValue}%</span></div>`;
          } else {
            contentHtml += `<div><b>${subK.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}:</b> <span style="white-space:pre-line;">${subV}</span></div>`;
          }
        });
        contentHtml += '</div></div>';
      } else {
        contentHtml += `<div><b>${k.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}:</b> <span style="white-space:pre-line;">${v}</span></div>`;
      }
    });
    contentHtml += '</div>';
  } else {
    contentHtml = `<div class="section-content">${value ? value : '(None)'}</div>`;
  }
  return `
    <div class="section-accordion">
      <div class="section-header" tabindex="0" role="button" aria-expanded="false">
        <span>${sectionKey.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}</span>
        ${tooltip}
        <span class="accordion-arrow" style="margin-left:auto;">&#x25BC;</span>
      </div>
      ${contentHtml}
    </div>
  `;
}

// ========== Agent Card Renderer ===========
function renderAgentCard(agentKey, agentData) {
  const meta = agentMeta[agentKey];
  let html = `<section class="agent-card" id="${meta.cardId}">
    <div class="agent-header">
      <span class="agent-icon">${meta.icon}</span>
      <span class="agent-title">${meta.label}</span>
    </div>
  `;
  if (agentData.error) {
    html += `<div class="error-message"><b>ERROR:</b> ${agentData.error}</div>`;
  } else if (agentKey === 'hypothesis_test_results') {
    // Special handling for hypothesis test results which are stored as a JSON string
    html += '<div class="agent-sections">';
    try {
      // Try to parse the JSON string
      let testResults;
      if (typeof agentData === 'string') {
        // Extract the JSON part from the string
        // Look for the pattern where JSON starts (after any text and newlines)
        const jsonMatch = agentData.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          // Parse the extracted JSON
          testResults = JSON.parse(jsonMatch[0]);
        } else {
          // If no JSON pattern found, try parsing the whole string
          testResults = JSON.parse(agentData);
        }
      } else if (typeof agentData === 'object') {
        // If it's already an object, use it directly
        testResults = agentData;
      }
      
      if (testResults) {
        Object.entries(testResults).forEach(([k, v]) => {
          html += renderSectionAccordion(k, v);
        });
      }
    } catch (err) {
      console.error('Error parsing hypothesis test results:', err);
      // Fallback to displaying as text if parsing fails
      html += `<div class="agent-output-md">${marked.parse(agentData.toString())}</div>`;
    }
    html += '</div>';
  } else if (agentData.sections) {
    html += '<div class="agent-sections">';
    if (Array.isArray(agentData.sections)) {
      // List of objects (for hypotheses)
      agentData.sections.forEach((obj, idx) => {
        html += renderSectionAccordion(`Hypothesis ${idx+1}`, obj);
      });
    } else if (typeof agentData.sections === 'object') {
      Object.entries(agentData.sections).forEach(([k, v]) => {
        html += renderSectionAccordion(k, v);
      });
    }
    html += '</div>';
  } else if (agentData.markdown) {
    // Render markdown output if present
    html += `<div class="agent-output-md">${marked.parse(agentData.markdown)}</div>`;
  } else if (agentData.text) {
    // Fallback: treat as markdown for rich formatting
    html += `<div class="agent-output-md">${marked.parse(agentData.text)}</div>`;
  }
  html += '</section>';
  return html;
}

// ========== Workflow Submission ===========
async function submitWorkflow() {
  const brief = document.getElementById('brief').value;
  const rawData = document.getElementById('raw_data').value;
  const resultDiv = document.getElementById('result');
  resultDiv.innerHTML = `
    <div style="padding:2em;text-align:center;">
      <div class="loading-spinner"></div>
      <div style="font-size:1.2em;color:#0f3d91;margin-top:1em;">Submitting request...</div>
    </div>
  `;

  try {
    const response = await fetch('/api/workflow', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ brief, raw_data: rawData })
    });
    const data = await response.json();
    if (data.error) {
      resultDiv.innerHTML = `<div class="error-message">${data.error}</div>`;
    } else {
      // Show pending status
      resultDiv.innerHTML = `
        <div style="padding:2em;">
          <h3>Request Submitted</h3>
          <p>Request ID: ${data.request_id}</p>
          <p>Status: <span class="status-badge status-${data.status}">${data.status.toUpperCase()}</span></p>
          <p>Your request is being processed. Results will appear here when ready.</p>
          <div class="progress-indicator"><div class="progress-bar"></div></div>
        </div>
      `;
      
      // Refresh executions list
      loadExecutions();
      
      // Start polling for results
      pollExecutionStatus(data.request_id);
      
      // Smooth scroll to results
      setTimeout(()=>{
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 150);
    }
  } catch (err) {
    resultDiv.innerHTML = `<span style='color:red;'>${err}</span>`;
  }
}

// ========== Execution Status Polling ===========
let activePolling = null;

// Track last completed execution ID
window.lastCompletedExecutionId = null;

async function pollExecutionStatus(requestId) {
  // Cancel any existing polling
  if (activePolling) {
    clearInterval(activePolling);
  }
  
  // Start polling
  activePolling = setInterval(async () => {
    try {
      const status = await fetchExecutionStatus(requestId);
      
      // Update UI based on status
      if (status.status === 'completed' || status.status === 'failed') {
        // Stop polling when complete or failed
        clearInterval(activePolling);
        activePolling = null;
        
        // Reset all agent status indicators
        resetAllAgentStatusIndicators();
        
        // Refresh executions list
        loadExecutions();
        
        // Display results if completed
        if (status.status === 'completed' && status.results) {
          // Store the execution ID for PDF export
          window.lastCompletedExecutionId = requestId;
          displayResults(status.results);
        } else if (status.status === 'failed') {
          const resultDiv = document.getElementById('result');
          resultDiv.innerHTML = `<div class="error-message">Execution failed: ${status.error || 'Unknown error'}</div>`;
        }
      } else {
        // Update progress indicator
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = `
          <div style="padding:2em;">
            <h3>Processing Request</h3>
            <p>Request ID: ${status.request_id}</p>
            <p>Status: <span class="status-badge status-${status.status}">${status.status.toUpperCase()}</span></p>
            <p>Current step: ${status.current_step || 'Initializing...'}</p>
            <div class="progress-indicator"><div class="progress-bar"></div></div>
          </div>
        `;
        
        // Update agent status indicators based on current step
        updateAgentStatusIndicators(status.current_step);
      }
    } catch (err) {
      console.error('Error polling execution status:', err);
    }
  }, 2000); // Poll every 2 seconds
}

async function fetchExecutionStatus(requestId) {
  const response = await fetch(`/api/workflow/${requestId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch execution status: ${response.statusText}`);
  }
  return await response.json();
}

// ========== Agent Status Indicators ===========
function updateAgentStatusIndicators(currentStep) {
  // Reset all indicators first
  resetAllAgentStatusIndicators();
  
  // Map the current step to the corresponding agent
  const step = currentStep ? currentStep.toLowerCase() : '';
  
  if (step.includes('scoping') || step.includes('analyzing brief')) {
    setAgentStatusActive('nav-scope');
  } else if (step.includes('data') || step.includes('analyzing data')) {
    setAgentStatusActive('nav-data');
  } else if (step.includes('hypothesis') || step.includes('generating hypotheses')) {
    setAgentStatusActive('nav-hypo');
  } else if (step.includes('testing') || step.includes('evaluating hypotheses')) {
    setAgentStatusActive('nav-test');
  }
}

function setAgentStatusActive(agentId) {
  const agentElement = document.getElementById(agentId);
  if (agentElement) {
    const statusIndicator = agentElement.querySelector('.agent-status');
    if (statusIndicator) {
      statusIndicator.classList.add('active');
      
      // Add pulsing animation
      statusIndicator.style.backgroundColor = '#F1C93B'; // Gold color for active agent
      statusIndicator.style.boxShadow = '0 0 10px rgba(241, 201, 59, 0.7)'; // Glow effect
    }
  }
}

function resetAllAgentStatusIndicators() {
  const agentElements = document.querySelectorAll('.agent-link');
  agentElements.forEach(agent => {
    const statusIndicator = agent.querySelector('.agent-status');
    if (statusIndicator) {
      statusIndicator.classList.remove('active');
      statusIndicator.style.backgroundColor = ''; // Reset to default
      statusIndicator.style.boxShadow = ''; // Reset glow effect
    }
  });
}

// ========== Display Results ===========
function displayResults(results) {
  const resultDiv = document.getElementById('result');
  let html = '';
  
  // Show export button when results are displayed
  document.getElementById('export-pdf-btn').style.display = 'flex';
  
  Object.keys(agentMeta).forEach(agentKey => {
    if (results[agentKey]) {
      html += renderAgentCard(agentKey, results[agentKey]);
    }
  });
  
  resultDiv.innerHTML = html;
  
  // Initialize accordions
  initAccordions();
  
  // Reset all agent status indicators when results are displayed
  resetAllAgentStatusIndicators();
}

// ========== Load Executions ===========
async function loadExecutions() {
  const executionsListDiv = document.getElementById('executions-list');
  
  try {
    const response = await fetch('/api/workflows');
    if (!response.ok) {
      throw new Error(`Failed to fetch executions: ${response.statusText}`);
    }
    
    const executions = await response.json();
    
    if (executions.length === 0) {
      executionsListDiv.innerHTML = '<div class="loading-text">No executions found</div>';
      return;
    }
    
    let html = '';
    executions.forEach(execution => {
      // Format the brief for display (truncate if too long)
      const briefDisplay = execution.brief.length > 30 ? 
        execution.brief.substring(0, 30) + '...' : 
        execution.brief;
      
      // Format the date
      const date = new Date(execution.created_at);
      const dateStr = `${date.toLocaleDateString()} ${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
      
      html += `
        <div class="execution-item" data-id="${execution.request_id}">
          <div class="execution-title">${briefDisplay}</div>
          <div class="execution-status">
            <span class="status-indicator status-${execution.status}"></span>
            ${execution.status} - ${dateStr}
          </div>
        </div>
      `;
    });
    
    executionsListDiv.innerHTML = html;
    
    // Add click event listeners to execution items
    document.querySelectorAll('.execution-item').forEach(item => {
      item.addEventListener('click', () => {
        // Remove selected class from all items
        document.querySelectorAll('.execution-item').forEach(i => {
          i.classList.remove('selected');
        });
        
        // Add selected class to clicked item
        item.classList.add('selected');
        
        // Load the execution
        const requestId = item.dataset.id;
        loadExecution(requestId);
      });
    });
    
  } catch (err) {
    executionsListDiv.innerHTML = `<div class="loading-text">Error loading executions: ${err.message}</div>`;
    console.error('Error loading executions:', err);
  }
}

async function loadExecution(requestId) {
  const resultDiv = document.getElementById('result');
  resultDiv.innerHTML = `
    <div style="padding:2em;text-align:center;">
      <div class="loading-spinner"></div>
      <div style="font-size:1.2em;color:#0f3d91;margin-top:1em;">Loading execution results...</div>
    </div>
  `;
  
  try {
    const status = await fetchExecutionStatus(requestId);
    
    if (status.status === 'completed' && status.results) {
      // Display completed results
      displayResults(status.results);
    } else if (status.status === 'failed') {
      // Display error
      resultDiv.innerHTML = `<div class="error-message">Execution failed: ${status.error || 'Unknown error'}</div>`;
    } else {
      // Display in-progress status and start polling
      resultDiv.innerHTML = `
        <div style="padding:2em;">
          <h3>Processing Request</h3>
          <p>Request ID: ${status.request_id}</p>
          <p>Status: <span class="status-badge status-${status.status}">${status.status.toUpperCase()}</span></p>
          <p>Current step: ${status.current_step || 'Initializing...'}</p>
          <div class="progress-indicator"><div class="progress-bar"></div></div>
        </div>
      `;
      
      // Start polling for updates
      pollExecutionStatus(requestId);
    }
    
  } catch (err) {
    resultDiv.innerHTML = `<div class="error-message">Error loading execution: ${err.message}</div>`;
    console.error('Error loading execution:', err);
  }
}

// ========== Example Templates ===========
const templates = [
  {
    label: "Launch new Rummy Tournament (Games24x7)",
    brief: "Launch a new real-money online rummy tournament format for Games24x7.",
    data: "Historical tournaments show peak engagement during weekends and holidays. Previous format changes impacted retention by +10%."
  },
  {
    label: "AI-Powered Game Recommendations (Games24x7)",
    brief: "Add AI-powered personalized game recommendations to the Games24x7 app.",
    data: "User segmentation and session data available. Prior recommendation attempts had limited uplift (3-5%)."
  },
  {
    label: "Gametech: Real-time Anti-Fraud System",
    brief: "Implement a real-time fraud detection system for digital gaming transactions.",
    data: "Recent spike in suspicious withdrawal patterns. Current rules-based system has 8% false positive."
  },
  {
    label: "Gametech: LiveOps Event Automation",
    brief: "Automate LiveOps event scheduling and reward distribution for multiplayer games.",
    data: "Manual events require 10+ hours/week. Engagement increases 12% during well-timed events."
  }
];

const examplesPanel = document.getElementById('examples-panel');

function renderExampleCards() {
  examplesPanel.innerHTML = '';
  templates.forEach((tpl, idx) => {
    const card = document.createElement('div');
    card.className = 'example-card';
    card.tabIndex = 0;
    card.setAttribute('role', 'button');
    card.setAttribute('aria-label', tpl.label);
    card.innerHTML = `
      <div class="example-title">${tpl.label}</div>
      <div class="example-brief"><b>Brief:</b> ${tpl.brief}</div>
      <div class="example-data"><b>Data:</b> ${tpl.data}</div>
    `;
    card.addEventListener('click', () => selectTemplate(idx));
    card.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') selectTemplate(idx); });
    examplesPanel.appendChild(card);
  });
}

function selectTemplate(idx) {
  // Highlight selected card
  Array.from(document.getElementsByClassName('example-card')).forEach((el, i) => {
    el.classList.toggle('active', i === idx);
  });
  // Fill form
  document.getElementById('brief').value = templates[idx].brief;
}

// ========== Initialize Accordions ===========
function initAccordions() {
  document.querySelectorAll('.section-header').forEach(header => {
    header.addEventListener('click', function() {
      this.classList.toggle('active');
      this.setAttribute('aria-expanded', this.classList.contains('active'));
      const content = this.nextElementSibling;
      if (content.style.maxHeight) {
        content.style.maxHeight = null;
      } else {
        content.style.maxHeight = content.scrollHeight + 'px';
      }
      const arrow = this.querySelector('.accordion-arrow');
      if (arrow) {
        arrow.style.transform = this.classList.contains('active') ? 'rotate(180deg)' : '';
      }
    });
  });
}

// ========== PDF Export Functionality ===========
async function exportToPDF() {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF('p', 'mm', 'a4');
  const resultSection = document.getElementById('result');
  const exportBtn = document.getElementById('export-pdf-btn');
  
  // Show loading state
  const originalBtnText = exportBtn.innerHTML;
  exportBtn.innerHTML = 'Generating PDF...';
  exportBtn.disabled = true;
  
  try {
    // Get execution ID from URL or current state
    const executionId = getCurrentExecutionId();
    const title = `Aivar Product Analysis - ${new Date().toLocaleDateString()}`;
    
    // Add title
    doc.setFontSize(18);
    doc.setTextColor(75, 86, 210); // Aivar blue
    doc.text(title, 20, 20);
    doc.setLineWidth(0.5);
    doc.setDrawColor(130, 38, 158); // Aivar purple
    doc.line(20, 25, 190, 25);
    
    // Add timestamp and execution ID
    doc.setFontSize(10);
    doc.setTextColor(100, 100, 100);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 20, 33);
    doc.text(`Execution ID: ${executionId || 'N/A'}`, 20, 38);
    
    let yPosition = 45;
    const pageWidth = doc.internal.pageSize.getWidth();
    
    // Process each agent card
    const agentCards = resultSection.querySelectorAll('.agent-card');
    for (const card of agentCards) {
      // Capture the agent card as an image
      const canvas = await html2canvas(card, {
        scale: 2, // Higher resolution
        logging: false,
        useCORS: true
      });
      
      const imgData = canvas.toDataURL('image/png');
      const imgWidth = pageWidth - 40; // 20mm margins on each side
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      
      // Add new page if content won't fit
      if (yPosition + imgHeight > doc.internal.pageSize.getHeight() - 20) {
        doc.addPage();
        yPosition = 20;
      }
      
      // Add the image to the PDF
      doc.addImage(imgData, 'PNG', 20, yPosition, imgWidth, imgHeight);
      yPosition += imgHeight + 15; // Add some spacing between cards
    }
    
    // Add footer
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(150, 150, 150);
      doc.text(`Page ${i} of ${pageCount} - Powered by Aivar`, pageWidth / 2, doc.internal.pageSize.getHeight() - 10, { align: 'center' });
    }
    
    // Save the PDF
    doc.save(`aivar-product-analysis-${executionId || 'results'}.pdf`);
  } catch (err) {
    console.error('Error generating PDF:', err);
    alert('Failed to generate PDF. Please try again.');
  } finally {
    // Restore button state
    exportBtn.innerHTML = originalBtnText;
    exportBtn.disabled = false;
  }
}

// Get current execution ID from various possible sources
function getCurrentExecutionId() {
  // Try to get from URL if available
  const urlParams = new URLSearchParams(window.location.search);
  const idFromUrl = urlParams.get('execution');
  if (idFromUrl) return idFromUrl;
  
  // Try to get from selected execution in sidebar
  const selectedExecution = document.querySelector('.execution-item.selected');
  if (selectedExecution) return selectedExecution.dataset.id;
  
  // Try to get from last completed execution status
  return window.lastCompletedExecutionId || null;
}

// ========== Document Ready ===========
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('submit-btn').addEventListener('click', submitWorkflow);
  
  // Initialize PDF export button
  document.getElementById('export-pdf-btn').addEventListener('click', exportToPDF);
  
  renderExampleCards();
  
  // Load executions list
  loadExecutions();
  
  // Initialize accordions
  initAccordions();
});