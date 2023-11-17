// javascript functions


// weight_tracker delete weight
function deleteWeight(weightId) {
    fetch("/delete-weight", {
      method: "POST",
      body: JSON.stringify({ weightId: weightId }),
    }).then((_res) => {
      window.location.href = "/weighttracker";
    });
  }


// Get references to the modal and buttons
const modal = document.getElementById("myModal");
const openModalButton = document.getElementById("openModalButton");
const closeModalButton = document.getElementById("closeModalButton");

// Event listener to open the modal
openModalButton.addEventListener("click", function() {
    modal.style.display = "block";
});

// Event listener to close the modal
closeModalButton.addEventListener("click", function() {
    modal.style.display = "none";
});

// Close the modal if the user clicks outside of it
window.addEventListener("click", function(event) {
    if (event.target === modal) {
        modal.style.display = "none";
    }
});


// creating, adding, displaying exercises and workouts

let exerciseId = 0; // To give each exercise input field a unique ID

document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('addButton');
    const exerciseRows = document.getElementById('exerciseRows');
    const form = document.querySelector('#myModal form');

    // adding exercises
    addButton.addEventListener('click', function() {
        const exerciseRow = document.createElement('div');
        exerciseRow.classList.add('exerciseRow');

        exerciseRow.innerHTML = `
        <div class="exerciseFields">
            <input type="text" name="exercise_${exerciseId}_name" placeholder="Enter exercise name">
            <input type="number" name="exercise_${exerciseId}_sets" placeholder="Enter number of sets">
            <input type="number" name="exercise_${exerciseId}_reps" placeholder="Enter number of reps">
            <button type="button" class="removeButton">X</button>
        </div>
        `;

        exerciseRows.appendChild(exerciseRow);
        exerciseId++; // Increment ID for the next exercise
    });

    exerciseRows.addEventListener('click', function(e) {
        if (e.target.classList.contains('removeButton')) {
            e.target.parentNode.remove();
        }
    });

    // submitting workout data
    function sendWorkoutDataToFlask() {
      const title = document.getElementById('name').value;
      const date = document.getElementById('selected-date').value;
  
      const exerciseData = [
        // sample data
        // { name: 'Push-ups', sets: 3, reps: 12 },
        // { name: 'Squats', sets: 4, reps: 10 },
        // { name: 'Plank', sets: 3, reps: 30 },
        // Add more exercise objects as needed
      ];
      const exerciseRows = document.querySelectorAll('.exerciseRow');
  
      exerciseRows.forEach(row => {
        const exercise = {
          name: row.querySelector('input[name^="exercise_"][name$="_name"]').value,
          sets: row.querySelector('input[name^="exercise_"][name$="_sets"]').value,
          reps: row.querySelector('input[name^="exercise_"][name$="_reps"]').value
        };
  
        exerciseData.push(exercise);
      });
  
      // Send workoutData to Flask backend using AJAX (POST request)
      fetch('/workoutlog', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' // Set the correct content type
        },
        body: JSON.stringify({
            title: title,
            date: date,
            exercises: exerciseData
        })
      })
      .then(response => response.text())
      .then(data => {
          console.log(data);
      })
      .catch(error => {
          console.error('Error:', error);
      });
    }
  
    form.addEventListener('submit', function(event) {
      event.preventDefault();
      sendWorkoutDataToFlask();
      window.location.href = '/workoutlog';
  });

});

