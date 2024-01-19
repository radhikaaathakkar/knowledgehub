document.addEventListener("DOMContentLoaded", function () {
    // Function to populate dropdowns with unique values
    function populateDropdown(elementId, property, values) {
        const dropdown = document.getElementById(elementId);

        values.forEach(value => {
            const option = document.createElement("option");
            option.value = value;
            option.text = value;
            dropdown.add(option);
        });
    }

    // Function to filter data based on selected filters
    function filterData(data) {
        const courseFilter = document.getElementById("course-filter").value;
        const subjectFilter = document.getElementById("subject-filter").value;
        const semesterFilter = document.getElementById("semester-filter").value;

        const filteredData = data.filter(item =>
            (!courseFilter || item.course === courseFilter) &&
            (!subjectFilter || item.subject === subjectFilter) &&
            (!semesterFilter || item.semester === semesterFilter)
        );

        displayMaterials(filteredData);
    }

    // Function to display study materials
    function displayMaterials(materials) {
        const materialsContainer = document.getElementById("study-materials");
        materialsContainer.innerHTML = "";

        materials.forEach(item => {
            const card = document.createElement("div");
            card.classList.add("material-card");

            const title = document.createElement("h3");
            title.textContent = `${item.course} - ${item.subject} - ${item.semester}`;

            const image = document.createElement("img");
            image.src = item.image;
            image.alt = `${item.course} Image`;
            card.appendChild(image);

            const description = document.createElement("p");
            description.textContent = item.description;
            card.appendChild(description);

            const downloadButton = document.createElement("button");
            downloadButton.textContent = "Download";
            downloadButton.addEventListener("click", () => window.location.href = item.material);

            const viewButton = document.createElement("button");
            viewButton.textContent = "View";
            viewButton.addEventListener("click", () => window.open(item.material, "_blank"));

            card.appendChild(title);
            card.appendChild(downloadButton);
            card.appendChild(viewButton);

            materialsContainer.appendChild(card);
        });
    }

    // Fetch JSON data from external file
    fetch('/static/study_materials.json')
        .then(response => response.json())
        .then(data => {
            // Populate dropdowns initially
            populateDropdown("course-filter", "course", [...new Set(data.map(item => item.course))]);
            populateDropdown("subject-filter", "subject", [...new Set(data.map(item => item.subject))]);
            populateDropdown("semester-filter", "semester", [...new Set(data.map(item => item.semester))]);

            // Event listeners for filter changes
            document.getElementById("course-filter").addEventListener("change", () => filterData(data));
            document.getElementById("subject-filter").addEventListener("change", () => filterData(data));
            document.getElementById("semester-filter").addEventListener("change", () => filterData(data));

            // Display all materials initially
            displayMaterials(data);
        })
        .catch(error => console.error('Error fetching JSON:', error));
});
