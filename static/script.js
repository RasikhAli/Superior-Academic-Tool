

// Get username/computer info
function getUserInfo() {
    // Due to browser security restrictions, we cannot access:
    // - Computer name
    // - Windows username
    // - Logged-in account information
    return 'Rasikh Ali';
}

// Update welcome message
function updateWelcomeMessage() {
    const welcomeElement = document.querySelector('.top-nav .text-muted');
    if (welcomeElement) {
        const userInfo = getUserInfo();
        welcomeElement.textContent = `Developed By, ${userInfo}`+`\u00A0\u00A0`;
    }
}

// Initialize on page load
$(document).ready(function() {
    // Update welcome message
    updateWelcomeMessage();
    
    // Initialize Select2 for better dropdowns
    $('#teacher-search').select2({
        placeholder: "Search for a teacher...",
        allowClear: true,
        width: '100%'
    });
    
    $('#section-search').select2({
        placeholder: "Search for a section...",
        allowClear: true,
        width: '100%'
    });
    
    $('#subject-select').select2({
        placeholder: "Search for a subject...",
        allowClear: true,
        width: '100%'
    });
    
    $('#section-select-custom').select2({
        placeholder: "Choose a section...",
        allowClear: true,
        width: '100%'
    });
    
    // Load sections for section timetable and update dashboard
    loadSections();
    
    // Load subjects for custom schedule
    loadSubjects();
    
    // Load all teacher timetables initially
    loadAllTeacherTimetables();
});

// Sidebar functionality
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
}

// Close sidebar when clicking overlay
document.getElementById('overlay').addEventListener('click', function() {
    toggleSidebar();
});

// Section navigation
function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(sectionId).classList.add('active');
    
    // Update sidebar active state
    const menuItems = document.querySelectorAll('.sidebar-menu a');
    menuItems.forEach(item => {
        item.classList.remove('active');
    });
    
    // Find and activate the clicked menu item
    event.target.classList.add('active');
    
    // Close sidebar on mobile
    if (window.innerWidth <= 768) {
        toggleSidebar();
    }
}

// Theme toggle functionality
function toggleTheme() {
    const body = document.body;
    const html = document.documentElement;
    const themeIcon = document.getElementById('theme-icon');
    
    if (body.getAttribute('data-bs-theme') === 'dark') {
        body.setAttribute('data-bs-theme', 'light');
        html.setAttribute('data-bs-theme', 'light');
        themeIcon.className = 'fas fa-moon';
        localStorage.setItem('theme', 'light');
    } else {
        body.setAttribute('data-bs-theme', 'dark');
        html.setAttribute('data-bs-theme', 'dark');
        themeIcon.className = 'fas fa-sun';
        localStorage.setItem('theme', 'dark');
    }
}

// Load saved theme
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const body = document.body;
    const html = document.documentElement;
    const themeIcon = document.getElementById('theme-icon');
    
    body.setAttribute('data-bs-theme', savedTheme);
    html.setAttribute('data-bs-theme', savedTheme);
    themeIcon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
}

// Load theme on page load
document.addEventListener('DOMContentLoaded', loadTheme);

// Load sections from server and update dashboard count
function loadSections() {
    fetch('/get_sections')
        .then(response => response.json())
        .then(sections => {
            const sectionSelect = document.getElementById('section-search');
            sectionSelect.innerHTML = '<option value="">Select a section...</option>';
            
            sections.forEach(section => {
                const option = document.createElement('option');
                option.value = section;
                option.textContent = section;
                sectionSelect.appendChild(option);
            });
            
            // Update dashboard section count
            const sectionCountElement = document.getElementById('section-count');
            if (sectionCountElement) {
                sectionCountElement.textContent = `${sections.length} Sections`;
            }
            
            // Refresh Select2
            $('#section-search').trigger('change');
        })
        .catch(error => {
            // console.error('Error loading sections:', error);
            const sectionCountElement = document.getElementById('section-count');
            if (sectionCountElement) {
                sectionCountElement.textContent = 'Error loading';
            }
        });
}

// Sort entries by day and time
function sortEntriesByDayAndTime(entries) {
    const dayOrder = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    
    return entries.sort((a, b) => {
        // First sort by day
        const dayA = dayOrder.indexOf(a.day);
        const dayB = dayOrder.indexOf(b.day);
        
        if (dayA !== dayB) {
            return dayA - dayB;
        }
        
        // Then sort by start time
        const timeA = timeToMinutes(a.start_time);
        const timeB = timeToMinutes(b.start_time);
        
        return timeA - timeB;
    });
}

// Convert time string to minutes for sorting
function timeToMinutes(timeStr) {
    if (!timeStr) return 0;
    
    const parts = timeStr.split(':');
    if (parts.length !== 2) return 0;
    
    let hours = parseInt(parts[0]) || 0;
    const minutes = parseInt(parts[1]) || 0;
    
    // Handle 12-hour format without AM/PM indicators
    // Assume times 1-7 are PM (13-19), times 8-12 are AM (8-12)
    if (hours >= 1 && hours <= 7) {
        hours += 12; // Convert to 24-hour format (1 PM = 13, 2 PM = 14, etc.)
    }
    
    return hours * 60 + minutes;
}

// Load all teacher timetables
function loadAllTeacherTimetables() {
    const container = document.getElementById('teacher-timetable-container');
    container.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin fa-2x"></i><p>Loading all timetables...</p></div>';
    
    fetch('/timetable?type=teacher')
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                container.innerHTML = '<div class="text-center text-muted"><i class="fas fa-info-circle fa-2x mb-3"></i><p>No timetables found.</p></div>';
                return;
            }
            
            // Group data by teacher, but filter out combined teacher entries
            const teacherGroups = {};
            data.forEach(entry => {
                const teacherName = entry.teachers;
                // Skip entries where teacher name contains commas (combined teachers)
                if (!teacherName.includes(',')) {
                    if (!teacherGroups[teacherName]) {
                        teacherGroups[teacherName] = [];
                    }
                    teacherGroups[teacherName].push(entry);
                }
            });
            
            let html = '';
            Object.keys(teacherGroups).sort().forEach(teacher => {
                // Sort each teacher's data and remove duplicates
                const sortedData = sortEntriesByDayAndTime(teacherGroups[teacher]);
                const uniqueData = removeDuplicateEntries(sortedData);
                html += generateTeacherTimetableHTML(teacher, uniqueData);
            });
            
            container.innerHTML = html;
        })
        .catch(error => {
            // console.error('Error loading all timetables:', error);
            container.innerHTML = '<div class="text-center text-danger"><i class="fas fa-exclamation-triangle fa-2x mb-3"></i><p>Error loading timetables. Please try again.</p></div>';
        });
}

// Generate teacher timetable HTML
function generateTeacherTimetableHTML(teacherName, data) {
    let html = `
        <div class="teacher-timetable" id="${teacherName.replace(/[^a-zA-Z0-9]/g, '_')}">
            <div class="card">
                <h5 class="card-title"><i class="fas fa-user-tie"></i>${teacherName}</h5>
                <div class="table-container">
                    <div class="table-responsive">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th><i class="fas fa-calendar-day mr-2"></i>Day</th>
                                    <th><i class="fas fa-clock mr-2"></i>Start Time</th>
                                    <th><i class="fas fa-clock mr-2"></i>End Time</th>
                                    <th><i class="fas fa-map-marker-alt mr-2"></i>Location</th>
                                    <th><i class="fas fa-book mr-2"></i>Subject</th>
                                    <th><i class="fas fa-users mr-2"></i>Groups</th>
                                </tr>
                            </thead>
                            <tbody>
    `;
    
    data.forEach(entry => {
        // Format groups properly
        let groupsDisplay = '';
        if (Array.isArray(entry.groups)) {
            groupsDisplay = entry.groups.join(', ');
        } else {
            groupsDisplay = entry.groups || '';
        }
        
        html += `
            <tr>
                <td>${entry.day}</td>
                <td>${entry.start_time}</td>
                <td>${entry.end_time}</td>
                <td>${entry.location}</td>
                <td>${entry.subject}</td>
                <td>${groupsDisplay}</td>
            </tr>
        `;
    });
    
    html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return html;
}

// Load teacher timetable
function loadTeacherTimetable() {
    const teacherName = document.getElementById('teacher-search').value;
    const container = document.getElementById('teacher-timetable-container');
    
    if (!teacherName) {
        loadAllTeacherTimetables();
        return;
    }
    
    // Show loading
    container.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin fa-2x"></i><p>Loading timetable...</p></div>';
    
    fetch(`/timetable?name=${encodeURIComponent(teacherName)}&type=teacher`)
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                container.innerHTML = '<div class="text-center text-muted"><i class="fas fa-info-circle fa-2x mb-3"></i><p>No timetable found for this teacher.</p></div>';
                return;
            }
            
            // Sort the data and remove duplicates
            const sortedData = sortEntriesByDayAndTime(data);
            const uniqueData = removeDuplicateEntries(sortedData);
            container.innerHTML = generateTeacherTimetableHTML(teacherName, uniqueData);
        })
        .catch(error => {
            // console.error('Error loading teacher timetable:', error);
            container.innerHTML = '<div class="text-center text-danger"><i class="fas fa-exclamation-triangle fa-2x mb-3"></i><p>Error loading timetable. Please try again.</p></div>';
        });
}

// Load section timetable
function loadSectionTimetable() {
    const sectionName = document.getElementById('section-search').value;
    const container = document.getElementById('section-timetable-container');
    
    if (!sectionName) {
        container.innerHTML = '<div class="text-center text-muted"><i class="fas fa-info-circle fa-2x mb-3"></i><p>Please select a section to view its timetable.</p></div>';
        return;
    }
    
    // Show loading
    container.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin fa-2x"></i><p>Loading timetable...</p></div>';
    
    fetch(`/timetable?name=${encodeURIComponent(sectionName)}&type=section`)
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                container.innerHTML = '<div class="text-center text-muted"><i class="fas fa-info-circle fa-2x mb-3"></i><p>No timetable found for this section.</p></div>';
                return;
            }
            
            // Sort the data and remove duplicates with merging
            const sortedData = sortEntriesByDayAndTime(data);
            const uniqueData = removeDuplicateEntries(sortedData);
            
            // Generate HTML for the timetable
            let html = `
                <div class="section-timetable">
                    <div class="card">
                        <h5 class="card-title"><i class="fas fa-users"></i>${sectionName}</h5>
                        <div class="table-container">
                            <div class="table-responsive">
                                <table class="table">
                                    <thead>
                                        <tr>
                                            <th><i class="fas fa-calendar-day mr-2"></i>Day</th>
                                            <th><i class="fas fa-clock mr-2"></i>Start Time</th>
                                            <th><i class="fas fa-clock mr-2"></i>End Time</th>
                                            <th><i class="fas fa-map-marker-alt mr-2"></i>Location</th>
                                            <th><i class="fas fa-book mr-2"></i>Subject</th>
                                            <th><i class="fas fa-chalkboard-teacher mr-2"></i>Teacher</th>
                                        </tr>
                                    </thead>
                                    <tbody>
            `;
            
            uniqueData.forEach(entry => {
                html += `
                    <tr>
                        <td>${entry.day}</td>
                        <td>${entry.start_time}</td>
                        <td>${entry.end_time}</td>
                        <td>${entry.location}</td>
                        <td>${entry.subject}</td>
                        <td>${entry.teachers}</td>
                    </tr>
                `;
            });
            
            html += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            container.innerHTML = html;
        })
        .catch(error => {
            // console.error('Error loading section timetable:', error);
            container.innerHTML = '<div class="text-center text-danger"><i class="fas fa-exclamation-triangle fa-2x mb-3"></i><p>Error loading timetable. Please try again.</p></div>';
        });
}

// Clear selections
function clearTeacherSelection() {
    $('#teacher-search').val(null).trigger('change');
    loadAllTeacherTimetables();
}

function clearSectionSelection() {
    $('#section-search').val(null).trigger('change');
    document.getElementById('section-timetable-container').innerHTML = '<div class="text-center text-muted"><i class="fas fa-info-circle fa-2x mb-3"></i><p>Please select a section to view its timetable.</p></div>';
}

// Loading state for buttons
function addLoadingState(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading"></span> Loading...';
    button.disabled = true;
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 2000);
}

// Remove duplicate entries and merge consecutive slots
function removeDuplicateEntries(entries) {
    // First remove exact duplicates
    const uniqueEntries = [];
    const seen = new Set();
    
    entries.forEach(entry => {
        const key = `${entry.day}-${entry.start_time}-${entry.end_time}-${entry.location}-${entry.subject}-${entry.teachers}`;
        if (!seen.has(key)) {
            seen.add(key);
            uniqueEntries.push(entry);
        }
    });
    
    // Then merge consecutive time slots
    return mergeConsecutiveSlots(uniqueEntries);
}

// Merge consecutive time slots in JavaScript
function mergeConsecutiveSlots(entries) {
    if (!entries || entries.length === 0) return [];
    
    // Sort entries first
    entries.sort((a, b) => {
        const dayOrder = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
        const dayA = dayOrder.indexOf(a.day);
        const dayB = dayOrder.indexOf(b.day);
        
        if (dayA !== dayB) return dayA - dayB;
        
        const timeA = timeToMinutes(a.start_time);
        const timeB = timeToMinutes(b.start_time);
        
        if (timeA !== timeB) return timeA - timeB;
        
        // Sort by subject, location, teachers for consistent grouping
        return (a.subject + a.location + a.teachers).localeCompare(b.subject + b.location + b.teachers);
    });
    
    const merged = [];
    let current = { ...entries[0] };
    
    for (let i = 1; i < entries.length; i++) {
        const entry = entries[i];
        
        // Check if entries can be merged
        const sameDay = current.day === entry.day;
        const sameSubject = current.subject === entry.subject;
        const sameLocation = current.location === entry.location;
        const sameTeachers = current.teachers === entry.teachers;
        const sameGroups = JSON.stringify(current.groups) === JSON.stringify(entry.groups);
        const consecutiveTime = current.end_time === entry.start_time;
        
        if (sameDay && sameSubject && sameLocation && sameTeachers && sameGroups && consecutiveTime) {
            // Merge by extending end time
            current.end_time = entry.end_time;
            // console.log(`Merged: ${current.day} ${current.start_time}-${current.end_time} ${current.subject}`);
        } else {
            // Can't merge, add current to merged list and start new
            merged.push(current);
            current = { ...entry };
        }
    }
    
    // Add the last entry
    merged.push(current);
    return merged;
}

// Custom Schedule Management
let customSchedule = [];

// Load subjects for custom schedule
function loadSubjects() {
    fetch('/get_subjects')
        .then(response => response.json())
        .then(subjects => {
            const subjectSelect = document.getElementById('subject-select');
            subjectSelect.innerHTML = '<option value="">Choose a subject...</option>';
            
            subjects.forEach(subject => {
                const option = document.createElement('option');
                option.value = subject;
                option.textContent = subject;
                subjectSelect.appendChild(option);
            });
            
            // Add event listener for subject selection
            $('#subject-select').on('change', function() {
                const selectedSubject = this.value;
                if (selectedSubject) {
                    loadSectionsForSubject(selectedSubject);
                } else {
                    clearSectionSelection();
                }
            });
        })
        .catch(error => {
            console.error('Error loading subjects:', error);
        });
}

// Load sections for a specific subject
function loadSectionsForSubject(subject) {
    const sectionSelect = document.getElementById('section-select-custom');
    const addButton = document.getElementById('add-to-schedule-btn');
    
    // Show loading state
    sectionSelect.innerHTML = '<option value="">Loading sections...</option>';
    sectionSelect.disabled = true;
    addButton.disabled = true;
    
    fetch(`/get_sections_for_subject?subject=${encodeURIComponent(subject)}`)
        .then(response => response.json())
        .then(sections => {
            sectionSelect.innerHTML = '<option value="">Choose a section...</option>';
            
            sections.forEach(section => {
                const option = document.createElement('option');
                option.value = section;
                option.textContent = section;
                sectionSelect.appendChild(option);
            });
            
            sectionSelect.disabled = false;
            $('#section-select-custom').trigger('change');
            
            // Add event listener for section selection
            $('#section-select-custom').off('change.customSchedule').on('change.customSchedule', function() {
                addButton.disabled = !this.value;
            });
        })
        .catch(error => {
            console.error('Error loading sections for subject:', error);
            sectionSelect.innerHTML = '<option value="">Error loading sections</option>';
        });
}

// Add subject to custom schedule
function addToSchedule() {
    const subject = document.getElementById('subject-select').value;
    const section = document.getElementById('section-select-custom').value;
    
    if (!subject || !section) {
        alert('Please select both subject and section.');
        return;
    }
    
    // Check if this combination already exists
    const exists = customSchedule.some(item => 
        item.subject === subject && item.section === section
    );
    
    if (exists) {
        alert('This subject-section combination is already in your schedule.');
        return;
    }
    
    // Get subject details
    fetch(`/get_subject_details?subject=${encodeURIComponent(subject)}&section=${encodeURIComponent(section)}`)
        .then(response => response.json())
        .then(details => {
            if (details.length === 0) {
                alert('No schedule found for this subject-section combination.');
                return;
            }
            
            // Add to custom schedule
            details.forEach(detail => {
                customSchedule.push(detail);
            });
            
            // Update the display
            updateCustomScheduleDisplay();
            
            // Clear selections
            $('#subject-select').val(null).trigger('change');
            $('#section-select-custom').val(null).trigger('change');
            document.getElementById('add-to-schedule-btn').disabled = true;
            
            // Enable download button
            document.getElementById('download-btn').disabled = false;
        })
        .catch(error => {
            console.error('Error getting subject details:', error);
            alert('Error adding to schedule. Please try again.');
        });
}

// Update custom schedule display
function updateCustomScheduleDisplay() {
    const container = document.getElementById('schedule-table-container');
    
    if (customSchedule.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-info-circle fa-2x mb-3"></i>
                <p>Your custom schedule will appear here. Start by adding subjects above.</p>
            </div>
        `;
        document.getElementById('download-btn').disabled = true;
        return;
    }
    
    // Sort schedule by day and time
    const sortedSchedule = sortEntriesByDayAndTime(customSchedule);
    
    // Generate HTML table
    let html = `
        <div class="table-responsive" id="schedule-table">
            <table class="table table-bordered">
                <thead class="thead-dark">
                    <tr>
                        <th><i class="fas fa-calendar-day mr-2"></i>Day</th>
                        <th><i class="fas fa-clock mr-2"></i>Time</th>
                        <th><i class="fas fa-book mr-2"></i>Subject</th>
                        <th><i class="fas fa-users mr-2"></i>Section</th>
                        <th><i class="fas fa-map-marker-alt mr-2"></i>Location</th>
                        <th><i class="fas fa-chalkboard-teacher mr-2"></i>Teacher</th>
                        <th><i class="fas fa-trash mr-2"></i>Action</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    sortedSchedule.forEach((entry, index) => {
        html += `
            <tr>
                <td>${entry.day}</td>
                <td>${entry.start_time} - ${entry.end_time}</td>
                <td>${entry.subject}</td>
                <td>${entry.section}</td>
                <td>${entry.location}</td>
                <td>${entry.teachers}</td>
                <td>
                    <button class="btn btn-sm btn-outline-danger" onclick="removeFromSchedule(${index})" title="Remove from schedule">
                        <i class="fas fa-times"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
}

// Remove item from custom schedule
function removeFromSchedule(index) {
    customSchedule.splice(index, 1);
    updateCustomScheduleDisplay();
}

// Clear entire schedule
function clearSchedule() {
    if (customSchedule.length === 0) {
        return;
    }
    
    if (confirm('Are you sure you want to clear your entire schedule?')) {
        customSchedule = [];
        updateCustomScheduleDisplay();
    }
}

// Download schedule as image
function downloadScheduleAsImage() {
    if (customSchedule.length === 0) {
        alert('Please add some subjects to your schedule first.');
        return;
    }
    
    const scheduleTable = document.getElementById('schedule-table');
    if (!scheduleTable) {
        alert('No schedule found to download.');
        return;
    }
    
    // Use html2canvas to convert the table to image
    // First, we need to load the html2canvas library
    if (typeof html2canvas === 'undefined') {
        // Load html2canvas dynamically
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
        script.onload = function() {
            captureScheduleAsImage();
        };
        document.head.appendChild(script);
    } else {
        captureScheduleAsImage();
    }
}

// Capture schedule as image using html2canvas
function captureScheduleAsImage() {
    const scheduleContainer = document.getElementById('custom-schedule-container');
    const downloadBtn = document.getElementById('download-btn');
    
    // Show loading state
    const originalText = downloadBtn.innerHTML;
    downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Generating...';
    downloadBtn.disabled = true;
    
    // Clone the schedule container to modify for image generation
    const clone = scheduleContainer.cloneNode(true);
    
    // Remove action column from the clone
    const actionCells = clone.querySelectorAll('th:last-child, td:last-child');
    actionCells.forEach(cell => cell.remove());
    
    // Style the clone for better image quality
    clone.style.backgroundColor = 'white';
    clone.style.padding = '20px';
    clone.style.fontFamily = 'Arial, sans-serif';
    clone.style.position = 'absolute';
    clone.style.left = '-9999px';
    clone.style.top = '-9999px';
    clone.style.width = '800px';
    
    // Add clone to document temporarily
    document.body.appendChild(clone);
    
    // Capture the image
    html2canvas(clone, {
        backgroundColor: '#ffffff',
        scale: 2,
        useCORS: true,
        allowTaint: true
    }).then(canvas => {
        // Create download link
        const link = document.createElement('a');
        link.download = 'my-custom-schedule.png';
        link.href = canvas.toDataURL('image/png');
        
        // Trigger download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Clean up
        document.body.removeChild(clone);
        
        // Restore button
        downloadBtn.innerHTML = originalText;
        downloadBtn.disabled = false;
        
    }).catch(error => {
        console.error('Error generating image:', error);
        alert('Error generating image. Please try again.');
        
        // Clean up
        document.body.removeChild(clone);
        
        // Restore button
        downloadBtn.innerHTML = originalText;
        downloadBtn.disabled = false;
    });
}

// Clear section selection for custom schedule
function clearSectionSelection() {
    const sectionSelect = document.getElementById('section-select-custom');
    const addButton = document.getElementById('add-to-schedule-btn');
    
    sectionSelect.innerHTML = '<option value="">First select a subject...</option>';
    sectionSelect.disabled = true;
    addButton.disabled = true;
    $('#section-select-custom').trigger('change');
}
