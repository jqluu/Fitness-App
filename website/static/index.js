
// weight_tracker delete weight
function deleteWeight(weightId) {
    fetch("/delete-weight", {
      method: "POST",
      body: JSON.stringify({ weightId: weightId }),
    }).then((_res) => {
      window.location.href = "/weighttracker";
    });
  }



// workout_log dynamic form
function showFieldsBasedOnSelection() {
  var workoutType = document.getElementById("workout-type").value;
  var exerciseFields = document.getElementById("exercise-fields");

  // Hide all exercise fields
  exerciseFields.style.display = "none";
  

  // Show exercise fields based on the selected workout type
  switch (workoutType) {
    case "upperbody":
      exerciseFields.style.display = "block";
      break;
    case "lowerbody":
      exerciseFields.style.display = "block";
      break;
    case "cardio":
      exerciseFields.style.display = "block";
      break;  
    case "custom":
      exerciseFields.style.display = "block";
      break;
  }

}



