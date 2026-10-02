document.addEventListener('DOMContentLoaded', function() {
    // 1. Teacher Child toggle in Registration Form
    const isTeacherCheckbox = document.getElementById('isTeacherCheckbox');
    const teacherSelectContainer = document.getElementById('teacherSelectContainer');
    
    if (isTeacherCheckbox && teacherSelectContainer) {
        function toggleTeacherField() {
            if (isTeacherCheckbox.checked) {
                teacherSelectContainer.style.display = 'block';
            } else {
                teacherSelectContainer.style.display = 'none';
            }
        }
        isTeacherCheckbox.addEventListener('change', toggleTeacherField);
        toggleTeacherField(); // run once on load
    }

    // 2. Mark All Present button in Attendance View
    const markAllPresentBtn = document.getElementById('markAllPresentBtn');
    if (markAllPresentBtn) {
        markAllPresentBtn.addEventListener('click', function() {
            const presentRadios = document.querySelectorAll('input[type="radio"][value="PRESENT"]');
            presentRadios.forEach(radio => {
                radio.checked = true;
                // trigger visual change
                updateToggleStyles(radio);
            });
        });
    }

    // 3. Radio button styling sync
    function updateToggleStyles(radio) {
        const group = radio.closest('.attendance-toggle-group');
        if (group) {
            group.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
            const label = group.querySelector(`label[for="${radio.id}"]`);
            if (label) label.classList.add('active');
        }
    }

    const attendanceRadios = document.querySelectorAll('.attendance-toggle-group input[type="radio"]');
    attendanceRadios.forEach(radio => {
        if (radio.checked) {
            updateToggleStyles(radio);
        }
        radio.addEventListener('change', function() {
            updateToggleStyles(this);
        });
    });
});
