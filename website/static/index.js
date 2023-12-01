// javascript functions

// weightTracker scroll from bottom
document.addEventListener("DOMContentLoaded", function() {
  const weightTracker = document.getElementById("weightTracker");
  weightTracker.scrollTop = weightTracker.scrollHeight;
});

// confirm delete weight
function confirmDeleteWeight(weightId) {
  var confirmed = window.confirm('Are you sure you want to delete this weight?');
  if (confirmed) {
      // Call the delete function if user confirms
      deleteWeight(weightId);
  } else {
      // Do nothing or handle cancellation
  }
}

// weight_tracker delete weight
function deleteWeight(weightId) {
  fetch("/delete-weight", {
    method: "POST",
    body: JSON.stringify({ weightId: weightId }),
  }).then((_res) => {
    window.location.href = "/weighttracker";
  });
}


// confirm delete
function confirmDeleteWorkout(workoutId) {
  var confirmed = window.confirm('Are you sure you want to delete this workout?');
  if (confirmed) {
      // Call the delete function if user confirms
      deleteWorkout(workoutId);
  } else {
      // Do nothing or handle cancellation
  }
}

  // workout log delete weight
function deleteWorkout(workoutId) {
  fetch("/delete-workout", {
    method: "POST",
    body: JSON.stringify({ workoutId: workoutId }),
  }).then((_res) => {
    window.location.href = "/workoutlog";
  });
}

// weight_tracker delete weight
function toggleFavorite(workoutId) {
  fetch("/toggle-favorite", {
    method: "POST",
    body: JSON.stringify({ workoutId: workoutId }),
  }).then((_res) => {
    window.location.href = "/workoutlog";
  });
}

function redirectToWeightTracker() {
  // Redirect to the specified URL
  window.location.href = "/weighttracker";
}

function redirectToWorkoutLog() {
  // Redirect to the specified URL
  window.location.href = "/workoutlog";
}

function redirectToAnalytics() {
  window.location.href = "/analytics";
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
    const addCardioButton = document.getElementById('addCardioButton');
    const exerciseRows = document.getElementById('exerciseRows');
    const form = document.querySelector('#myModal form');

    // adding exercises
    addButton.addEventListener('click', function() {
        const exerciseRow = document.createElement('div');
        exerciseRow.classList.add('exerciseRow');

        exerciseRow.innerHTML = `
        <div class="exerciseFields">
            <input type="text" name="exercise_${exerciseId}_name" placeholder="Enter exercise name (weight training)" pattern="[A-Za-z0-9 ]+" required>
            <input type="number" name="exercise_${exerciseId}_weight" placeholder="Enter weight" pattern="[1-9][0-9]*" required>
            <input type="number" name="exercise_${exerciseId}_sets" placeholder="Enter number of sets" pattern="[1-9][0-9]*" required>
            <input type="number" name="exercise_${exerciseId}_reps" placeholder="Enter number of reps" pattern="[1-9][0-9]*" required>
            <button type="button" class="removeButton">X</button>
        </div>
        `;

        exerciseRows.appendChild(exerciseRow);
        exerciseId++; // Increment ID for the next exercise
    });

    addCardioButton.addEventListener('click', function() {
      const exerciseRow = document.createElement('div');
      exerciseRow.classList.add('exerciseRow');

      exerciseRow.innerHTML = `
      <div class="exerciseFields">
          <input type="text" name="exercise_${exerciseId}_name" placeholder="Enter exercise name (cardio)" required>
          <input type="number" name="exercise_${exerciseId}_sets" placeholder="Enter number of sets" required>
          <input type="number" name="exercise_${exerciseId}_reps" placeholder="Enter duration(mins)" required>
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
  
      const exerciseData = [];
      const exerciseRows = document.querySelectorAll('.exerciseRow');
  
      exerciseRows.forEach(row => {
        const exercise = {
          name: row.querySelector('input[name^="exercise_"][name$="_name"]').value,
          sets: row.querySelector('input[name^="exercise_"][name$="_sets"]').value,
          reps: row.querySelector('input[name^="exercise_"][name$="_reps"]').value
        };

        const weightInput = row.querySelector('input[name^="exercise_"][name$="_weight"]');
        if (weightInput && weightInput.value !== '') {
            exercise.weight = weightInput.value;
            exercise.type = "weightTraining";
        } else {
            exercise.type = "cardio";
        }
  
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
      
      setTimeout(function() {
        window.location.href = '/workoutlog';
      }, 100);
  });

});


